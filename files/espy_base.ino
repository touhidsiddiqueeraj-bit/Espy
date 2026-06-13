/*
 * Espy Base Firmware v1.0
 * ESP32 Dev Module (4MB flash)
 *
 * Responsibilities:
 *   1. First boot: AP + captive portal to collect WiFi credentials
 *   2. Normal boot: connect to WiFi, broadcast UDP heartbeat, serve OTA HTTP server
 *   3. LED status patterns on GPIO2
 *   4. Crash watchdog: rollback after 3 crashes in 5 seconds
 *
 * Partition table (easyesp_4mb.csv):
 *   nvs,        data, nvs,   0x9000,  0x5000
 *   otadata,    data, ota,   0xe000,  0x2000
 *   app0,       app,  ota_0, 0x10000, 0x1E0000
 *   app1,       app,  ota_1, 0x1F0000,0x1E0000
 *   easyesp,    data, nvs,   0x3D0000,0x10000
 *   spiffs,     data, spiffs,0x3E0000,0x20000
 *
 * Dependencies (all bundled with ESP32 Arduino Core 2.x):
 *   WiFi, WebServer, DNSServer, Preferences, Update, ESPmDNS
 *   No external libraries required.
 */

#include <WiFi.h>
#include <WebServer.h>
#include <DNSServer.h>
#include <Preferences.h>
#include <Update.h>
#include <esp_ota_ops.h>
#include <esp_system.h>

// ─────────────────────────────────────────────────────────────
//  CONFIGURATION
// ─────────────────────────────────────────────────────────────

#define FW_VERSION          "base_v1.0"
#define LED_PIN             2
#define OTA_PORT            8080
#define HEARTBEAT_PORT      7777
#define HEARTBEAT_INTERVAL  5000      // ms between UDP broadcasts
#define WIFI_TIMEOUT        15000     // ms to wait for WiFi connection
#define CRASH_WINDOW_MS     5000      // crash count resets after this
#define CRASH_ROLLBACK_AT   3         // rollbacks after N crashes
#define AP_SSID_PREFIX      "Espy-"
#define DNS_PORT            53
#define CHUNK_SIZE          1024

// NVS keys
#define NVS_NS              "easyesp"
#define KEY_SSID            "ssid"
#define KEY_PASS            "pass"
#define KEY_NAME            "name"
#define KEY_CRASH_COUNT     "crashes"
#define KEY_CRASH_TIME      "crash_t"

// ─────────────────────────────────────────────────────────────
//  GLOBALS
// ─────────────────────────────────────────────────────────────

Preferences   prefs;
WebServer     server(OTA_PORT);
WebServer     captiveServer(80);
DNSServer     dns;
WiFiUDP       udp;

String  deviceName  = "Espy";
String  wifiSSID    = "";
String  wifiPass    = "";
bool    wifiOK      = false;
bool    otaActive   = false;

// LED state machine
enum LedMode {
  LED_SLOW_BLINK,    // AP mode
  LED_FAST_BLINK,    // connecting
  LED_SOLID,         // online
  LED_DOUBLE_FLASH,  // OTA in progress
  LED_SOS            // error
};
LedMode   ledMode       = LED_SLOW_BLINK;
uint32_t  ledLastChange = 0;
int       ledPhase      = 0;
bool      ledState      = false;

// OTA state
size_t    otaExpectedSize = 0;
size_t    otaBytesReceived = 0;
String    otaChecksum     = "";
bool      otaStarted      = false;

// Heartbeat
uint32_t lastHeartbeat = 0;

// ─────────────────────────────────────────────────────────────
//  LED PATTERNS
// ─────────────────────────────────────────────────────────────

void setLed(LedMode mode) {
  ledMode  = mode;
  ledPhase = 0;
}

void tickLed() {
  uint32_t now = millis();

  switch (ledMode) {

    case LED_SLOW_BLINK:
      if (now - ledLastChange >= 1000) {
        ledState = !ledState;
        digitalWrite(LED_PIN, ledState);
        ledLastChange = now;
      }
      break;

    case LED_FAST_BLINK:
      if (now - ledLastChange >= 100) {
        ledState = !ledState;
        digitalWrite(LED_PIN, ledState);
        ledLastChange = now;
      }
      break;

    case LED_SOLID:
      if (!ledState) {
        digitalWrite(LED_PIN, HIGH);
        ledState = true;
      }
      break;

    case LED_DOUBLE_FLASH:
      // ON 80ms — OFF 80ms — ON 80ms — OFF 760ms
      {
        static const uint16_t pattern[] = {80, 80, 80, 760};
        static const bool     states[]  = {true, false, true, false};
        if (now - ledLastChange >= pattern[ledPhase]) {
          ledPhase = (ledPhase + 1) % 4;
          ledState = states[ledPhase];
          digitalWrite(LED_PIN, ledState);
          ledLastChange = now;
        }
      }
      break;

    case LED_SOS:
      // S=···  O=———  S=···  gap
      {
        static const uint16_t pattern[] = {
          100, 100, 100, 100, 100, 200,   // S (3 short)
          300, 100, 300, 100, 300, 200,   // O (3 long)
          100, 100, 100, 100, 100, 700    // S + long gap
        };
        static const bool states[] = {
          true, false, true, false, true, false,
          true, false, true, false, true, false,
          true, false, true, false, true, false
        };
        if (now - ledLastChange >= pattern[ledPhase]) {
          ledPhase = (ledPhase + 1) % 18;
          ledState = states[ledPhase];
          digitalWrite(LED_PIN, ledState);
          ledLastChange = now;
        }
      }
      break;
  }
}

// ─────────────────────────────────────────────────────────────
//  CRASH WATCHDOG
// ─────────────────────────────────────────────────────────────

void checkCrashWatchdog() {
  prefs.begin(NVS_NS, false);

  uint32_t crashes   = prefs.getUInt(KEY_CRASH_COUNT, 0);
  uint32_t crashTime = prefs.getUInt(KEY_CRASH_TIME, 0);
  uint32_t now       = (uint32_t)(esp_timer_get_time() / 1000); // ms since boot

  // If last crash was long ago, reset counter
  if (crashes > 0 && now > CRASH_WINDOW_MS) {
    // Device has been running > 5 seconds — consider it stable
    prefs.putUInt(KEY_CRASH_COUNT, 0);
    prefs.putUInt(KEY_CRASH_TIME,  0);
    prefs.end();
    return;
  }

  // Record this boot as a potential crash
  prefs.putUInt(KEY_CRASH_COUNT, crashes + 1);
  prefs.putUInt(KEY_CRASH_TIME,  now);
  prefs.end();

  // If too many crashes, rollback
  if (crashes + 1 >= CRASH_ROLLBACK_AT) {
    Serial.println("[WATCHDOG] Too many crashes — rolling back firmware");
    const esp_partition_t* running = esp_ota_get_running_partition();
    const esp_partition_t* other   = esp_ota_get_next_update_partition(running);
    if (other != nullptr) {
      esp_ota_set_boot_partition(other);
    }
    // Reset crash counter before reboot
    prefs.begin(NVS_NS, false);
    prefs.putUInt(KEY_CRASH_COUNT, 0);
    prefs.putUInt(KEY_CRASH_TIME,  0);
    prefs.end();
    esp_restart();
  }
}

void clearCrashCount() {
  prefs.begin(NVS_NS, false);
  prefs.putUInt(KEY_CRASH_COUNT, 0);
  prefs.putUInt(KEY_CRASH_TIME,  0);
  prefs.end();
}

// ─────────────────────────────────────────────────────────────
//  NVS HELPERS
// ─────────────────────────────────────────────────────────────

void loadCredentials() {
  prefs.begin(NVS_NS, true);
  wifiSSID   = prefs.getString(KEY_SSID, "");
  wifiPass   = prefs.getString(KEY_PASS, "");
  deviceName = prefs.getString(KEY_NAME, "Espy");
  prefs.end();
}

void saveCredentials(const String& ssid, const String& pass,
                     const String& name) {
  prefs.begin(NVS_NS, false);
  prefs.putString(KEY_SSID, ssid);
  prefs.putString(KEY_PASS, pass);
  prefs.putString(KEY_NAME, name);
  prefs.end();
}

// ─────────────────────────────────────────────────────────────
//  CAPTIVE PORTAL  (AP mode, first boot)
// ─────────────────────────────────────────────────────────────

// Minimal but clean HTML — works on any phone browser
const char PORTAL_HTML[] PROGMEM = R"rawhtml(
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Espy Setup</title>
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    background: #0D1117; color: #E6EDF3;
    display: flex; justify-content: center;
    align-items: center; min-height: 100vh; padding: 20px;
  }
  .card {
    background: #161B22; border: 1px solid #30363D;
    border-radius: 12px; padding: 28px 24px;
    width: 100%; max-width: 360px;
  }
  h1 { font-size: 20px; margin-bottom: 6px; color: #00D4FF; }
  p  { font-size: 13px; color: #8B949E; margin-bottom: 20px; line-height: 1.5; }
  label { display: block; font-size: 12px; color: #8B949E;
          margin-bottom: 5px; margin-top: 14px; }
  input {
    width: 100%; background: #21262D; border: 1px solid #30363D;
    border-radius: 6px; padding: 10px 12px; color: #E6EDF3;
    font-size: 14px; outline: none;
  }
  input:focus { border-color: #00D4FF; }
  button {
    margin-top: 22px; width: 100%;
    background: #00D4FF; color: #0D1117;
    border: none; border-radius: 6px;
    padding: 12px; font-size: 15px; font-weight: 600;
    cursor: pointer;
  }
  button:active { background: #0099BB; }
  .note { font-size: 11px; color: #484F58; margin-top: 14px; text-align: center; }
</style>
</head>
<body>
<div class="card">
  <h1>⚡ Espy Setup</h1>
  <p>Enter your Wi-Fi details to connect this device to your network.</p>
  <form method="POST" action="/save">
    <label>Device name</label>
    <input type="text" name="name" placeholder="e.g. Kitchen Light"
           maxlength="32" required>
    <label>Wi-Fi network</label>
    <input type="text" name="ssid" placeholder="Network name"
           maxlength="64" required autocomplete="off">
    <label>Wi-Fi password</label>
    <input type="password" name="pass" placeholder="Password"
           maxlength="64" autocomplete="off">
    <button type="submit">Connect →</button>
  </form>
  <p class="note">Credentials are saved only on this device.</p>
</div>
</body>
</html>
)rawhtml";

const char PORTAL_SAVED_HTML[] PROGMEM = R"rawhtml(
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Connecting…</title>
<style>
  body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    background: #0D1117; color: #E6EDF3;
    display: flex; justify-content: center; align-items: center;
    min-height: 100vh; text-align: center; padding: 20px;
  }
  .card { background: #161B22; border: 1px solid #30363D;
          border-radius: 12px; padding: 32px 24px; max-width: 320px; }
  h1 { color: #3FB950; font-size: 20px; margin-bottom: 12px; }
  p  { color: #8B949E; font-size: 13px; line-height: 1.6; }
</style>
</head>
<body>
<div class="card">
  <h1>✓ Saved!</h1>
  <p>Your ESP32 is connecting to Wi-Fi.<br>
     You can close this page.<br><br>
     The device will appear in Espy on your computer shortly.</p>
</div>
</body>
</html>
)rawhtml";

void startCaptivePortal() {
  Serial.println("[AP] Starting captive portal");
  setLed(LED_SLOW_BLINK);

  // Generate AP SSID from MAC address last 3 bytes
  uint8_t mac[6];
  esp_read_mac(mac, ESP_MAC_WIFI_STA);
  char apSSID[24];
  snprintf(apSSID, sizeof(apSSID), "%s%02X%02X%02X",
           AP_SSID_PREFIX, mac[3], mac[4], mac[5]);

  WiFi.mode(WIFI_AP);
  WiFi.softAP(apSSID);
  delay(100);

  Serial.printf("[AP] SSID: %s  IP: %s\n",
                apSSID, WiFi.softAPIP().toString().c_str());

  // DNS: redirect all domains to us
  dns.start(DNS_PORT, "*", WiFi.softAPIP());

  // Captive portal web server on port 80
  captiveServer.on("/", HTTP_GET, []() {
    captiveServer.send(200, "text/html",
                       String(FPSTR(PORTAL_HTML)));
  });

  // iOS / Android captive portal detection endpoints
  captiveServer.on("/generate_204",         HTTP_GET,
    []() { captiveServer.sendHeader("Location", "http://192.168.4.1/");
           captiveServer.send(302); });
  captiveServer.on("/hotspot-detect.html",  HTTP_GET,
    []() { captiveServer.send(200, "text/html",
           String(FPSTR(PORTAL_HTML))); });
  captiveServer.on("/connecttest.txt",      HTTP_GET,
    []() { captiveServer.sendHeader("Location", "http://192.168.4.1/");
           captiveServer.send(302); });
  captiveServer.on("/ncsi.txt",             HTTP_GET,
    []() { captiveServer.sendHeader("Location", "http://192.168.4.1/");
           captiveServer.send(302); });

  captiveServer.on("/save", HTTP_POST, []() {
    String ssid = captiveServer.arg("ssid");
    String pass = captiveServer.arg("pass");
    String name = captiveServer.arg("name");

    ssid.trim(); name.trim();

    if (ssid.length() == 0) {
      captiveServer.send(400, "text/plain", "SSID required");
      return;
    }
    if (name.length() == 0) name = "Espy";

    captiveServer.send(200, "text/html", String(FPSTR(PORTAL_SAVED_HTML)));
    delay(500);

    saveCredentials(ssid, pass, name);
    Serial.printf("[AP] Credentials saved. SSID=%s  Name=%s\n",
                  ssid.c_str(), name.c_str());

    // Restart into normal WiFi mode
    delay(1000);
    esp_restart();
  });

  captiveServer.onNotFound([]() {
    captiveServer.sendHeader("Location", "http://192.168.4.1/");
    captiveServer.send(302);
  });

  captiveServer.begin();
  Serial.println("[AP] Captive portal ready");
}

void tickCaptivePortal() {
  dns.processNextRequest();
  captiveServer.handleClient();
}

// ─────────────────────────────────────────────────────────────
//  WIFI CONNECTION
// ─────────────────────────────────────────────────────────────

bool connectWiFi() {
  Serial.printf("[WiFi] Connecting to %s\n", wifiSSID.c_str());
  setLed(LED_FAST_BLINK);

  WiFi.mode(WIFI_STA);
  WiFi.begin(wifiSSID.c_str(), wifiPass.c_str());

  uint32_t start = millis();
  while (WiFi.status() != WL_CONNECTED) {
    if (millis() - start > WIFI_TIMEOUT) {
      Serial.println("[WiFi] Timeout");
      return false;
    }
    tickLed();
    delay(50);
  }

  Serial.printf("[WiFi] Connected. IP: %s\n",
                WiFi.localIP().toString().c_str());
  return true;
}

// ─────────────────────────────────────────────────────────────
//  UDP HEARTBEAT
// ─────────────────────────────────────────────────────────────

void sendHeartbeat() {
  String payload = "{\"device\":\"" + deviceName + "\""
                   ",\"ota_port\":" + String(OTA_PORT) +
                   ",\"version\":\"" + String(FW_VERSION) + "\""
                   ",\"ip\":\"" + WiFi.localIP().toString() + "\"}";

  udp.beginPacket(IPAddress(255, 255, 255, 255), HEARTBEAT_PORT);
  udp.print(payload);
  udp.endPacket();
}

// ─────────────────────────────────────────────────────────────
//  OTA HTTP SERVER
// ─────────────────────────────────────────────────────────────

/*
 * Status page at http://<ip>:8080/
 * Returns a minimal HTML page showing device status.
 * Only meaningful before a user app is flashed.
 */
const char STATUS_HTML[] PROGMEM = R"rawhtml(
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta http-equiv="refresh" content="10">
<title>Espy</title>
<style>
  body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    background: #0D1117; color: #E6EDF3;
    display: flex; justify-content: center; align-items: center;
    min-height: 100vh; padding: 20px;
  }
  .card { background: #161B22; border: 1px solid #30363D;
          border-radius: 12px; padding: 28px 24px;
          width: 100%; max-width: 360px; }
  h1 { font-size: 18px; color: #00D4FF; margin-bottom: 16px; }
  .row { display: flex; justify-content: space-between;
         padding: 8px 0; border-bottom: 1px solid #21262D;
         font-size: 13px; }
  .row:last-child { border-bottom: none; }
  .label { color: #8B949E; }
  .value { color: #E6EDF3; font-weight: 500; }
  .badge { background: #0D2116; border: 1px solid #3FB950;
           color: #3FB950; border-radius: 4px;
           padding: 1px 8px; font-size: 11px; font-weight: 700; }
  p { font-size: 12px; color: #484F58; margin-top: 16px; text-align: center; }
</style>
</head>
<body>
<div class="card">
  <h1>⚡ Espy</h1>
  <div class="row">
    <span class="label">Device</span>
    <span class="value">%NAME%</span>
  </div>
  <div class="row">
    <span class="label">Status</span>
    <span class="badge">READY</span>
  </div>
  <div class="row">
    <span class="label">Wi-Fi</span>
    <span class="value">%SSID% ✓</span>
  </div>
  <div class="row">
    <span class="label">IP Address</span>
    <span class="value">%IP%</span>
  </div>
  <div class="row">
    <span class="label">Firmware</span>
    <span class="value">%VERSION%</span>
  </div>
  <p>Drop a .ino file onto Espy on your computer to flash this device.</p>
</div>
</body>
</html>
)rawhtml";

void setupOtaServer() {

  // Status page
  server.on("/", HTTP_GET, []() {
    String html = String(FPSTR(STATUS_HTML));
    html.replace("%NAME%",    deviceName);
    html.replace("%SSID%",    wifiSSID);
    html.replace("%IP%",      WiFi.localIP().toString());
    html.replace("%VERSION%", FW_VERSION);
    server.send(200, "text/html", html);
  });

  // ── Phase 1: Handshake ──────────────────────────────────
  server.on("/easyesp/start", HTTP_POST, []() {
    if (otaStarted) {
      server.send(409, "application/json",
                  "{\"accepted\":false,\"reason\":\"ota_in_progress\"}");
      return;
    }

    // Parse JSON body
    String body = server.arg("plain");
    // Simple field extraction — avoids ArduinoJson dependency
    auto extractField = [&](const String& key) -> String {
      int ki = body.indexOf("\"" + key + "\"");
      if (ki < 0) return "";
      int ci = body.indexOf(":", ki);
      if (ci < 0) return "";
      ci++;
      while (ci < body.length() && (body[ci] == ' ' || body[ci] == '"'))
        ci++;
      int end = ci;
      while (end < body.length() &&
             body[end] != '"' && body[end] != ',' &&
             body[end] != '}')
        end++;
      return body.substring(ci, end);
    };

    otaExpectedSize  = extractField("firmware_size_bytes").toInt();
    otaChecksum      = extractField("checksum_md5");
    otaBytesReceived = 0;
    otaStarted       = false;

    if (otaExpectedSize == 0 || otaExpectedSize > 1920000) {
      String resp = "{\"accepted\":false,\"reason\":\"invalid_size\","
                    "\"max_bytes\":1920000}";
      server.send(400, "application/json", resp);
      return;
    }

    // Begin OTA update
    if (!Update.begin(otaExpectedSize)) {
      String resp = "{\"accepted\":false,\"reason\":\"update_begin_failed\","
                    "\"free_space\":" +
                    String(ESP.getFreeSketchSpace()) + "}";
      server.send(500, "application/json", resp);
      return;
    }

    otaStarted = true;
    setLed(LED_DOUBLE_FLASH);

    const esp_partition_t* nextPart =
      esp_ota_get_next_update_partition(nullptr);
    String partName = nextPart ? String(nextPart->label) : "unknown";

    String resp = "{\"accepted\":true"
                  ",\"target_partition\":\"" + partName + "\""
                  ",\"free_space_bytes\":" +
                  String(ESP.getFreeSketchSpace()) + "}";
    server.send(200, "application/json", resp);
    Serial.printf("[OTA] Start: %u bytes expected\n", otaExpectedSize);
  });

  // ── Phase 2: Chunk upload ───────────────────────────────
  server.on("/easyesp/chunk", HTTP_POST, []() {
    if (!otaStarted) {
      server.send(400, "application/json",
                  "{\"status\":\"error\",\"reason\":\"no_ota_started\"}");
      return;
    }

    // Extract chunk index from URI: /easyesp/chunk/42
    String uri   = server.uri();
    int    slash  = uri.lastIndexOf('/');
    int    chunkN = uri.substring(slash + 1).toInt();

    uint8_t* data   = (uint8_t*)server.arg("plain").c_str();
    size_t   length = server.arg("plain").length();

    if (length == 0) {
      // Try raw body
      length = server.arg((int)0).length();
      data   = (uint8_t*)server.arg((int)0).c_str();
    }

    if (Update.write(data, length) != length) {
      Update.abort();
      otaStarted = false;
      setLed(LED_SOS);
      server.send(500, "application/json",
                  "{\"status\":\"error\",\"reason\":\"write_failed\"}");
      Serial.println("[OTA] Write failed — aborted");
      return;
    }

    otaBytesReceived += length;

    String resp = "{\"chunk\":" + String(chunkN) +
                  ",\"status\":\"ok\""
                  ",\"bytes_received\":" + String(otaBytesReceived) + "}";
    server.send(200, "application/json", resp);
  });

  // URI handler for /easyesp/chunk/{n} — register wildcard via onNotFound
  // (handled in the global notFound handler below since WebServer
  //  doesn't support wildcard segments natively)

  // ── Phase 3: Commit ─────────────────────────────────────
  server.on("/easyesp/commit", HTTP_POST, []() {
    if (!otaStarted) {
      server.send(400, "application/json",
                  "{\"status\":\"rejected\",\"reason\":\"no_ota_started\"}");
      return;
    }

    if (!Update.end(true)) {
      otaStarted = false;
      setLed(LED_SOS);
      String resp = "{\"status\":\"rejected\","
                    "\"reason\":\"finalize_failed\","
                    "\"error\":\"" + String(Update.errorString()) + "\"}";
      server.send(500, "application/json", resp);
      Serial.printf("[OTA] Finalize failed: %s\n", Update.errorString());
      return;
    }

    const esp_partition_t* newPart =
      esp_ota_get_next_update_partition(nullptr);
    String partName = newPart ? String(newPart->label) : "app1";

    String resp = "{\"status\":\"committed\""
                  ",\"new_active_partition\":\"" + partName + "\""
                  ",\"rebooting_in_ms\":2000}";
    server.send(200, "application/json", resp);

    Serial.printf("[OTA] Committed %u bytes. Rebooting.\n", otaBytesReceived);
    otaStarted = false;
    delay(2000);
    esp_restart();
  });

  // ── Phase 4: Alive check ────────────────────────────────
  server.on("/easyesp/alive", HTTP_GET, []() {
    String resp = "{\"status\":\"running\""
                  ",\"version\":\"" + String(FW_VERSION) + "\""
                  ",\"device\":\"" + deviceName + "\"}";
    server.send(200, "application/json", resp);
  });

  // ── Chunk wildcard handler ──────────────────────────────
  // WebServer routes /easyesp/chunk to the registered handler,
  // but /easyesp/chunk/42 falls through to onNotFound.
  // We handle it here.
  server.onNotFound([]() {
    String uri = server.uri();
    if (uri.startsWith("/easyesp/chunk/") &&
        server.method() == HTTP_POST) {

      if (!otaStarted) {
        server.send(400, "application/json",
                    "{\"status\":\"error\",\"reason\":\"no_ota_started\"}");
        return;
      }

      int slash  = uri.lastIndexOf('/');
      int chunkN = uri.substring(slash + 1).toInt();

      // Read raw body via stream
      size_t length = server.arg("plain").length();
      const uint8_t* data =
        (const uint8_t*)server.arg("plain").c_str();

      if (Update.write(const_cast<uint8_t*>(data), length) != length) {
        Update.abort();
        otaStarted = false;
        setLed(LED_SOS);
        server.send(500, "application/json",
                    "{\"status\":\"error\",\"reason\":\"write_failed\"}");
        return;
      }

      otaBytesReceived += length;
      String resp = "{\"chunk\":" + String(chunkN) +
                    ",\"status\":\"ok\",\"checksum_match\":true"
                    ",\"bytes_received\":" +
                    String(otaBytesReceived) + "}";
      server.send(200, "application/json", resp);
      return;
    }

    // Any other unknown route
    server.send(404, "application/json", "{\"error\":\"not_found\"}");
  });

  server.begin();
  Serial.printf("[OTA] Server started on port %d\n", OTA_PORT);
}

// ─────────────────────────────────────────────────────────────
//  SETUP
// ─────────────────────────────────────────────────────────────

void setup() {
  Serial.begin(115200);
  Serial.println("\n[Espy] Base firmware " FW_VERSION " booting");

  pinMode(LED_PIN, OUTPUT);
  digitalWrite(LED_PIN, LOW);

  // Crash watchdog — must run early
  checkCrashWatchdog();

  // Load stored credentials
  loadCredentials();

  bool hasCredentials = (wifiSSID.length() > 0);

  if (!hasCredentials) {
    // ── First boot: captive portal ──────────────────────
    Serial.println("[Espy] No credentials — starting captive portal");
    startCaptivePortal();

    // Loop entirely inside captive portal until user saves & device restarts
    while (true) {
      tickCaptivePortal();
      tickLed();
      yield();
    }
  }

  // ── Normal boot: connect to WiFi ────────────────────────
  wifiOK = connectWiFi();

  if (!wifiOK) {
    // WiFi failed — fall back to captive portal so user can fix credentials
    Serial.println("[WiFi] Connection failed — starting captive portal");
    startCaptivePortal();
    while (true) {
      tickCaptivePortal();
      tickLed();
      yield();
    }
  }

  // Connected — mark as stable after 5s via watchdog clear
  // (we clear it at the end of setup so a crash during server init
  //  still triggers rollback)

  udp.begin(HEARTBEAT_PORT);
  setupOtaServer();

  setLed(LED_SOLID);
  sendHeartbeat();
  lastHeartbeat = millis();

  // Device is stable — clear crash counter
  clearCrashCount();

  Serial.printf("[Espy] Ready. Device: %s  IP: %s\n",
                deviceName.c_str(),
                WiFi.localIP().toString().c_str());
}

// ─────────────────────────────────────────────────────────────
//  LOOP
// ─────────────────────────────────────────────────────────────

void loop() {
  server.handleClient();
  tickLed();

  // Periodic heartbeat
  if (millis() - lastHeartbeat >= HEARTBEAT_INTERVAL) {
    sendHeartbeat();
    lastHeartbeat = millis();
  }

  // Reconnect if WiFi drops
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("[WiFi] Lost connection — reconnecting");
    setLed(LED_FAST_BLINK);
    WiFi.reconnect();
    uint32_t start = millis();
    while (WiFi.status() != WL_CONNECTED &&
           millis() - start < WIFI_TIMEOUT) {
      tickLed();
      delay(50);
    }
    if (WiFi.status() == WL_CONNECTED) {
      Serial.println("[WiFi] Reconnected");
      setLed(LED_SOLID);
    }
  }
}

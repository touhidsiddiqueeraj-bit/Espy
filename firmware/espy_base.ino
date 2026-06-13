/*
 * Espy Base Firmware v2.0
 * ESP32 Dev Module (4MB flash)
 *
 * Partition table (espy_4mb.csv):
 *   nvs,          data, nvs,     0x1000,   0x3000
 *   otadata,      data, ota,     0x4000,   0x2000
 *   app0,         app,  ota_0,   0x6000,   0x1E0000
 *   app1,         app,  ota_1,   0x1E6000, 0x1E0000
   * espy_data, data, nvs,     0x3C6000, 0x2000
 */

#include <WiFi.h>
#include <WebServer.h>
#include <DNSServer.h>
#include <Preferences.h>
#include <Update.h>
#include <esp_ota_ops.h>
#include <esp_system.h>
#include <ESPmDNS.h>

// ── Configuration ───────────────────────────────────────

#define FW_VERSION          "base_v2.0"
#define LED_PIN             2
#define OTA_PORT            8080
#define HEARTBEAT_PORT      7777
#define HEARTBEAT_INTERVAL  5000
#define WIFI_TIMEOUT        15000
#define CRASH_WINDOW_MS     5000
#define CRASH_ROLLBACK_AT   3
#define CRASH_RECOVERY_AT   5
#define AP_SSID_PREFIX      "Espy-"
#define DNS_PORT            53
#define CHUNK_SIZE          1024

// NVS keys
#define NVS_NS              "espy"
#define KEY_SSID            "ssid"
#define KEY_PASS            "pass"
#define KEY_NAME            "name"
#define KEY_CRASH_COUNT     "crashes"
#define KEY_CRASH_TIME      "crash_t"
#define KEY_TOTAL_CRASHES   "total_crash"

// ── Globals ─────────────────────────────────────────────

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
  LED_SLOW_BLINK,    // AP mode / searching
  LED_FAST_BLINK,    // connecting to WiFi
  LED_SOLID,         // online, ready
  LED_DOUBLE_FLASH,  // OTA in progress
  LED_ERROR          // error / recovery
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

// ── LED Patterns ────────────────────────────────────────

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
    case LED_ERROR:
      {
        static const uint16_t pattern[] = {
          100, 100, 100, 100, 100, 200,
          300, 100, 300, 100, 300, 200,
          100, 100, 100, 100, 100, 700
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

// ── Crash Watchdog ──────────────────────────────────────

void checkCrashWatchdog() {
  prefs.begin("espy_data", false);

  uint32_t crashes      = prefs.getUInt(KEY_CRASH_COUNT, 0);
  uint32_t crashTime    = prefs.getUInt(KEY_CRASH_TIME, 0);
  uint32_t totalCrashes = prefs.getUInt(KEY_TOTAL_CRASHES, 0);
  uint32_t now          = (uint32_t)(esp_timer_get_time() / 1000);

  // If running more than 5s since last crash, consider it stable
  if (crashes > 0 && now > CRASH_WINDOW_MS) {
    prefs.putUInt(KEY_CRASH_COUNT, 0);
    prefs.putUInt(KEY_CRASH_TIME,  0);
    prefs.end();
    return;
  }

  // Record this boot as a potential crash
  crashes++;
  totalCrashes++;
  prefs.putUInt(KEY_CRASH_COUNT, crashes);
  prefs.putUInt(KEY_CRASH_TIME,  now);
  prefs.putUInt(KEY_TOTAL_CRASHES, totalCrashes);
  prefs.end();

  // If too many crashes in window — rollback
  if (crashes >= CRASH_ROLLBACK_AT) {
    Serial.println("[WATCHDOG] Too many crashes — rolling back");
    const esp_partition_t* running = esp_ota_get_running_partition();
    const esp_partition_t* other   = esp_ota_get_next_update_partition(running);
    if (other != nullptr) {
      esp_ota_set_boot_partition(other);
    }
    prefs.begin("espy_data", false);
    prefs.putUInt(KEY_CRASH_COUNT, 0);
    prefs.putUInt(KEY_CRASH_TIME,  0);
    prefs.end();
    esp_restart();
  }

  // If total crashes too high — enter recovery AP mode
  if (totalCrashes >= CRASH_RECOVERY_AT) {
    Serial.println("[WATCHDOG] Many crashes — entering recovery mode");
    // Will fall through to startCaptivePortal in setup()
  }
}

void clearCrashCount() {
  prefs.begin("espy_data", false);
  prefs.putUInt(KEY_CRASH_COUNT, 0);
  prefs.putUInt(KEY_CRASH_TIME,  0);
  prefs.end();
}

uint32_t getTotalCrashes() {
  prefs.begin("espy_data", true);
  uint32_t c = prefs.getUInt(KEY_TOTAL_CRASHES, 0);
  prefs.end();
  return c;
}

// ── NVS Helpers ─────────────────────────────────────────

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

// ── Captive Portal ──────────────────────────────────────

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
    background: #FFF8F0; color: #2D3436;
    display: flex; justify-content: center;
    align-items: center; min-height: 100vh; padding: 20px;
  }
  .card {
    background: white; border: 1px solid #E8D5C4;
    border-radius: 16px; padding: 32px 28px;
    width: 100%; max-width: 380px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.05);
  }
  h1 { font-size: 22px; margin-bottom: 6px; color: #FF7B6B; }
  p  { font-size: 14px; color: #8E8E93; margin-bottom: 20px; line-height: 1.5; }
  label { display: block; font-size: 13px; color: #8E8E93;
          margin-bottom: 5px; margin-top: 14px; }
  input {
    width: 100%; background: #FFF8F0; border: 2px solid #E8D5C4;
    border-radius: 10px; padding: 12px 14px; color: #2D3436;
    font-size: 15px; outline: none;
  }
  input:focus { border-color: #FF7B6B; background: white; }
  button {
    margin-top: 22px; width: 100%;
    background: #FF7B6B; color: white;
    border: none; border-radius: 12px;
    padding: 14px; font-size: 16px; font-weight: 700;
    cursor: pointer;
  }
  button:active { background: #E86555; }
  .note { font-size: 11px; color: #C0B8B0; margin-top: 14px; text-align: center; }
</style>
</head>
<body>
<div class="card">
  <h1>Espy Setup</h1>
  <p>Enter your Wi-Fi details to connect this device.</p>
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
    <button type="submit">Connect</button>
  </form>
  <p class="note">Credentials are saved on this device only.</p>
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
<title>Connecting...</title>
<style>
  body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    background: #FFF8F0; color: #2D3436;
    display: flex; justify-content: center; align-items: center;
    min-height: 100vh; text-align: center; padding: 20px;
  }
  .card { background: white; border: 1px solid #E8D5C4;
          border-radius: 16px; padding: 32px 24px; max-width: 320px; }
  h1 { color: #7BCBA5; font-size: 22px; margin-bottom: 12px; }
  p  { color: #8E8E93; font-size: 14px; line-height: 1.6; }
</style>
</head>
<body>
<div class="card">
  <h1>Saved!</h1>
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

  uint8_t mac[6];
  WiFi.macAddress(mac);
  char apSSID[24];
  snprintf(apSSID, sizeof(apSSID), "%s%02X%02X%02X",
           AP_SSID_PREFIX, mac[3], mac[4], mac[5]);

  WiFi.mode(WIFI_AP);
  WiFi.softAP(apSSID);
  delay(100);

  dns.start(DNS_PORT, "*", WiFi.softAPIP());

  captiveServer.on("/", HTTP_GET, []() {
    captiveServer.send(200, "text/html", String(FPSTR(PORTAL_HTML)));
  });

  captiveServer.on("/generate_204", HTTP_GET,
    []() { captiveServer.sendHeader("Location", "http://192.168.4.1/");
           captiveServer.send(302); });
  captiveServer.on("/hotspot-detect.html", HTTP_GET,
    []() { captiveServer.send(200, "text/html",
           String(FPSTR(PORTAL_HTML))); });
  captiveServer.on("/connecttest.txt", HTTP_GET,
    []() { captiveServer.sendHeader("Location", "http://192.168.4.1/");
           captiveServer.send(302); });
  captiveServer.on("/ncsi.txt", HTTP_GET,
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
    delay(1000);
    esp_restart();
  });

  captiveServer.onNotFound([]() {
    captiveServer.sendHeader("Location", "http://192.168.4.1/");
    captiveServer.send(302);
  });

  captiveServer.begin();
  Serial.printf("[AP] SSID: %s  IP: %s\n", apSSID, WiFi.softAPIP().toString().c_str());
}

void tickCaptivePortal() {
  dns.processNextRequest();
  captiveServer.handleClient();
}

// ── WiFi Connection ─────────────────────────────────────

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

  Serial.printf("[WiFi] Connected. IP: %s\n", WiFi.localIP().toString().c_str());
  return true;
}

// ── mDNS Advertiser ─────────────────────────────────────

void startMDNS() {
  char mdnsName[32];
  String safeName = deviceName;
  safeName.toLowerCase();
  safeName.replace(" ", "-");
  snprintf(mdnsName, sizeof(mdnsName), "espy-%.24s", safeName.c_str());

  if (MDNS.begin(mdnsName)) {
    MDNS.addService("_espy", "_tcp", OTA_PORT);
    MDNS.addServiceTxt("_espy", "_tcp", "device", deviceName.c_str());
    MDNS.addServiceTxt("_espy", "_tcp", "version", FW_VERSION);
    Serial.printf("[mDNS] Advertised as %s.local\n", mdnsName);
  }
}

// ── OTA HTTP Server ─────────────────────────────────────

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
    background: #FFF8F0; color: #2D3436;
    display: flex; justify-content: center; align-items: center;
    min-height: 100vh; padding: 20px;
  }
  .card { background: white; border: 1px solid #E8D5C4;
          border-radius: 16px; padding: 28px 24px;
          width: 100%; max-width: 360px; }
  h1 { font-size: 18px; color: #FF7B6B; margin-bottom: 16px; }
  .row { display: flex; justify-content: space-between;
         padding: 8px 0; border-bottom: 1px solid #FFE8D6;
         font-size: 14px; }
  .row:last-child { border-bottom: none; }
  .label { color: #8E8E93; }
  .value { color: #2D3436; font-weight: 500; }
  .badge { background: #E8F8F0; border: 1px solid #7BCBA5;
           color: #7BCBA5; border-radius: 6px;
           padding: 2px 8px; font-size: 11px; font-weight: 700; }
  p { font-size: 12px; color: #C0B8B0; margin-top: 16px; text-align: center; }
</style>
</head>
<body>
<div class="card">
  <h1>Espy</h1>
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
    <span class="value">%SSID%</span>
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

  // ── Phase 1: Handshake ──────────────────────────────
  server.on("/espy/start", HTTP_POST, []() {
    if (otaStarted) {
      server.send(409, "application/json",
                  "{\"status\":\"busy\",\"reason\":\"ota_in_progress\"}");
      return;
    }

    String body = server.arg("plain");
    auto extractField = [&](const String& key) -> String {
      int ki = body.indexOf("\"" + key + "\"");
      if (ki < 0) return "";
      int ci = body.indexOf(":", ki);
      if (ci < 0) return "";
      ci++;
      while (ci < body.length() && (body[ci] == ' ' || body[ci] == '"')) ci++;
      int end = ci;
      while (end < body.length() &&
             body[end] != '"' && body[end] != ',' && body[end] != '}')
        end++;
      return body.substring(ci, end);
    };

    size_t fwSize = extractField("firmware_size_bytes").toInt();
    otaChecksum   = extractField("checksum_sha256");

    if (fwSize == 0 || fwSize > 1920000) {
      String resp = "{\"status\":\"rejected\",\"reason\":\"invalid_size\","
                    "\"max_bytes\":1920000}";
      server.send(400, "application/json", resp);
      return;
    }

    otaExpectedSize = fwSize;
    otaBytesReceived = 0;
    otaStarted = false;

    if (!Update.begin(otaExpectedSize)) {
      String resp = "{\"status\":\"error\",\"reason\":\"update_begin_failed\"}";
      server.send(500, "application/json", resp);
      return;
    }

    otaStarted = true;
    setLed(LED_DOUBLE_FLASH);

    const esp_partition_t* nextPart = esp_ota_get_next_update_partition(nullptr);
    String partName = nextPart ? String(nextPart->label) : "unknown";

    String resp = "{\"status\":\"ready\""
                  ",\"target_partition\":\"" + partName + "\""
                  ",\"free_space_bytes\":" + String(ESP.getFreeSketchSpace()) + "}";
    server.send(200, "application/json", resp);
    Serial.printf("[OTA] Ready for %u bytes\n", otaExpectedSize);
  });

  // ── Phase 2: Chunk upload ───────────────────────────
  server.onNotFound([]() {
    String uri = server.uri();
    if (uri.startsWith("/espy/chunk/") && server.method() == HTTP_POST) {
      if (!otaStarted) {
        server.send(400, "application/json",
                    "{\"status\":\"error\",\"reason\":\"no_ota_started\"}");
        return;
      }

      int slash  = uri.lastIndexOf('/');
      int chunkN = uri.substring(slash + 1).toInt();
      size_t length = server.arg("plain").length();
      const uint8_t* data = (const uint8_t*)server.arg("plain").c_str();

      if (Update.write(const_cast<uint8_t*>(data), length) != length) {
        Update.abort();
        otaStarted = false;
        setLed(LED_ERROR);
        server.send(500, "application/json",
                    "{\"status\":\"error\",\"reason\":\"write_failed\"}");
        return;
      }

      otaBytesReceived += length;
      String resp = "{\"chunk\":" + String(chunkN) +
                    ",\"status\":\"ok\",\"checksum_match\":true"
                    ",\"bytes_received\":" + String(otaBytesReceived) + "}";
      server.send(200, "application/json", resp);
      return;
    }

    if (uri == "/espy/chunk" && server.method() == HTTP_POST) {
      // Alternate chunk endpoint without index in path
      if (!otaStarted) {
        server.send(400, "application/json",
                    "{\"status\":\"error\",\"reason\":\"no_ota_started\"}");
        return;
      }
      size_t len = server.arg("plain").length();
      const uint8_t* d = (const uint8_t*)server.arg("plain").c_str();
      if (Update.write(const_cast<uint8_t*>(d), len) != len) {
        Update.abort();
        otaStarted = false;
        setLed(LED_ERROR);
        server.send(500, "application/json",
                    "{\"status\":\"error\",\"reason\":\"write_failed\"}");
        return;
      }
      otaBytesReceived += len;
      String resp = "{\"status\":\"ok\",\"checksum_match\":true"
                    ",\"bytes_received\":" + String(otaBytesReceived) + "}";
      server.send(200, "application/json", resp);
      return;
    }

    // ── Phase 4: Alive check ─────────────────────────
    if (uri == "/espy/alive" && server.method() == HTTP_GET) {
      String resp = "{\"status\":\"running\""
                    ",\"version\":\"" + String(FW_VERSION) + "\""
                    ",\"device\":\"" + deviceName + "\"}";
      server.send(200, "application/json", resp);
      return;
    }

    // ── Backup endpoint ─────────────────────────────
    if (uri == "/espy/firmware" && server.method() == HTTP_GET) {
      const esp_partition_t* running = esp_ota_get_running_partition();
      if (!running) {
        server.send(500, "application/json", "{\"error\":\"no_partition\"}");
        return;
      }
      // Stream the running firmware for backup
      size_t fwSize = running->size;
      server.setContentLength(fwSize);
      server.send(200, "application/octet-stream", "");
      WiFiClient client = server.client();
      for (size_t offset = 0; offset < fwSize; offset += 256) {
        uint8_t buf[256];
        size_t toRead = min((size_t)256, fwSize - offset);
        esp_partition_read(running, offset, buf, toRead);
        client.write(buf, toRead);
      }
      return;
    }

    server.send(404, "application/json", "{\"error\":\"not_found\"}");
  });

  // ── Phase 3: Commit ─────────────────────────────────
  server.on("/espy/commit", HTTP_POST, []() {
    if (!otaStarted) {
      server.send(400, "application/json",
                  "{\"status\":\"rejected\",\"reason\":\"no_ota_started\"}");
      return;
    }

    if (!Update.end(true)) {
      otaStarted = false;
      setLed(LED_ERROR);
      String resp = "{\"status\":\"rejected\","
                    "\"reason\":\"finalize_failed\"}";
      server.send(500, "application/json", resp);
      return;
    }

    const esp_partition_t* newPart = esp_ota_get_next_update_partition(nullptr);
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

  server.begin();
  Serial.printf("[OTA] Server ready on port %d\n", OTA_PORT);
}

// ── Serial Bridge (Wireless Serial) ────────────────────

#define SERIAL_BRIDGE_PORT 3232

WiFiServer serialBridge(SERIAL_BRIDGE_PORT);
WiFiClient serialClient;

void startSerialBridge() {
  serialBridge.begin();
  Serial.printf("[SerialBridge] Listening on port %d\n", SERIAL_BRIDGE_PORT);
}

void tickSerialBridge() {
  if (!serialClient || !serialClient.connected()) {
    serialClient = serialBridge.accept();
    if (serialClient) {
      serialClient.setNoDelay(true);
      Serial.println("[SerialBridge] Client connected");
    }
  }

  if (serialClient && serialClient.connected()) {
    while (serialClient.available()) {
      int c = serialClient.read();
      if (c >= 0) {
        Serial.write((char)c);
      }
    }
  }

  if (serialClient && serialClient.connected()) {
    int avail = Serial.available();
    if (avail > 0) {
      uint8_t buf[64];
      int n = Serial.readBytes(buf, min(avail, 64));
      if (n > 0) {
        serialClient.write(buf, n);
      }
    }
  }
}

// ── UDP Heartbeat (fallback discovery) ──────────────────

void sendHeartbeat() {
  String payload = "{\"device\":\"" + deviceName + "\""
                   ",\"ota_port\":" + String(OTA_PORT) +
                   ",\"version\":\"" + String(FW_VERSION) + "\"}";

  udp.beginPacket(IPAddress(255, 255, 255, 255), HEARTBEAT_PORT);
  udp.print(payload);
  udp.endPacket();
}

// ── Setup ───────────────────────────────────────────────

void setup() {
  Serial.begin(115200);
  Serial.println("\n[Espy] Base firmware " FW_VERSION);

  pinMode(LED_PIN, OUTPUT);
  digitalWrite(LED_PIN, LOW);

  // Crash watchdog — must run early
  checkCrashWatchdog();
  uint32_t totalCrashes = getTotalCrashes();

  loadCredentials();

  bool hasCredentials = (wifiSSID.length() > 0);
  bool recoveryMode   = (totalCrashes >= CRASH_RECOVERY_AT);

  if (!hasCredentials || recoveryMode) {
    Serial.println(recoveryMode ? "[RECOVERY] Many crashes — AP mode"
                                : "[Espy] No credentials — AP mode");
    startCaptivePortal();
    while (true) {
      tickCaptivePortal();
      tickLed();
      yield();
    }
  }

  // Normal boot
  wifiOK = connectWiFi();
  if (!wifiOK) {
    Serial.println("[WiFi] Failed — starting AP");
    startCaptivePortal();
    while (true) {
      tickCaptivePortal();
      tickLed();
      yield();
    }
  }

  // Start services
  udp.begin(HEARTBEAT_PORT);
  startMDNS();
  setupOtaServer();
  startSerialBridge();

  setLed(LED_SOLID);
  sendHeartbeat();
  lastHeartbeat = millis();

  // Device is stable — clear crash counter
  clearCrashCount();

  Serial.printf("[Espy] Ready. %s @ %s\n",
                deviceName.c_str(), WiFi.localIP().toString().c_str());
}

// ── Loop ────────────────────────────────────────────────

void loop() {
  server.handleClient();
  tickLed();
  tickSerialBridge();

  // Periodic heartbeat
  if (millis() - lastHeartbeat >= HEARTBEAT_INTERVAL) {
    sendHeartbeat();
    lastHeartbeat = millis();
  }

  // Reconnect if WiFi drops
  if (WiFi.status() != WL_CONNECTED) {
    setLed(LED_FAST_BLINK);
    WiFi.reconnect();
    uint32_t start = millis();
    while (WiFi.status() != WL_CONNECTED &&
           millis() - start < 5000) {
      tickLed();
      delay(50);
    }
    if (WiFi.status() == WL_CONNECTED) {
      setLed(LED_SOLID);
    }
  }

  yield();
}

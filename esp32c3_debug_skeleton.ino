/**
 * ESP32-C3 Debug / Compilation / Parser Skeleton
 * Board  : ESP32-C3 (8 MB flash, custom partition)
 * Author : <your name>
 * Date   : 2026-06-11
 *
 * Partition table (boards.txt or CSV below — select "8M with spiffs" or use
 * a custom CSV pointed to from platformio.ini / Arduino extra flags):
 *
 *   # Name,   Type, SubType,  Offset,    Size,   Flags
 *   nvs,      data, nvs,      0x9000,    0x5000,
 *   otadata,  data, ota,      0xe000,    0x2000,
 *   app0,     app,  ota_0,    0x10000,   0x330000,
 *   app1,     app,  ota_1,    0x340000,  0x330000,
 *   spiffs,   data, spiffs,   0x670000,  0x180000,
 *   coredump, data, coredump, 0x7F0000,  0x10000,
 *
 * Arduino IDE board config:
 *   Board            : "ESP32C3 Dev Module"
 *   Flash Size       : "8MB (64Mb)"
 *   Partition Scheme : "8M with spiffs (3MB APP/1.5MB SPIFFS)" or custom CSV
 *   Upload Speed     : 921600
 *   CPU Frequency    : 160 MHz
 *   Core Debug Level : "Debug"  ← important for Serial debug output
 */

// ── Common library includes ────────────────────────────────────────────────
#include <Arduino.h>

// WiFi / networking
#include <WiFi.h>
#include <WiFiClient.h>
#include <HTTPClient.h>
#include <WebServer.h>          // ESP32 built-in
#include <DNSServer.h>

// Storage
#include <SPIFFS.h>
#include <Preferences.h>        // NVS key-value store
#include <ArduinoJson.h>        // Install: "ArduinoJson" by Benoit Blanchon

// Serial parsing helpers
#include <StreamUtils.h>        // Install: "StreamUtils" by Benoit Blanchon

// Time
#include <time.h>

// OTA
#include <Update.h>
#include <ArduinoOTA.h>

// Misc utilities
#include <esp_log.h>            // Native ESP-IDF log macros
#include <esp_system.h>
#include <esp_chip_info.h>


// ── Configuration ──────────────────────────────────────────────────────────
#define WIFI_SSID      "YOUR_SSID"
#define WIFI_PASS      "YOUR_PASSWORD"
#define SERIAL_BAUD    115200
#define DEBUG_TAG      "MAIN"

// Use Arduino Serial for human-readable debug; also mirrors to ESP_LOGx
#define DLOG(fmt, ...) \
  do { Serial.printf("[DBG][%s] " fmt "\n", DEBUG_TAG, ##__VA_ARGS__); \
       ESP_LOGD(DEBUG_TAG, fmt, ##__VA_ARGS__); } while (0)

#define WLOG(fmt, ...) \
  do { Serial.printf("[WRN][%s] " fmt "\n", DEBUG_TAG, ##__VA_ARGS__); \
       ESP_LOGW(DEBUG_TAG, fmt, ##__VA_ARGS__); } while (0)

#define ELOG(fmt, ...) \
  do { Serial.printf("[ERR][%s] " fmt "\n", DEBUG_TAG, ##__VA_ARGS__); \
       ESP_LOGE(DEBUG_TAG, fmt, ##__VA_ARGS__); } while (0)


// ── Globals ────────────────────────────────────────────────────────────────
WebServer   server(80);
Preferences prefs;

static String  rxBuffer   = "";   // accumulates incoming serial bytes
static bool    wifiReady  = false;


// ══════════════════════════════════════════════════════════════════════════
//  PARSER  — lightweight line-oriented command parser
// ══════════════════════════════════════════════════════════════════════════

/**
 * parseCommand — splits a line like "CMD arg1 arg2" into tokens.
 * Returns false if the line is empty or a comment ('#').
 */
bool parseCommand(const String& line, String& cmd, String args[], int& argc, int maxArgs = 8) {
  String trimmed = line;
  trimmed.trim();
  if (trimmed.isEmpty() || trimmed.startsWith("#")) return false;

  int   pos   = 0;
  argc        = 0;
  bool  first = true;

  while (pos <= (int)trimmed.length()) {
    int sp = trimmed.indexOf(' ', pos);
    if (sp == -1) sp = trimmed.length();

    String token = trimmed.substring(pos, sp);
    token.trim();
    if (token.length() > 0) {
      if (first) { cmd = token; first = false; }
      else if (argc < maxArgs) args[argc++] = token;
    }
    pos = sp + 1;
  }
  cmd.toUpperCase();
  return !cmd.isEmpty();
}

/** Dispatch parsed commands from the Serial REPL */
void dispatchCommand(const String& cmd, String args[], int argc) {
  if (cmd == "HELP") {
    Serial.println(F(
      "Commands:\r\n"
      "  HELP            — this menu\r\n"
      "  INFO            — chip / heap / partition info\r\n"
      "  FS LIST         — list SPIFFS files\r\n"
      "  FS READ <path>  — dump SPIFFS file\r\n"
      "  FS DEL  <path>  — delete SPIFFS file\r\n"
      "  WIFI STATUS     — WiFi details\r\n"
      "  PREFS GET <key> — read NVS key\r\n"
      "  PREFS SET <key> <val> — write NVS key\r\n"
      "  RESET           — software reset\r\n"
    ));

  } else if (cmd == "INFO") {
    esp_chip_info_t ci;
    esp_chip_info(&ci);
    Serial.printf("  Chip   : ESP32-C3 rev %d, %d cores\r\n", ci.revision, ci.cores);
    Serial.printf("  Flash  : %u MB\r\n", spi_flash_get_chip_size() >> 20);
    Serial.printf("  Heap   : %u free / %u total\r\n",
                  ESP.getFreeHeap(), ESP.getHeapSize());
    Serial.printf("  PSRAM  : %u free / %u total\r\n",
                  ESP.getFreePsram(), ESP.getPsramSize());
    Serial.printf("  Sketch : %u used / %u total\r\n",
                  ESP.getSketchSize(), ESP.getFreeSketchSpace() + ESP.getSketchSize());
    Serial.printf("  Uptime : %lu ms\r\n", millis());

  } else if (cmd == "FS") {
    if (argc == 0) { Serial.println("FS needs a sub-command (LIST/READ/DEL)"); return; }
    String sub = args[0]; sub.toUpperCase();

    if (sub == "LIST") {
      File root = SPIFFS.open("/");
      File f    = root.openNextFile();
      int  cnt  = 0;
      while (f) {
        Serial.printf("  %-40s  %6u B\r\n", f.name(), f.size());
        f = root.openNextFile(); cnt++;
      }
      Serial.printf("  [%d files, %u B used / %u B total]\r\n",
                    cnt, SPIFFS.usedBytes(), SPIFFS.totalBytes());

    } else if (sub == "READ" && argc >= 2) {
      File f = SPIFFS.open(args[1]);
      if (!f) { ELOG("File not found: %s", args[1].c_str()); return; }
      while (f.available()) Serial.write(f.read());
      Serial.println();
      f.close();

    } else if (sub == "DEL" && argc >= 2) {
      if (SPIFFS.remove(args[1])) DLOG("Deleted %s", args[1].c_str());
      else ELOG("Delete failed: %s", args[1].c_str());
    }

  } else if (cmd == "WIFI") {
    Serial.printf("  Status : %s\r\n", WiFi.isConnected() ? "connected" : "disconnected");
    if (WiFi.isConnected()) {
      Serial.printf("  SSID   : %s\r\n", WiFi.SSID().c_str());
      Serial.printf("  IP     : %s\r\n", WiFi.localIP().toString().c_str());
      Serial.printf("  RSSI   : %d dBm\r\n", WiFi.RSSI());
    }

  } else if (cmd == "PREFS") {
    if (argc < 2) { Serial.println("PREFS needs GET/SET + key"); return; }
    String sub = args[0]; sub.toUpperCase();
    prefs.begin("app", false);
    if (sub == "GET") {
      String val = prefs.getString(args[1].c_str(), "<not set>");
      Serial.printf("  %s = %s\r\n", args[1].c_str(), val.c_str());
    } else if (sub == "SET" && argc >= 3) {
      prefs.putString(args[1].c_str(), args[2]);
      DLOG("Saved %s = %s", args[1].c_str(), args[2].c_str());
    }
    prefs.end();

  } else if (cmd == "RESET") {
    Serial.println("Rebooting…");
    delay(200);
    ESP.restart();

  } else {
    Serial.printf("  Unknown command: %s (try HELP)\r\n", cmd.c_str());
  }
}


// ══════════════════════════════════════════════════════════════════════════
//  HTTP ROUTES  (debug endpoints)
// ══════════════════════════════════════════════════════════════════════════

void routeInfo() {
  StaticJsonDocument<512> doc;
  doc["chip"]        = "ESP32-C3";
  doc["freeHeap"]    = ESP.getFreeHeap();
  doc["flashSize"]   = spi_flash_get_chip_size();
  doc["uptime_ms"]   = millis();
  doc["ip"]          = WiFi.localIP().toString();
  String body;
  serializeJsonPretty(doc, body);
  server.send(200, "application/json", body);
}

void routeNotFound() {
  server.send(404, "text/plain", "404 – not found\r\n");
}


// ══════════════════════════════════════════════════════════════════════════
//  WIFI HELPER
// ══════════════════════════════════════════════════════════════════════════

void wifiConnect(unsigned long timeoutMs = 15000) {
  Serial.printf("Connecting to %s", WIFI_SSID);
  WiFi.mode(WIFI_STA);
  WiFi.begin(WIFI_SSID, WIFI_PASS);
  unsigned long t0 = millis();
  while (!WiFi.isConnected() && (millis() - t0) < timeoutMs) {
    delay(300); Serial.print('.');
  }
  Serial.println();
  if (WiFi.isConnected()) {
    wifiReady = true;
    DLOG("WiFi OK — IP: %s", WiFi.localIP().toString().c_str());
  } else {
    WLOG("WiFi timeout — continuing without network");
  }
}


// ══════════════════════════════════════════════════════════════════════════
//  SETUP
// ══════════════════════════════════════════════════════════════════════════

void setup() {
  Serial.begin(SERIAL_BAUD);
  delay(500);
  Serial.println(F("\r\n=== ESP32-C3 Debug Skeleton ==="));

  // — SPIFFS ——————————————————————————————————————————————
  if (!SPIFFS.begin(true)) {           // true = format on fail
    ELOG("SPIFFS mount failed");
  } else {
    DLOG("SPIFFS OK — %u / %u bytes used",
         SPIFFS.usedBytes(), SPIFFS.totalBytes());
  }

  // — WiFi ————————————————————————————————————————————————
  wifiConnect();

  // — HTTP server ————————————————————————————————————————
  if (wifiReady) {
    server.on("/info",  HTTP_GET, routeInfo);
    server.onNotFound(routeNotFound);
    server.begin();
    DLOG("HTTP server started on port 80");
  }

  // — OTA ————————————————————————————————————————————————
  ArduinoOTA.setHostname("esp32c3-debug");
  ArduinoOTA.onStart([]()   { DLOG("OTA start"); });
  ArduinoOTA.onEnd([]()     { DLOG("OTA done"); });
  ArduinoOTA.onError([](ota_error_t e) { ELOG("OTA error %u", e); });
  ArduinoOTA.begin();

  Serial.println(F("Type HELP for commands.\r\n> "));
}


// ══════════════════════════════════════════════════════════════════════════
//  LOOP
// ══════════════════════════════════════════════════════════════════════════

void loop() {
  // — OTA + HTTP ————————————————————————————————————————
  ArduinoOTA.handle();
  if (wifiReady) server.handleClient();

  // — Serial REPL ————————————————————————————————————————
  while (Serial.available()) {
    char c = (char)Serial.read();
    if (c == '\r') continue;           // ignore CR
    if (c == '\n') {
      if (rxBuffer.length() > 0) {
        String cmd;
        String args[8];
        int    argc = 0;
        if (parseCommand(rxBuffer, cmd, args, argc)) {
          dispatchCommand(cmd, args, argc);
        }
        rxBuffer = "";
      }
      Serial.print("> ");
    } else {
      rxBuffer += c;
    }
  }
}

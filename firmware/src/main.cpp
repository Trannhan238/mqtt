#include <WiFi.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>
#include <LittleFS.h>
#include <time.h>

// --- 1. CẤU HÌNH HỆ THỐNG ---
const char* ssid = "TV";
const char* password = "0383678565";
const char* mqtt_server = "broker.emqx.io"; 
const char* mac_addr = "E05A1BACAB50"; 

#define LED_PIN 25 
#define SCHEDULE_FILE "/schedules.json"

WiFiClient espClient;
PubSubClient client(espClient);

// Cấu trúc lịch trình
struct BellSchedule {
    String time;
    int pulses, on_ms, off_ms;
};
BellSchedule schedules[30]; // Sức chứa 30 lịch trình
int scheduleCount = 0;

// Trạng thái vận hành
bool isRinging = false;
int currentPulse = 0, totalPulses = 0, onDuration = 0, offDuration = 0;
unsigned long lastActionTime = 0, lastHeartbeat = 0;
bool ledState = false;
String ringType = "AUTO";

// --- 2. HÀM GỬI BÁO CÁO QUA MQTT ---
void sendLog(String status, String msg, String event = "") {
    if (!client.connected()) return;
    JsonDocument doc;
    doc["event_type"] = (event == "") ? ringType : event;
    doc["status"] = status;
    doc["message"] = msg;
    doc["rssi"] = WiFi.RSSI();
    
    char buffer[256];
    serializeJson(doc, buffer);
    String topic = "school_bell/" + String(mac_addr) + "/logs";
    client.publish(topic.c_str(), buffer);
    Serial.printf(">>> [MQTT LOG] %s\n", msg.c_str());
}

// --- 3. QUẢN LÝ LƯU TRỮ ---
void saveSchedulesToFS() {
    JsonDocument doc;
    JsonArray array = doc.to<JsonArray>();
    for (int i = 0; i < scheduleCount; i++) {
        JsonObject obj = array.add<JsonObject>();
        obj["t"] = schedules[i].time;
        obj["n"] = schedules[i].pulses;
        obj["on"] = schedules[i].on_ms;
        obj["off"] = schedules[i].off_ms;
    }
    File file = LittleFS.open(SCHEDULE_FILE, FILE_WRITE);
    if (file) { 
        serializeJson(doc, file); 
        file.close(); 
        Serial.println("--- [FS] Đã lưu lịch trình mới vào Flash.");
    }
}

void loadSchedulesFromFS() {
    if (!LittleFS.exists(SCHEDULE_FILE)) return;
    File file = LittleFS.open(SCHEDULE_FILE, FILE_READ);
    JsonDocument doc;
    if (deserializeJson(doc, file) == DeserializationError::Ok) {
        JsonArray array = doc.as<JsonArray>();
        scheduleCount = 0;
        for (JsonObject item : array) {
            if (scheduleCount >= 30) break;
            schedules[scheduleCount++] = {item["t"].as<String>(), item["n"], item["on"], item["off"]};
        }
        Serial.printf("--- [FS] Đã nạp %d lịch trình từ bộ nhớ Flash.\n", scheduleCount);
    }
    file.close();
}

// --- 4. LOGIC CHUÔNG ---
void startBell(int pulses, int on_ms, int off_ms, String type) {
    if (isRinging) return;
    totalPulses = (pulses <= 0) ? 1 : pulses; 
    onDuration = (on_ms <= 10) ? 1000 : on_ms; 
    offDuration = (off_ms <= 10) ? 500 : off_ms;
    ringType = type; currentPulse = 0; isRinging = true;
    lastActionTime = millis(); ledState = true; 
    digitalWrite(LED_PIN, HIGH);
    Serial.printf("🔔 [BELL] BẮT ĐẦU (%s): %d hồi\n", type.c_str(), totalPulses);
}

void updateBell() {
    if (!isRinging) return;
    unsigned long now = millis();
    if (ledState && now - lastActionTime >= onDuration) {
        digitalWrite(LED_PIN, LOW); ledState = false; lastActionTime = now;
        if (++currentPulse >= totalPulses) {
            isRinging = false;
            digitalWrite(LED_PIN, LOW); // Cưỡng bức tắt
            sendLog("SUCCESS", "Completed ringing.");
            Serial.println("✅ [BELL] Kết thúc.");
        }
    } else if (!ledState && now - lastActionTime >= offDuration) {
        digitalWrite(LED_PIN, HIGH); ledState = true; lastActionTime = now;
    }
}

void requestSync() {
    String topic = "school_bell/" + String(mac_addr) + "/request_sync";
    client.publish(topic.c_str(), "{}");
    Serial.println("--- [SYNC] Yêu cầu lấy lịch trình mới...");
}

// --- 5. MQTT CALLBACK (Chuẩn ArduinoJson V7) ---
void callback(char* topic, byte* payload, unsigned int length) {
    Serial.printf("<<< [MQTT] Nhận gói tin: %d bytes\n", length);
    String topicStr = String(topic);
    JsonDocument doc; 
    
    DeserializationError error = deserializeJson(doc, payload, length);
    if (error) {
        Serial.printf("❌ [JSON] Parse failed: %s\n", error.c_str());
        return;
    }

    if (topicStr.endsWith("/sync_now")) {
        Serial.println("<<< [CMD] Nhận lệnh cập nhật (Auto-Push).");
        requestSync();
    } 
    else if (topicStr.endsWith("/sync")) {
        JsonArray sch = doc["sch"];
        scheduleCount = 0;
        for (JsonObject item : sch) {
            if (scheduleCount >= 30) break;
            schedules[scheduleCount].time = item["t"].as<String>();
            schedules[scheduleCount].pulses = item["p"]["n"].as<int>();
            schedules[scheduleCount].on_ms = item["p"]["on"].as<int>();
            schedules[scheduleCount].off_ms = item["p"]["off"].as<int>();
            scheduleCount++;
        }
        saveSchedulesToFS();
        
        // Fix Warning: Sử dụng chuẩn .is<T>() của V7
        if (doc["server_time"].is<long>()) {
            struct timeval tv = { (long)doc["server_time"], 0 };
            settimeofday(&tv, NULL);
            Serial.println("⏰ [TIME] Đã đồng bộ giờ từ gói Sync.");
        }
        Serial.printf("<<< [SYNC] Cập nhật %d lịch thành công.\n", scheduleCount);
    } 
    else if (topicStr == "school_bell/broadcast/time") {
        if (doc["timestamp"].is<long>()) {
            struct timeval tv = { (long)doc["timestamp"], 0 };
            settimeofday(&tv, NULL);
        }
    } 
    else if (topicStr.endsWith("/cmd") && doc["action"] == "ring_now") {
        Serial.println("<<< [CMD] Lệnh REO TỨC THỜI.");
        startBell(doc["p"]["n"], doc["p"]["on"], doc["p"]["off"], "MANUAL");
    }
}

// --- 6. SETUP ---
void setup() {
    Serial.begin(115200);
    delay(1000);
    Serial.println("\n\n--- HỆ THỐNG CHUÔNG TRƯỜNG HỌC (PRO) ---");

    // Cấu hình Múi giờ Việt Nam (ICT-7)
    configTime(7 * 3600, 0, "pool.ntp.org");
    setenv("TZ", "ICT-7", 1); 
    tzset();

    pinMode(LED_PIN, OUTPUT);
    digitalWrite(LED_PIN, LOW);
    
    if (LittleFS.begin(true)) loadSchedulesFromFS();

    WiFi.begin(ssid, password);
    while (WiFi.status() != WL_CONNECTED) { delay(500); Serial.print("."); }
    Serial.println("\n✅ WiFi Connected!");

    client.setServer(mqtt_server, 1883);
    client.setCallback(callback);
    
    // NÂNG CẤP: Tăng bộ đệm MQTT lên 4KB để nhận đủ 30 lịch trình
    client.setBufferSize(4096); 
    Serial.println("🚀 [System] MQTT Buffer: 4096 bytes.");
}

// --- 7. LOOP ---
void loop() {
    if (!client.connected()) {
        if (client.connect(mac_addr)) {
            Serial.println("✅ MQTT Connected!");
            String base = "school_bell/" + String(mac_addr);
            client.subscribe((base + "/sync").c_str());
            client.subscribe((base + "/sync_now").c_str());
            client.subscribe((base + "/cmd").c_str());
            client.subscribe("school_bell/broadcast/time");
            requestSync();
        }
    }
    client.loop();
    updateBell();

    if (millis() - lastHeartbeat > 30000) {
        sendLog("ONLINE", "Heartbeat OK", "HEARTBEAT");
        lastHeartbeat = millis();
    }

    static time_t lastCheck = 0;
    time_t now = time(NULL);
    if (now != lastCheck) {
        lastCheck = now;
        struct tm* tm_info = localtime(&now);
        char timeStr[6];
        strftime(timeStr, sizeof(timeStr), "%H:%M", tm_info);

        if (now % 10 == 0) {
            Serial.printf("⏱ [Clock] %s | Lịch: %d bản ghi\n", timeStr, scheduleCount);
        }

        if (!isRinging) {
            for (int i = 0; i < scheduleCount; i++) {
                if (schedules[i].time == String(timeStr)) {
                    static String lastTriggerMinute = "";
                    if (lastTriggerMinute != String(timeStr)) {
                        Serial.printf("🚀 [MATCH] Reo tự động lúc %s\n", timeStr);
                        startBell(schedules[i].pulses, schedules[i].on_ms, schedules[i].off_ms, "AUTO");
                        lastTriggerMinute = String(timeStr);
                    }
                    break;
                }
            }
        }
    }
    delay(10);
}
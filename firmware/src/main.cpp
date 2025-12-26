#include <WiFi.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>
#include <NTPClient.h>
#include <WiFiUdp.h>
#include <LittleFS.h>

// --- 1. CẤU HÌNH ---
const char* ssid = "TV";
const char* password = "0383678565";
const char* mqtt_server = "broker.emqx.io"; 
const char* mac_addr = "E05A1BACAB50"; 

#define LED_PIN 25 
#define SCHEDULE_FILE "/schedules.json"

WiFiClient espClient;
PubSubClient client(espClient);
WiFiUDP ntpUDP;
NTPClient timeClient(ntpUDP, "pool.ntp.org", 7 * 3600); 

struct BellSchedule {
    String time;
    int pulses;
    int on_ms;
    int off_ms;
};
BellSchedule schedules[30];
int scheduleCount = 0;

// Biến quản lý trạng thái reo chuông
bool isRinging = false;
int currentPulse = 0, totalPulses = 0, onDuration = 0, offDuration = 0;
unsigned long lastActionTime = 0;
bool ledState = false;
String ringType = "AUTO"; // Để phân biệt reo theo lịch hay bấm tay

// --- 2. HÀM GỬI BÁO CÁO (FEEDBACK) ---
void sendLog(String status, String msg) {
    if (!client.connected()) return;
    
    JsonDocument doc;
    doc["event_type"] = ringType; // "AUTO" hoặc "MANUAL"
    doc["status"] = status;       // "SUCCESS"
    doc["message"] = msg;
    doc["time"] = timeClient.getFormattedTime();

    char buffer[256];
    serializeJson(doc, buffer);
    
    String logTopic = "school_bell/" + String(mac_addr) + "/logs";
    client.publish(logTopic.c_str(), buffer);
    Serial.println("📤 Đã gửi báo cáo về Backend: " + msg);
}

// --- 3. HÀM LƯU TRỮ & LOGIC ---
void saveSchedulesToFS() {
    JsonDocument doc;
    JsonArray array = doc.to<JsonArray>();
    for (int i = 0; i < scheduleCount; i++) {
        JsonObject obj = array.add<JsonObject>();
        obj["t"] = schedules[i].time; obj["n"] = schedules[i].pulses;
        obj["on"] = schedules[i].on_ms; obj["off"] = schedules[i].off_ms;
    }
    File file = LittleFS.open(SCHEDULE_FILE, FILE_WRITE);
    if (file) { serializeJson(doc, file); file.close(); }
}

void loadSchedulesFromFS() {
    if (!LittleFS.exists(SCHEDULE_FILE)) return;
    File file = LittleFS.open(SCHEDULE_FILE, FILE_READ);
    JsonDocument doc;
    if (deserializeJson(doc, file) == DeserializationError::Ok) {
        JsonArray array = doc.as<JsonArray>();
        scheduleCount = 0;
        for (JsonObject item : array) {
            schedules[scheduleCount] = {item["t"].as<String>(), item["n"], item["on"], item["off"]};
            scheduleCount++;
        }
        Serial.printf("📂 Nạp %d lịch từ Flash.\n", scheduleCount);
    }
    file.close();
}

void startBell(int pulses, int on_ms, int off_ms, String type) {
    if (isRinging) return;
    totalPulses = pulses; onDuration = on_ms; offDuration = off_ms;
    ringType = type; // Lưu lại kiểu reo để tí nữa báo cáo
    currentPulse = 0; isRinging = true; lastActionTime = millis();
    ledState = true; digitalWrite(LED_PIN, HIGH);
    Serial.printf("🔔 BẮT ĐẦU REO (%s): %d hồi...\n", type.c_str(), pulses);
}

void updateBell() {
    if (!isRinging) return;
    unsigned long now = millis();
    if (ledState) {
        if (now - lastActionTime >= onDuration) {
            digitalWrite(LED_PIN, LOW); ledState = false; lastActionTime = now;
            currentPulse++;
            if (currentPulse >= totalPulses) { 
                isRinging = false; 
                Serial.println("✅ Reo xong!");
                sendLog("SUCCESS", "Đã hoàn thành " + String(totalPulses) + " hồi chuông.");
            }
        }
    } else {
        if (now - lastActionTime >= offDuration) {
            digitalWrite(LED_PIN, HIGH); ledState = true; lastActionTime = now;
        }
    }
}

void requestSync() {
    String reqTopic = "school_bell/" + String(mac_addr) + "/request_sync";
    client.publish(reqTopic.c_str(), "{}");
}

void callback(char* topic, byte* payload, unsigned int length) {
    String topicStr = String(topic);
    JsonDocument doc;
    if (deserializeJson(doc, payload, length) != DeserializationError::Ok) return;

    if (topicStr.endsWith("/sync_now")) {
        requestSync();
    } else if (topicStr.endsWith("/sync")) {
        JsonArray sch = doc["sch"];
        scheduleCount = 0;
        for (JsonObject item : sch) {
            schedules[scheduleCount] = {item["t"].as<String>(), item["p"]["n"], item["p"]["on"], item["p"]["off"]};
            scheduleCount++;
        }
        saveSchedulesToFS();
        Serial.println("✅ Đã đồng bộ lịch mới.");
    } else if (topicStr.endsWith("/cmd") && doc["action"] == "ring_now") {
        startBell(doc["p"]["n"], doc["p"]["on"], doc["p"]["off"], "MANUAL");
    }
}

void setup() {
    Serial.begin(115200);
    pinMode(LED_PIN, OUTPUT);
    if (LittleFS.begin(true)) loadSchedulesFromFS();
    WiFi.begin(ssid, password);
    while (WiFi.status() != WL_CONNECTED) { delay(500); Serial.print("."); }
    client.setServer(mqtt_server, 1883);
    client.setBufferSize(2048);
    client.setCallback(callback);
    timeClient.begin();
}

void loop() {
    if (!client.connected()) {
        if (client.connect(mac_addr)) {
            String base = "school_bell/" + String(mac_addr);
            client.subscribe((base + "/sync").c_str());
            client.subscribe((base + "/sync_now").c_str());
            client.subscribe((base + "/cmd").c_str());
            requestSync();
        }
    }
    client.loop();
    timeClient.update();
    updateBell();

    if (timeClient.isTimeSet()) {
        String currentTime = timeClient.getFormattedTime().substring(0, 5);
        static String lastRung = "";
        if (currentTime != lastRung && !isRinging) {
            for (int i = 0; i < scheduleCount; i++) {
                if (schedules[i].time == currentTime) {
                    startBell(schedules[i].pulses, schedules[i].on_ms, schedules[i].off_ms, "AUTO");
                    lastRung = currentTime;
                    break;
                }
            }
        }
    }
    delay(200);
}
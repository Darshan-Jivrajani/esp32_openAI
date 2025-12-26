#include <WiFi.h>

const char* ssid = "ssid";
const char* password = "1234567890";


const char* serverIP = "192.168.1.104";  // PC IP address
const uint16_t serverPort = 5000;

WiFiClient client;
String clientName = "ESP32_1";

//String clientName = "ESP32_1";
// ============================================

//WiFiClient client;

// -------- Read long message (length-prefixed) --------
String readLongMessage() {
  // Read length header
  String lenStr = client.readStringUntil('\n');
  int length = lenStr.toInt();

  if (length <= 0) return "";

  String message = "";
  unsigned long start = millis();

  // Read exact number of bytes
  while (message.length() < length) {
    if (client.available()) {
      message += char(client.read());
    }

    // Safety timeout (5 seconds)
    if (millis() - start > 5000) {
      break;
    }
  }

  return message;
}

// -------------------- SETUP --------------------
void setup() {
  Serial.begin(115200);
  delay(1000);

  Serial.println("\nConnecting to WiFi...");
  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println("\nWiFi connected");
  Serial.print("ESP32 IP: ");
  Serial.println(WiFi.localIP());

  Serial.println("Connecting to AI server...");
  if (client.connect(serverIP, serverPort)) {
    Serial.println("Connected to server");
    client.println(clientName + " connected");
  } else {
    Serial.println("Server connection failed");
  }

  Serial.println("\nType message and press ENTER:");
}

// -------------------- LOOP --------------------
void loop() {
  // -------- Send message to server --------
  if (Serial.available()) {
    String msg = Serial.readStringUntil('\n');
    msg.trim();

    if (msg.length() > 0 && client.connected()) {
      client.println(msg);
      Serial.println("[SENT] " + msg);
    }
  }

  // -------- Receive AI response --------
  if (client.available()) {
    String aiReply = readLongMessage();

    if (aiReply.length() > 0) {
      Serial.println("\n[AI RESPONSE]");
      Serial.println(aiReply);
      Serial.println("---------------------------------\n");
    }
  }

  // -------- Reconnect if needed --------
  if (!client.connected()) {
    Serial.println("Disconnected from server, reconnecting...");
    delay(2000);
    client.connect(serverIP, serverPort);
  }
}

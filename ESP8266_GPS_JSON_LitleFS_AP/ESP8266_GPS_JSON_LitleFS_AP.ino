/**
  * Version: ESP8266 con módulo GY-NEO6MV2 y LittleFS register
  * Project instructions: https://www.infotronikblog.com/2025/10/esp8266-y-gps-gy-neo6mv2-y-littlefs.html
  * Project repository:   https://github.com/Peyutron/ESP8266-GPS-tracker-KML-converter
  * web: https://www.infotronikblog.com
  * Creator: Carlos MC
  *
  * External Library:
  * - TinyGPS++:        https://github.com/codegardenllc/tiny_gps_plus
  * - ArduinoJson       https://github.com/bblanchon/ArduinoJson
  *
  * ESP8266 Library:    
  * - LittleFS:         https://github.com/littlefs-project/littlefs
  * - ESP8266WiFi:      https://arduino-esp8266.readthedocs.io/en/latest/esp8266wifi/readme.html
  * - ESP8266WebServer: https://links2004.github.io/Arduino/d3/d58/class_e_s_p8266_web_server.html
  * - SoftwareSerial:   https://docs.arduino.cc/learn/built-in-libraries/software-serial/
  * 
  * 
  * Board: LOLIN(WEMOS) D1 mini (clone)
  * - CPU Frequency:   80MHz
  * - Flash frequency: 40Mhz
  *
**/

#include <ESP8266WiFi.h>
#include <LittleFS.h>
#include <TinyGPS++.h>
#include <ESP8266WebServer.h>
#include <SoftwareSerial.h>
#include <ArduinoJson.h>

// Access Point configuration
// Access Point SSID
const char* AP_SSID = "gpsServer";  

// Password
const char* AP_PASS = "!2345678";   
unsigned long previousMillis = 0;   

//Configure data collection interval
const long interval = 10000;        


// Hardware
TinyGPSPlus gps;
SoftwareSerial gpsSerial(13, 15);  // RX=D7(GPIO13), TX=D8(GPIO15)
ESP8266WebServer server(80);

void setup() 
{
  // Start serial communication
  Serial.begin(115200);             

  // Start GPS communication
  gpsSerial.begin(9600);            
  delay(200);

  // 1. Start Access Point
  // Create Access Point
  WiFi.softAP(AP_SSID, AP_PASS);
  // Show IP (192.168.4.1 default)   
  Serial.print("IP del AP: ");
  Serial.println(WiFi.softAPIP());  

  // 2. Start LittleFS
  if (!LittleFS.begin()) 
  {
    Serial.println("Error mounting LittleFS");
    return;
  }

  // 3. Endpoints configuration
  server.on("/gps", HTTP_GET, handleGPSData);       // GET /gps → Datos actuales
  server.on("/download", HTTP_GET, handleDownload); // GET /download → JSON File
  server.on("/clear", HTTP_GET, handleClear);    // DELETE /clear → Delete datas
  server.on("/files", HTTP_GET, handleFileList);    // Show file list
  server.on("/info", HTTP_GET, handleFSInfo);       // File system information

  
  // Start HTTP server
  server.begin(); 
  Serial.println("Servidor HTTP iniciado");
}
void loop() 
{
  server.handleClient();
  
  // Leer datos GPS continuamente
  while (gpsSerial.available() > 0) 
  {
    // Decodificate NMEA data
    if (gps.encode(gpsSerial.read())) 
    {
      // Store data on LittleFS (10 seconds)
      saveGPSData();  
    }
  }
}

// --- Handlers  ---
void handleGPSData() 
{
  // 200 bytes JSON file
  DynamicJsonDocument doc(200);
  doc["sat"] = String(gps.satellites.value());  // N Satéllites 
  doc["lat"] = gps.location.lat();              // Latitude
  doc["lng"] = gps.location.lng();              // Longitude
  doc["tim"] = gps.time.value();                // Time (hhmmsscc format)
  doc["alt"] = gps.altitude.meters();           // Altitude in meters
  doc["spe"] = gps.speed.kmph();                // Speed in km/h
  doc["cur"] = gps.course.deg();              // Compas

  // Convert JSON to String
  String response;
  serializeJson(doc, response);  
  
  // Send answer
  server.send(200, "application/json", response);  
}

void handleDownload() 
{
  Serial.println("Downloading datas");

  // Open file in reading mode
  File file = LittleFS.open("/gps_data.json", "r");  
  if (file) 
  {
    // Send file
    server.streamFile(file, "application/json");  
    file.close();
  } 
  else 
  {
    Serial.println("No file found");
    server.send(404, "text/plain", "No file found");
  }
}

void handleClear() 
{
  Serial.println("Cleaning datas");

  // Delete gps_data.json file 
  LittleFS.remove("/gps_data.json");  
  server.send(200, "application/json", "{\"status\":\"success\"}");
}

void saveGPSData() 
{
  unsigned long currentMillis = millis();
  
  // Store data every 10 seconds:
  if (currentMillis - previousMillis >= interval) 
  {
    previousMillis = currentMillis;
    
    // Filterin no valid datas
    if (!gps.location.isValid()) return;  
    Serial.print(F("N satelites: "));
    Serial.println(String(gps.satellites.value()));
    
    // Open file in append mode
    File file = LittleFS.open("/gps_data.json", "a");  
    if (!file) return;

    DynamicJsonDocument doc(200);
    doc["sat"] = String(gps.satellites.value());  // Satélites visibles
    doc["lat"] = gps.location.lat();      // Latitud
    doc["lng"] = gps.location.lng();      // Longitud
    doc["dat"] = gps.date.value();        // Fecha
    doc["tim"] = gps.time.value();        // Hora (formato hhmmsscc)
    doc["alt"] = gps.altitude.meters();   // Altitud en metros
    doc["spe"] = gps.speed.kmph();        // Velocidad en km/h    
    doc["cur"] = gps.course.deg();

    // Write data on a file
    serializeJson(doc, file);
    
    // New register line
    file.println();

    // Close file
    file.close();
  }
}

// Show all files
void handleFileList() 
{
  Serial.println("All files request");
  
  // Larger buffer for multiple files
  DynamicJsonDocument doc(1024);  
  JsonArray files = doc.createNestedArray("files");
  
  Dir dir = LittleFS.openDir("/");
  while (dir.next()) 
  {
    JsonObject file = files.createNestedObject();
    file["name"] = dir.fileName();
    file["size"] = dir.fileSize();
    file["isDirectory"] = dir.isDirectory();
  }
  
  // File system information
  FSInfo fs_info;
  LittleFS.info(fs_info);
  doc["totalBytes"] = fs_info.totalBytes;
  doc["usedBytes"] = fs_info.usedBytes;
  doc["freeBytes"] = fs_info.totalBytes - fs_info.usedBytes;
  
  String response;
  serializeJson(doc, response);
  server.send(200, "application/json", response);
}

// File system information
void handleFSInfo() 
{
  FSInfo fs_info;
  LittleFS.info(fs_info);
  
  DynamicJsonDocument doc(512);
  doc["totalBytes"] = fs_info.totalBytes;
  doc["usedBytes"] = fs_info.usedBytes;
  doc["freeBytes"] = fs_info.totalBytes - fs_info.usedBytes;
  doc["usedPercent"] = (fs_info.usedBytes * 100.0) / fs_info.totalBytes;
  
  String response;
  serializeJson(doc, response);
  server.send(200, "application/json", response);
}

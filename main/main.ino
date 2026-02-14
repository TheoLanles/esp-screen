#include <WiFi.h>
#include <WebServer.h>
#include <Preferences.h>

// Configuration WiFi
const char* ssid = "Bbox-172D12DD";
const char* password = "tNHPfVkv2YJRbwXU33";

// Objets
WebServer server(80);
Preferences preferences;

// Variables
int modeActuel = 1;
const int LED_PIN = 2; // LED intégrée (GPIO2 pour la plupart des ESP32)

// Variables pour le clignotement
unsigned long previousMillis = 0;
bool ledState = false;

void setup() {
  Serial.begin(115200);
  
  // Configuration LED
  pinMode(LED_PIN, OUTPUT);
  digitalWrite(LED_PIN, LOW);
  
  // Charger le mode sauvegardé
  preferences.begin("config", false);
  modeActuel = preferences.getInt("mode", 1); // Mode 1 par défaut
  preferences.end();
  
  Serial.print("Mode au démarrage : ");
  Serial.println(modeActuel);
  
  // Connexion WiFi
  WiFi.begin(ssid, password);
  Serial.print("Connexion WiFi");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println();
  Serial.print("Connecté ! IP : ");
  Serial.println(WiFi.localIP());
  
  // Routes API
  server.on("/api/mode", HTTP_GET, handleGetMode);
  server.on("/api/mode/set1", HTTP_GET, handleSetMode1);
  server.on("/api/mode/set2", HTTP_GET, handleSetMode2);
  server.on("/api/mode/set3", HTTP_GET, handleSetMode3);
  server.on("/api/reboot", HTTP_GET, handleReboot);
  
  // Démarrer le serveur
  server.begin();
  Serial.println("Serveur HTTP démarré");
}

void loop() {
  server.handleClient();
  
  // Gestion de la LED selon le mode
  gererLED();
}

// Fonction pour gérer la LED selon le mode
void gererLED() {
  unsigned long currentMillis = millis();
  
  switch(modeActuel) {
    case 1:
      // Mode 1 : LED fixe (allumée)
      digitalWrite(LED_PIN, HIGH);
      break;
      
    case 2:
      // Mode 2 : Clignotement lent (1 seconde)
      if (currentMillis - previousMillis >= 1000) {
        previousMillis = currentMillis;
        ledState = !ledState;
        digitalWrite(LED_PIN, ledState);
      }
      break;
      
    case 3:
      // Mode 3 : Clignotement rapide (200ms)
      if (currentMillis - previousMillis >= 200) {
        previousMillis = currentMillis;
        ledState = !ledState;
        digitalWrite(LED_PIN, ledState);
      }
      break;
  }
}

// API : GET /api/mode - Retourne le mode actuel
void handleGetMode() {
  String json = "{\"mode\":" + String(modeActuel) + "}";
  server.send(200, "application/json", json);
  Serial.println("API: Mode actuel demandé - Mode " + String(modeActuel));
}

// API : GET /api/mode/set1 - Définit le mode 1
void handleSetMode1() {
  setMode(1);
  server.send(200, "application/json", "{\"success\":true,\"mode\":1}");
}

// API : GET /api/mode/set2 - Définit le mode 2
void handleSetMode2() {
  setMode(2);
  server.send(200, "application/json", "{\"success\":true,\"mode\":2}");
}

// API : GET /api/mode/set3 - Définit le mode 3
void handleSetMode3() {
  setMode(3);
  server.send(200, "application/json", "{\"success\":true,\"mode\":3}");
}

// API : GET /api/reboot - Redémarre l'ESP32
void handleReboot() {
  server.send(200, "application/json", "{\"success\":true,\"message\":\"Redémarrage en cours...\"}");
  Serial.println("API: Redémarrage demandé");
  delay(1000);
  ESP.restart();
}

// Fonction pour changer et sauvegarder le mode
void setMode(int nouveauMode) {
  modeActuel = nouveauMode;
  previousMillis = 0; // Reset timer pour clignotement immédiat
  
  preferences.begin("config", false);
  preferences.putInt("mode", modeActuel);
  preferences.end();
  
  Serial.print("Mode changé et sauvegardé : ");
  Serial.println(modeActuel);
}
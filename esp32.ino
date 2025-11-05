// -------------------- lIBRERÍAS --------------------
#include <WiFi.h>
#include <HTTPClient.h>
#include <LiquidCrystal_I2C.h>
#include <OneWire.h>
#include <DallasTemperature.h>
#include <math.h>  // Para log10 y pow

// -------------------- CONFIGURACIÓN DE RED Y SERVIDOR --------------------
const char* ssid = "Caro";
const char* password = "carol1234";
const char* host = "172.20.10.2";
const int port = 5000;
const char* endpoint = "/api/lecturas";

// -------------------- lCD --------------------
int lcdColumns = 20;
int lcdRows = 4;
LiquidCrystal_I2C lcd(0x27, lcdColumns, lcdRows);

// -------------------- SENSORES --------------------

// DS18B20
OneWire oneWireTemp(4);
DallasTemperature sensorTemp(&oneWireTemp);

// MQ-4
const int MQ4_PIN = 34;
const float Rl_VAlUE = 1000.0;    // ohmios
const float V_REF = 3.3;       // Voltaje de referencia ESP32
float Ro = 0.733;              // Ro calibrado en aire limpio
const int UMBRAl_AlARMA = 1500;
const float CH4_X_REF = 2.301030;  // log10(200 ppm)
const float CH4_Y_REF = 0.255273;  // log10(1.8 Rs/Ro)
const float CH4_CURVA = -0.360112; // Pendiente (m)

// Transductor de presión
const int PRESSURE_PIN = 35;
const float PRES_MAX_MPA = 1.2;
const float V_OUT_MIN_3V3 = 0.33;
const float V_OUT_MAX_3V3 = 2.97;
const float ADC_RESOlUTION = 4095.0;

// -------------------- FUNCIONES AUXIlIARES --------------------

// Convertir ADC → Voltaje
float analogToVoltage(int adcValue) {
  return adcValue * (V_REF / ADC_RESOlUTION);
}

// leer ppm metano usando curva logarítmica aproximada
float readMethanePpm() {
  int adcValue = analogRead(MQ4_PIN);
  float voltage = analogToVoltage(adcValue);

  float Vcc_Calc = V_REF;

  float rs = Rl_VAlUE * (Vcc_Calc - voltage) / voltage;
  float ratio = rs / Ro;
  float log10_ratio = log10(ratio);
  float log10_ppm = (log10_ratio - CH4_Y_REF) / CH4_CURVA + CH4_X_REF;

  float ppm = pow(10, log10_ppm);

  return ppm;
}

// Conexión Wi-Fi
void connectToWiFi() {
    lcd.setCursor(0, 0);
    lcd.print("Conectando WiFi…");
    Serial.print("Conectando a ");
    Serial.println(ssid);

    WiFi.begin(ssid, password);
    int attempts = 0;
    while (WiFi.status() != WL_CONNECTED) {
        delay(500);
        Serial.print(".");
        attempts++;
        if (attempts > 20) {
            Serial.println("\nFallo la conexión. Reiniciando…");
            lcd.clear();
            lcd.print("ERROR WIFI!");
            delay(5000);
            ESP.restart();
        }
    }

    Serial.println("\nWiFi conectado");
    Serial.print("IP: ");
    Serial.println(WiFi.localIP());

    lcd.clear();
    lcd.setCursor(0, 0);
    lcd.print("WiFi OK!");
    lcd.setCursor(0, 1);
    lcd.print("IP: ");
    lcd.print(WiFi.localIP());
    delay(2000);
}

// Enviar datos a API Flask
void sendDataToAPI(int sensorId, float value, const char* obs) {
    if (WiFi.status() == WL_CONNECTED) {
        HTTPClient http;
        String url = "http://" + String(host) + ":" + String(port) + String(endpoint);

        http.begin(url.c_str());
        http.addHeader("Content-Type", "application/json");

        String payload = "{\"sensor_id\":\"" + String(sensorId) +
                         "\",\"valor\":" + String(value, 3) +
                         ",\"observaciones\":\"" + obs + "\"}";

        Serial.print("Enviando [");
        Serial.print(sensorId);
        Serial.print("]: ");
        Serial.println(payload);

        int httpResponseCode = http.POST(payload);
        if (httpResponseCode > 0) {
            Serial.print("Codigo HTTP: ");
            Serial.println(httpResponseCode);
        } else {
            Serial.print("Error en POST: ");
            Serial.println(httpResponseCode);
        }
        http.end();
    } else {
        Serial.println("WiFi desconectado. Reintentando…");
        connectToWiFi();
    }
}

// -------------------- SETUP --------------------
void setup() {
    lcd.init();
    lcd.backlight();
    Serial.begin(9600);

    connectToWiFi();

    sensorTemp.begin();
    pinMode(MQ4_PIN, INPUT);
    pinMode(PRESSURE_PIN, INPUT);

    lcd.clear();
}

// -------------------- lOOP PRINCIPAl --------------------
void loop() {
    // ---------- lectura DS18B20 ----------
    sensorTemp.requestTemperatures();
    float tempC = sensorTemp.getTempCByIndex(0);

    // ---------- lectura MQ-4 (ppm) ----------
    float mq4_ppm = readMethanePpm();
    String obsGas = (mq4_ppm > 1000) ? "Alarma de Gas" : "Normal"; // ajusta umbral según necesidad

    // ---------- lectura transductor presión ----------
    int lecturaPresion = analogRead(PRESSURE_PIN);
    float voltaje = analogToVoltage(lecturaPresion);
    float presionMPa = (voltaje - V_OUT_MIN_3V3) * (PRES_MAX_MPA / (V_OUT_MAX_3V3 - V_OUT_MIN_3V3));
    if (presionMPa < 0) presionMPa = 0.0;
    float presionKPa = presionMPa * 1000.0;

    // ---------- Envío a API ----------
    sendDataToAPI(1, mq4_ppm, obsGas.c_str());
    sendDataToAPI(2, tempC, "Temperatura externa");
    sendDataToAPI(3, presionKPa, "Presion en kPa");



    // ---------- Mostrar en lCD ----------
    lcd.clear();
    lcd.setCursor(0, 0);
    lcd.print("Temp: ");
    lcd.print(String(tempC, 1));
    lcd.print(" C");

    lcd.setCursor(0, 1);
    lcd.print("Pres: ");
    lcd.print(String(presionKPa, 1));
    lcd.print(" kPa");

    lcd.setCursor(0, 2);
    lcd.print("Gas: ");
    lcd.print(String(mq4_ppm, 0));
    lcd.print(" ppm");

    lcd.setCursor(0, 3);
    lcd.print("Estado: ");
    lcd.print(obsGas);

    // ---------- Serial ----------
    Serial.println("----- lECTURAS -----");
    Serial.print("Temperatura: "); Serial.print(tempC); Serial.println(" °C");
    Serial.print("Presion: "); Serial.print(presionKPa); Serial.println(" kPa");
    Serial.print("Gas: "); Serial.print(mq4_ppm); Serial.println(" ppm");
    Serial.print("Estado: "); Serial.println(obsGas);
    Serial.println("--------------------\n");

    delay(5000);
}

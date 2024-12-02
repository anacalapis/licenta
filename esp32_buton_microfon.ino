#include <BluetoothSerial.h>

BluetoothSerial SerialBT; // Obiect pentru comunicare Bluetooth

#define BUTTON_PIN 23 // Pinul la care este conectat butonul

void setup() {
  pinMode(BUTTON_PIN, INPUT_PULLUP); // Configurare buton cu pull-up intern
  Serial.begin(115200); // Inițializare Serial Monitor
  SerialBT.begin("ESP32_Button_Sender"); // Numele dispozitivului Bluetooth
  Serial.println("Aștept comenzi prin Bluetooth...");
}

void loop() {
  // Citește starea butonului
  int buttonState = digitalRead(BUTTON_PIN);

  // Trimite starea butonului la Raspberry Pi prin Bluetooth
  if (buttonState == LOW) {
    SerialBT.println(1);
    Serial.println("Butonul este APASAT");
  } else {
    SerialBT.println(0);
    Serial.println("Butonul este NEAPASAT");
  }

  delay(500); // Trimite starea de 2 ori pe secundă
}

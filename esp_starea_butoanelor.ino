#include <BluetoothSerial.h>

BluetoothSerial SerialBT; // Obiect pentru comunicare Bluetooth

#define PAUSE_BUTTON 23 // Pinul la care este conectat butonul
#define RESUME_BUTTON 22

void setup() {
  pinMode(PAUSE_BUTTON, INPUT_PULLUP); // Configurare buton cu pull-up intern
  pinMode(RESUME_BUTTON, INPUT_PULLUP);
  Serial.begin(9600); // Inițializare Serial Monitor
  SerialBT.begin("ESP32_Button_Sender"); // Numele dispozitivului Bluetooth
}

void loop() {
  // Citește starea butonului
  int pause_button = digitalRead(PAUSE_BUTTON);
  int resume_button = digitalRead(RESUME_BUTTON);

  // Trimite starea butonului la Raspberry Pi prin Bluetooth
  if (pause_button == LOW) {
    SerialBT.print(1);
  } 
  if (resume_button == LOW) {
    SerialBT.print(0);
  } 

  delay(200);
}
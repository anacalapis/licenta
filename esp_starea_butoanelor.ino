#include <BluetoothSerial.h>

BluetoothSerial SerialBT; // Obiect pentru comunicare Bluetooth

#define MIC_PIN 23 // Pinul la care este conectat microfonul
#define RESUME_BUTTON 22


int flag=0;
void setup() {
  pinMode(MIC_PIN, INPUT); // Configurare buton cu pull-up intern
  pinMode(RESUME_BUTTON, INPUT_PULLUP);
  Serial.begin(9600); // Inițializare Serial Monitor
  SerialBT.begin("ESP32_Button_Sender"); // Numele dispozitivului Bluetooth
}

void loop() {
  // Citește starea butonului
  int microphone = digitalRead(MIC_PIN);
  int resume_button = digitalRead(RESUME_BUTTON);

  // Trimite starea butonului la Raspberry Pi prin Bluetooth
  if (microphone == HIGH && flag==1) {
    SerialBT.print(1);
    flag=0;
  } 
  if (resume_button == LOW) {
    SerialBT.print(0);
    flag=1;
  } 

  delay(200);
}
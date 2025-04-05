#include <BluetoothSerial.h>

BluetoothSerial SerialBT; // Obiect pentru comunicare Bluetooth

#define MIC_PIN 23 // Pinul la care este conectat microfonul
#define RESUME_BUTTON 22
#define DELETE_POINTS 19


int flag=0;
void setup() {
  pinMode(MIC_PIN, INPUT); // Configurare buton cu pull-up intern
  pinMode(RESUME_BUTTON, INPUT_PULLUP);
  pinMode(DELETE_POINTS, INPUT_PULLUP);
  Serial.begin(9600); // Inițializare Serial Monitor
  SerialBT.begin("ESP32_Button_Sender"); // Numele dispozitivului Bluetooth
}

void loop() {
  // Citește starea butonului
  int microphone = digitalRead(MIC_PIN);
  int resume_button = digitalRead(RESUME_BUTTON);
  int delete_points = digitalRead(DELETE_POINTS);
  // Serial.print("albastru ");
  // Serial.println(resume_button);
  // Serial.print("rosu ");
  // Serial.println(delete_points);
  // Trimite starea butonului la Raspberry Pi prin Bluetooth
  // if (microphone == HIGH && flag==1) {
  //   SerialBT.print(1);
  //   flag=0;
  // } 
  // if (resume_button == LOW) {
  //   SerialBT.print(0);
  //   flag=1;
  // } 
  if(microphone == HIGH)
  {
    SerialBT.print("1");
  }
  else 
  {
    if (resume_button == LOW) 
    {
      SerialBT.print("0");
    }
    else
    {
      if(delete_points == LOW)
      {
        SerialBT.print("4");
      }
      else
      {
        SerialBT.print("2");
      }
    }
      
  }

  delay(50);
}
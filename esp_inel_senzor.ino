#include <BluetoothSerial.h>
#define SENSOR1_PIN 22 
#define SENSOR2_PIN 23 
#define SENSOR3_PIN 18

BluetoothSerial SerialBT;

String command = "";
bool flag;

unsigned long currentMillis = 0;
unsigned long previousMillis = 0;

int score = 0;
int sensor1State= 1;
int sensor2State= 1;
int sensor3State= 1;
void setup() {
  pinMode(SENSOR1_PIN, INPUT_PULLUP); 
  pinMode(SENSOR2_PIN, INPUT_PULLUP); 
  pinMode(SENSOR3_PIN, INPUT_PULLUP);
  Serial.begin(9600);    
  SerialBT.begin("ESP_Inel_Device"); 
}

void loop() 
{
  sensor1State = digitalRead(SENSOR1_PIN); 
  sensor3State = digitalRead(SENSOR3_PIN);
  while (SerialBT.available()) {
    char c = SerialBT.read();  // Citim câte un caracter
    if (c == '\n') {  // Dacă am primit un caracter de sfârșit de linie, procesăm comanda
      command.trim();  // Eliminăm orice spațiu sau \n la începutul și sfârșitul comenzii
      if (command.equals("S")) {
        flag = true;
        Serial.println("Received S");
      }
      else if (command.equals("P")) {
        flag = false;
        Serial.println("Received P");
      }
      command = "";  // Resetăm comanda pentru următoarea citire
    } else {
      command += c;  // Adăugăm caracterul la comanda curentă
    }
  }
  if ((sensor1State == 0 || sensor3State==0) && flag)
  {
    previousMillis = millis();
    currentMillis = millis();
    while(currentMillis - previousMillis < 300)
    {
      sensor2State = digitalRead(SENSOR2_PIN);
      if(sensor2State == 0)
      { 
        score++;
        break;
      }
      currentMillis = millis();
    }
  }
  // Serial.print("senz1 ");
  //Serial.print(sensor1State);
  //Serial.print("senz2 ");
  //Serial.println(sensor2State);
  // Serial.print("senz3 ");
  //Serial.println(sensor3State);
  //Serial.print("        score ");
  SerialBT.printf("%d", score);
  delay(50); 
}

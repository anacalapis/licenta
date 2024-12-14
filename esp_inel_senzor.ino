#include <BluetoothSerial.h>
#define SENSOR1_PIN 22 
#define SENSOR2_PIN 23 
#define SENSOR3_PIN 18

BluetoothSerial SerialBT;

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

void loop() {
  sensor1State = digitalRead(SENSOR1_PIN); 
  sensor3State = digitalRead(SENSOR3_PIN); 
  if (sensor1State == 0 || sensor3State==0)
  {
    delay(50);
    sensor2State = digitalRead(SENSOR2_PIN);
    if(sensor2State == 0)
    { 
      score++;
    }
    //Serial.print(sensor2State);
  }
  // Serial.print("senz1 ");
  //Serial.print(sensor1State);
  // Serial.print("senz2 ");
  // Serial.print(sensor2State);
  // Serial.print("senz3 ");
  //Serial.println(sensor3State);
  //Serial.print("        score ");
  SerialBT.print(score);
  delay(50); 
}

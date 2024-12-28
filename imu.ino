#include <Wire.h>
#include <Adafruit_MPU6050.h>
#include <Adafruit_Sensor.h>

Adafruit_MPU6050 imuu;

void setup() {
  Serial.begin(9600); 
  imuu.begin();
}

void loop() {
  sensors_event_t acc, giro, temp;
  imuu.getEvent(&acc, &giro, &temp);
  // a este acceleratie
  // g este giroscop
  // temp e temperatura interna - fct getEvent are nevoie de 3 param 

  //Serial.print("Acceleratie: ");
  Serial.print("Acc_X:");Serial.println(acc.acceleration.x);
  Serial.print("Acc_Y:");Serial.println(acc.acceleration.y);
  Serial.print("Acc_Z:");Serial.println(acc.acceleration.z);

 // Serial.print("  Giroscop: ");
  Serial.print("Giro_X:");Serial.println(giro.gyro.x);
  Serial.print("Giro_Y:");Serial.println(giro.gyro.y);
  Serial.print("Giro_Z:");Serial.println(giro.gyro.z);

  delay(500); 
}


#include <BluetoothSerial.h>

BluetoothSerial SerialBT;

void setup() {
  Serial.begin(115200);
  if (!SerialBT.begin("ESP_IMU")) {
    Serial.println("Bluetooth nu s-a pornit!");
    while (1);  // Blochează programul dacă Bluetooth nu pornește
  }
  Serial.println("Bluetooth pornit!");
}

void loop() {
  // if (SerialBT.connected()) {
  //   SerialBT.println("Salut de la ESP32!");
  // } else {
  //   Serial.println("Astept conexiune Bluetooth...");
  // }
  SerialBT.println("1");
  delay(1000);
}

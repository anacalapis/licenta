#include <Wire.h>

void setup() {
  Wire.begin();               // Inițializează bus-ul I2C
  Serial.begin(9600);         // Inițializează comunicarea serială
  while (!Serial);            // Așteaptă deschiderea monitorului serial (pentru plăcile care suportă această funcție)
  Serial.println("I2C Scanner - Caut dispozitive...");
}

void loop() {
  byte error, address;
  int devicesFound = 0;

  Serial.println("Scanare in curs...");
  
  for (address = 1; address < 127; address++) {
    Wire.beginTransmission(address);
    error = Wire.endTransmission();

    if (error == 0) {
      Serial.print("Dispozitiv gasit la adresa 0x");
      if (address < 16) Serial.print("0");
      Serial.print(address, HEX);
      Serial.println(" !");
      devicesFound++;
    } else if (error == 4) {
      Serial.print("Eroare necunoscuta la adresa 0x");
      if (address < 16) Serial.print("0");
      Serial.println(address, HEX);
    }
  }

  if (devicesFound == 0) {
    Serial.println("Nu s-au gasit dispozitive I2C.");
  } else {
    Serial.print("Numar total de dispozitive gasite: ");
    Serial.println(devicesFound);
  }

  delay(5000); // Așteaptă 5 secunde înainte de a scana din nou
}

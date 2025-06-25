#include "esp_bt_device.h"                                                  //pentru a folosi funcții necesare la obținerea adresei MAC
#include <BluetoothSerial.h>                                                //pentru a găsi adresa MAC destrinată comunicării prin Bluetooth
BluetoothSerial SerialBT;

void adresa_MAC() 
{
  const uint8_t* adresa_mac = esp_bt_dev_get_address();                     //se obține adresa MAC a dispozitivului
  Serial.print("Adresa MAC: ");
  for (int i = 0; i < 6; i++)                                               //pentru ca rezultatul a celor 6 bytes nu este formatat, urmează să fie afișat corespunzător
  {
    Serial.print(adresa_mac[i], HEX);                                       //fiecare byte va fi afișat în format zecimal dacă nu se specifică prin intermediul parametrului HEX că se dorește
    if (i < 5)                                                              //să fie vizualizat în format hexazecimal
    {
      Serial.print(":");                                                    //pentru a respecta formatul corect al unei adresa MAC, se pun : între fiecare pereche de bytes
    }
  }
  Serial.println();
}

void setup() {
  Serial.begin(115200);                                                     //se setează comunicarea serială la 9600 biți pe secundă
  delay(1000);                                                              //se adaugă o întârziere
  SerialBT.begin("ESP32");                                                  //se inițializează stivă Bluetooth pentru a putea apela funcția ce urmează 
  adresa_MAC();                                                             //se apelează, o singură dată, funcția pentru afișarea adresei MAC
}

void loop() { }                                                             //scopul acestui program este pentru a obține adresa MAC a fiecărui dispozitiv

//VERSIUNEA FINALA
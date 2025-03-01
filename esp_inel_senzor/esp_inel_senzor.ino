#include <BluetoothSerial.h>
#define SENSOR1_PIN 22 
#define SENSOR2_PIN 23 
#define SENSOR3_PIN 18

BluetoothSerial SerialBT;

String command = "";
int distanta =0;
bool flag;

unsigned long currentMillis = 0;
unsigned long previousMillis = 0;

int score = 0;
int sensor1State= 1;
int sensor2State= 1;
int sensor3State= 1;

char comanda;

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
      //Serial.println(command[0]);
      if(command[0]=='3')
      {
        String sir = String(command.c_str() +1); 
        if (sir.equals("S")) 
        {
          flag = true;
          comanda = 'S';
          Serial.println("Received S");
        }
        if (sir.equals("P")) 
        {
          flag = false;
          //comanda = 'P';
          Serial.println("Received P");
        }
        if (sir.equals("L")) 
        {
          flag = true;
          comanda = 'L';
          Serial.println("Received L");
        }
      }
      if(command[0]=='4')
      {
        String d = String(command.c_str() +1);
        distanta = d.toInt();
        //Serial.println(distanta);

      }
      
      command = "";  // Resetăm comanda pentru următoarea citire
    } 
    else 
    {
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
        if(comanda == 'L')
        {
          score++;
          SerialBT.printf("%d", score);
          break;
        }
        if(comanda == 'S')
        {
          if(distanta <= 50)
          {
            score = score+2;
          }
          else
          {
            score = score+3;
          }
          //score=score+2;
          SerialBT.printf("%d", score);
          break;
        }
        // score++;
        //break;
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

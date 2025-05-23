#include <BluetoothSerial.h>
#define SENSOR1_PIN 22 
#define SENSOR2_PIN 23 
#define SENSOR3_PIN 18

#define TREI_PUNCTE 35
BluetoothSerial SerialBT;

String command = "";
float distanta =0;
bool flag;
int ultima_aruncare;

unsigned long currentMillis = 0;
unsigned long previousMillis = 0;

int score;
int sensor1State= 1;
int sensor2State= 1;
int sensor3State= 1;

int scor_delete=0;
char comanda;
void setup() {
  pinMode(SENSOR1_PIN, INPUT_PULLUP); 
  pinMode(SENSOR2_PIN, INPUT_PULLUP); 
  pinMode(SENSOR3_PIN, INPUT_PULLUP);
  Serial.begin(9600);    
  SerialBT.begin("ESP_Inel_Device"); 
  score=0;
  ultima_aruncare =0;
}

void loop() 
{
  if (command.equals("RESET")) 
  {
  score = 0;
  ultima_aruncare = 0;
  command = ""; 
}
  sensor1State = digitalRead(SENSOR1_PIN); 
  sensor3State = digitalRead(SENSOR3_PIN);
  while (SerialBT.available()) {
    char c = SerialBT.read();  // Citim câte un caracter
    if (c == '\n') {  // Dacă am primit un caracter de sfârșit de linie, procesăm comanda
      command.trim();  // Eliminăm orice spațiu sau \n la începutul și sfârșitul comenzii
      //Serial.println(command);
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
        if (sir.equals("A")) 
        {
          comanda = 'A';
          Serial.println("Received A");
        }
        if (sir.equals("a")) 
        {
          comanda = 'a';
          flag = true;
          Serial.println("Received a");
        }
        String subsir = command.substring(1);
        if(subsir.startsWith("H"))
        {
          int start = subsir.indexOf('-');
          String val = subsir.substring(start+1);
          score = val.toInt();
          //pauza_mare=true;
          Serial.println(score);
        }
      }
      if(command[0]=='4')
      {
        String d = String(command.c_str() +1);
        String dist;
        int indexA = d.indexOf('A');
        int indexB = d.indexOf('B');
        dist = d.substring(indexA+1, indexB);
        distanta = dist.toFloat();
        Serial.println(distanta);
      }
      
      command = "";  // Resetăm comanda pentru următoarea citire
    } 
    else 
    {
      command += c;  // Adăugăm caracterul la comanda curentă
    }
  }
  if((sensor1State == 0 || sensor3State==0) && flag)
  {
    previousMillis = millis();
    currentMillis = millis();
    while(currentMillis - previousMillis < 700)
    {
      sensor2State = digitalRead(SENSOR2_PIN);
      if(sensor2State == 0)
      { 
        if(comanda == 'L' ||  comanda == 'a')
        {
          score++;
          ultima_aruncare = 1;
          SerialBT.printf("%d", score);
          break;
        }
        if(comanda == 'S')
        {
          Serial.print("luat");
          Serial.println(distanta);
          if(distanta < TREI_PUNCTE)
          {
            score = score+2;
            ultima_aruncare = 2;
          }
          else
          {
            score = score+3;
            ultima_aruncare = 3;
          }
          SerialBT.printf("%d", score);
          break;
        }
      }
      currentMillis = millis();
    }
  }
 if(comanda =='A' && (score != scor_delete))
  {
    score = score - ultima_aruncare;
    scor_delete = score;
    ultima_aruncare = 0;
  }
  SerialBT.printf("%d", score);
  delay(50); 
}

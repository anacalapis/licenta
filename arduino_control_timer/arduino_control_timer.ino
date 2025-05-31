#include <Wire.h>
#include <LiquidCrystal_I2C.h>

#define NR_SEC_SFERT 60   //aici se pune cat dorim sa tina un sfert in secunde
#define NR_SEC_PAUZA_MICA 3 //aici se pune cat dorim sa tina o pauza mica in secunde
#define NR_SEC_PAUZA_MARE 5 //aici se pune cat dorim sa tina o pauza mare in secunde
#define NR_SEC_OVERTIME 10


LiquidCrystal_I2C lcd(0x27, 16, 2); 

// Variabile de stare
volatile bool isPaused = false; // Flag pentru pauză
unsigned long previousMillis = 0; // Timpul anterior pentru actualizarea countdown-ului
const unsigned long interval = 1000; // Intervalul pentru scăderea timpului (1 secundă)

int timeIntervalCount =0; //numara in ce interval ne aflam, par este sfert, impar pauza
int nr_sfert=1;
int nr_overtime =0;
bool overtime = false;

int countDownTime = NR_SEC_SFERT; //in secunde
int timeQuarter =NR_SEC_SFERT ;
int timeOvertime = NR_SEC_OVERTIME;
int timeSmallBreak = NR_SEC_PAUZA_MICA;
int timeHalfBreak = NR_SEC_PAUZA_MARE; 
String command;

bool buton_stergere =false;

int scor1=0, scor2=0;
int curent_scor1 =0, anterior_scor1=0;
int curent_scor2 =0, anterior_scor2=0;

int scor_ec1=0, scor_ec2=0;
bool se_poate=false;
int ultim_scor_marcat; //daca este 1, semnifica ca ultimul cos a fost marcat de echipa A
                        //daca este 2, semnifica ca ultimul cos a fost marcat de echipa B
void setup() 
{
  Serial.begin(9600);
  lcd.init();
  lcd.backlight();
  lcd.setCursor(0, 0);
  lcd.print("  Start meci!");
  delay(500); 
  lcd.clear();
}

void loop() {
   
  displayQuarter();
  if (countDownTime <= 0) 
  {
    timeIntervalCount ++;
    switch(timeIntervalCount)
    {
      case 1:   //pauza dintre primul si al doilea sfert
      case 5:   //pauza dintre al treiea si al patrulea sfert
      {
        countDownTime = NR_SEC_PAUZA_MICA;
        displayPause();
        break;
      }
      case 2:   //sfertul 2
      case 4:   //sfertul 3
      case 6:   //sfertul 4
      {
        countDownTime = timeQuarter;
        nr_sfert++;
        displayQuarter();
        break;
      }
      case 3: 
      {
        countDownTime = NR_SEC_PAUZA_MARE;
        displayPause();
        Serial.print("H*");
        Serial.print(curent_scor1);
        Serial.print("-");
        Serial.println(curent_scor2);
        break;
      }
      case 7:   //situatia de overtime
      {
        while(curent_scor1 == curent_scor2)
        {
          overtime = true;
          countDownTime = NR_SEC_PAUZA_MICA;
          displayPause();

          countDownTime = timeOvertime;
          nr_overtime++;
          displayQuarter();
          
        }
        break;
      }
      case 8:   //finalul meciului
      {
        lcd.setCursor(0, 0);
        lcd.print(" Final de meci!");
        lcd.setCursor(0, 1);
        lcd.print("EchA ");
        lcd.print(curent_scor2);
        lcd.print("-");
        lcd.print(curent_scor1);
        lcd.print(" EchB");
        while(true);
      }
    }
  }
}

// Funcție pentru actualizarea afișajului LCD
void updateDisplay(int sfert) 
{
  int minutes = countDownTime / 60;
  int secunde = countDownTime % 60;
  lcd.clear();
  lcd.setCursor(0, 0);
  if(sfert == 0)
  {
    lcd.print("Pauza:  ");
  }
  else
  {
    if(overtime)
    {
      lcd.print("OT ");
      lcd.print(sfert);
    }
    else
    {
      lcd.print("Sf ");
      lcd.print(sfert);
    }
    lcd.print(":   ");
  }
  //lcd.setCursor(0, 1);

  if (minutes < 10) 
  {
    lcd.print("0");
  }
  lcd.print(minutes);
  lcd.print(":");
  if (secunde < 10) 
  {
    lcd.print("0");
  }
  lcd.print(secunde);
  displayScor();
}

void displayQuarter()
{
  //Serial.println("S");
  if(countDownTime == NR_SEC_SFERT || countDownTime == NR_SEC_OVERTIME)
  {
    int minutes, secunde;
    if(overtime)
    {
      minutes = timeOvertime / 60;
      secunde = timeOvertime % 60;
    }
    else
    {
      minutes = timeQuarter / 60;
      secunde = timeQuarter % 60;
    }
    lcd.clear();
    lcd.setCursor(0, 0);
    if (overtime)
    {
      lcd.print("OT ");
      lcd.print(nr_overtime);
    }
    else
    {
      lcd.print("Sf ");
      lcd.print(nr_sfert);
    }
    lcd.print("    ");
    if(minutes<10)
    {
      lcd.print("0");
    }
    lcd.print(minutes);
    lcd.print(":");
    if(secunde<10)
    {
      lcd.print("0");
    }
    lcd.print(secunde);
    if(nr_sfert == 3)   //pentru a nu imi afisa in perioada dintre pauza mare si inceputul sfertului 3, scorul inversat
    {
      nr_sfert--;     //scad ca sa creada ca inca nu se modifica ordinea
      displayScor();
      nr_sfert++;     //revin inapoi ca sa nu imi distrug afisajul pe mai departe
    }
    else
    {
      displayScor();
    }
    //displayScor();
   
    command = Serial.readStringUntil('\n');
    command.trim();
    buton_stergere=false;
    while(!command.equals("00"))    // e inceput de sfert si se asteapta ca timpul sa porneasca
    {
      command = Serial.readStringUntil('\n');
      command.trim();
      if (command.equals("02") && buton_stergere ==false) 
      {
        if(ultim_scor_marcat == 1)
        {
          Serial.println("A");
          ultim_scor_marcat = 1;
        }
        if(ultim_scor_marcat == 2 )
        {
          Serial.println("B");
          ultim_scor_marcat =2;
        }
        delay(100); 
        displayScor();
        buton_stergere=true;
      }
      // displayScor();
    }
    buton_stergere=true;
  }
  while(countDownTime !=0)  //suntem in timpul sfertului
  {
    command = Serial.readStringUntil('\n');
    command.trim();
    //if (digitalRead(pauseButton) == LOW)
    if(command.equals("01"))
    {
      Serial.println("L");
      isPaused = true; // Oprește timpul 
      delay(100);
    }
    displayScor();
    
    if (command.equals("00")) 
    {
      Serial.println("S");
      isPaused = false; // Reia timpul
      buton_stergere = false;
      delay(100); 
    }
    if (!isPaused)  //curge timpul in timpul sfertului
    {
      unsigned long currentMillis = millis();
      if (currentMillis - previousMillis >= interval && countDownTime > 0)
      {
        previousMillis = currentMillis; // Actualizează timpul anterior
        countDownTime--; // Scade timpul rămas
        if(overtime)
        {
          updateDisplay(nr_overtime); 
        }
        else
        {
          updateDisplay(nr_sfert); 
        }
        
      }
    }
    else  //suntem in perioada aruncarilor libere
    {
      if (command.equals("02")) 
      {
        if(ultim_scor_marcat == 1)
        {
          Serial.println("A");
          ultim_scor_marcat = 1;
        }
        if(ultim_scor_marcat == 2)
        {
          Serial.println("B");
          ultim_scor_marcat =2;
        }
        delay(100); 
        displayScor();
        if(ultim_scor_marcat == 1)
        {
          Serial.println("a");
        }
        else  //if(ultim_scor_marcat == 2) 
        {
          Serial.println("b");
        }
        //cat timp nu se mai inscrie nimic, de nicio echipa, se sta aici
        int scor_aici1= curent_scor1;
        int scor_aici2=curent_scor2;
        while (scor_aici1== curent_scor1 && scor_aici2==curent_scor2)
        {
          command = Serial.readStringUntil('\n');
          command.trim();
          if (command.equals("00")) 
          {
            Serial.println("S");
            isPaused = false; // Reia timpul
            buton_stergere = false;
            delay(100); 
            break;
          }
          if(command.startsWith("1"))
          {
            curent_scor1 =atoi(command.substring(1).c_str());
          }
          if(command.startsWith("2"))
          {
            curent_scor2 =atoi(command.substring(1).c_str());
          }
        }
      }
    }
    //displayScor();
  }
}

void displayPause()
{
  Serial.println("P");
  int minutes = countDownTime / 60;
  int secunde = countDownTime % 60;
  if(countDownTime==NR_SEC_PAUZA_MICA || countDownTime==NR_SEC_PAUZA_MARE)
  {
    lcd.clear();
    lcd.setCursor(0, 0);
    lcd.print("Pauza   ");
    if(minutes<10)
    {
      lcd.print("0");
    }
    lcd.print(minutes);
    lcd.print(":");
    if(secunde<10)
    {
      lcd.print("0");
    }
    lcd.print(secunde);
    displayScor();

  }
  buton_stergere=false;
  while(countDownTime!=0)
  {
    unsigned long currentMillis = millis();
    command = Serial.readStringUntil('\n');
    command.trim();
    if (command.equals("02") && buton_stergere ==false) 
    {
      //Serial.println("D");
      if(ultim_scor_marcat == 1)
        {
          Serial.println("A");
          ultim_scor_marcat =1;
        }
      else //(ultim_scor_marcat == 2)
        {
          Serial.println("B");
          ultim_scor_marcat =2;
        }
      //isPaused = false; // Reia timpul
      delay(100); 
      displayScor();
      buton_stergere=true;
    }
    displayScor();
    if (currentMillis - previousMillis >= interval && countDownTime > 0) 
    {
      previousMillis = currentMillis; // Actualizează timpul anterior
      countDownTime--; // Scade timpul rămas
      updateDisplay(0);
    }
  }
}

void displayScor()
{
  command = Serial.readStringUntil('\n');
  command.trim();
  if(command.startsWith("1"))
    {
      int stop= command.indexOf('*');
      String  scor_nr= command.substring(1, stop);
      curent_scor1 =scor_nr.toInt();
      //delay(100);
      if(anterior_scor1 != curent_scor1) 
      {
        ultim_scor_marcat =1;
      }
      anterior_scor1=curent_scor1;
    }
    if(command.startsWith("2"))
    {
      int stop= command.indexOf('/');
      String  scor_nr= command.substring(1, stop);
      curent_scor2 =scor_nr.toInt();
      if(anterior_scor2 != curent_scor2)      //dif sa fie<=3
      {
        ultim_scor_marcat =2;
      }
      anterior_scor2=curent_scor2;
    }  
  lcd.setCursor(0, 1);
  lcd.print("EchA ");
  if(nr_sfert<3)
  {
    if(curent_scor1<10)
    {
      lcd.print(" ");
    }
    lcd.print(curent_scor1);
    lcd.print("-");
    lcd.print(curent_scor2);
    if(curent_scor2<10)
    {
      lcd.print("  ");
    }
    else
    {
      lcd.print(" ");
    }  
  }
 else
 {
    if(curent_scor2<10)
    {
      lcd.print(" ");
    }
    lcd.print(curent_scor2);
    lcd.print("-");
    lcd.print(curent_scor1);
    if(curent_scor1<10)
    {
      lcd.print("  ");
    }
    else
    {
      lcd.print(" ");
    }
 }
  lcd.print(" EchB");
}

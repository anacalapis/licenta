#include <Wire.h>
#include <LiquidCrystal_I2C.h>


LiquidCrystal_I2C lcd(0x27, 16, 2); 

// Variabile de stare
volatile bool isPaused = false; // Flag pentru pauză
unsigned long previousMillis = 0; // Timpul anterior pentru actualizarea countdown-ului
const unsigned long interval = 1000; // Intervalul pentru scăderea timpului (1 secundă)

int timeIntervalCount =0; //numara in ce interval ne aflam, par este sfert, impar pauza
int nr_sfert=1;

int countDownTime = 10; //in secunde
int timeQuarter =10;
int timeSmallBreak =5;
int timeHalfBreak = 7; 
String command;

void setup() 
{
  Serial.begin(9600);
  lcd.init();
  lcd.backlight();
  lcd.setCursor(0, 0);
  lcd.print("Start meci!");
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
      case 1:
      case 5: 
      {
        countDownTime = timeSmallBreak;
        displayPause();
        break;
      }
      case 2:
      case 4:
      case 6: 
      {
        countDownTime = timeQuarter;
        nr_sfert++;
        displayQuarter();
        break;
      }
      case 3: 
      {
        countDownTime = timeHalfBreak;
        displayPause();
        break;
      }
      case 7:
      {
        while(true);
      }
    }
  }
}

// Funcție pentru actualizarea afișajului LCD
void updateDisplay(int sfert) 
{
  int minutes = countDownTime / 60;
  int seconds = countDownTime % 60; 

  lcd.clear();
  lcd.setCursor(0, 0);
  if(sfert == 0)
  {
    lcd.print("Pauza:");
  }
  else
  {
    lcd.print("Sfertul ");
    lcd.print(sfert);
    lcd.print(":");
  }
  lcd.setCursor(0, 1);

  if (minutes < 10) 
  {
    lcd.print("0");
  }
  lcd.print(minutes);
  lcd.print(":");
  if (seconds < 10) 
  {
    lcd.print("0");
  }
  lcd.print(seconds);
}

void displayQuarter()
{
  if(countDownTime==10)
  {
    lcd.clear();
    lcd.setCursor(0, 0);
    lcd.print("Sfertul ");
    lcd.print(nr_sfert);
    lcd.print(":");
    lcd.setCursor(0, 1);
    lcd.print("00:");
    lcd.print(timeQuarter);
    command = Serial.readStringUntil('\n');
    command.trim();
    while(command.equals("") || command.equals("1"))
    {
      command = Serial.readStringUntil('\n');
      command.trim();
    }
  }
  while(countDownTime !=0)
  {
    command = Serial.readStringUntil('\n');
    command.trim();
    //if (digitalRead(pauseButton) == LOW)
    if(command.equals("1"))
    {
      isPaused = true; // Oprește timpul 
      delay(100);
    }

    if (command.equals("0")) 
    {
      isPaused = false; // Reia timpul
      delay(100); 
    }
    if (!isPaused) 
    {
      unsigned long currentMillis = millis();
      if (currentMillis - previousMillis >= interval && countDownTime > 0)
      {
        previousMillis = currentMillis; // Actualizează timpul anterior
        countDownTime--; // Scade timpul rămas
        updateDisplay(nr_sfert); 
      }
    }
  }
}

void displayPause()
{
  if(countDownTime==timeSmallBreak || countDownTime==timeHalfBreak)
  {
    lcd.clear();
    lcd.setCursor(0, 0);
    lcd.print("Pauza:");
    lcd.setCursor(0, 1);
    lcd.print("00:0");
    lcd.print(countDownTime);
  }
  while(countDownTime!=0)
  {
    unsigned long currentMillis = millis();
      if (currentMillis - previousMillis >= interval && countDownTime > 0) 
      {
        previousMillis = currentMillis; // Actualizează timpul anterior
        countDownTime--; // Scade timpul rămas
        updateDisplay(0);
      }
  }
}
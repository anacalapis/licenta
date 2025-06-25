#include <BluetoothSerial.h>                                //bibliotecă necesară pentru a se putea realiza comunicarea prin intermediul protocolului de comunicație Bluetooth

BluetoothSerial Com_Bluetooth;                              //obiectul folosit pentru comunicare datelor prin intermediul Bluetoothu-lui

#define PIN_MICROFON 23                                     //pinul digital la care este conectat microfonul
#define PIN_BUTON_START 22                                  //pinul digital la care este conectat butonul prin care se pornește cronometrul de joc
#define PIN_BUTON_STERGERE 19                               //pinul digital la care este conectat butonul care este responsabil de ștergerea ultimului coș

void setup()                                                //funcție ce se execută o singură dată, la începutul execuției programului, și este responsabilă de inițializări
{
  pinMode(PIN_MICROFON, INPUT);                             //configurează pinul digital al microfonului ca și pin de intrare
  pinMode(PIN_BUTON_START, INPUT_PULLUP);                   //configurează pinii digitali la care sunt conectate butoanele de pornire a timpului și cel de ștergere al ultimului coș 
  pinMode(PIN_BUTON_STERGERE, INPUT_PULLUP);                //ca fiind de intrare, la care se activează și rezistența internă de pull-up pentru ca pinii să se afle într-o stare definită
                                                            //și atunci când nu transmit semnale
  Com_Bluetooth.begin("ESP32_Modul_timp");                  //numele dispozitivului care va apărea pe Raspberry în momentul în care se realizează conexiunea 
}

void loop()                                                 //funcție ce se execută la infinit pentru a detecta semnalele necesare
{
  int microfon = digitalRead(PIN_MICROFON);                 //se citește starea microfonului dacă s-a depășit sau nu pragul setat prin intermediul potențiometrului
  int buton_start = digitalRead(PIN_BUTON_START);           //se citește starea butonului de start
  int buton_stergere = digitalRead(PIN_BUTON_STERGERE);     //se citește starea butonului de ștergere a ultimelor puncte marcate

  if(microfon == HIGH)                                      //dacă microfonul a înregistrat o valoare mai mare decât cea setată
  {
    Com_Bluetooth.print("1");                               //asta înseamnă că arbitrul a fluierat, deci se oprește timpul și se trimite mesajul aferent prin Bluetooth
  }
  else 
  {
    if (buton_start == LOW)                                 //dacă s-a apăsat butonul de start a timpului
    {
      Com_Bluetooth.print("0");                             //se trimite mesajul aferent pentru a porni timpul de joc
    }
    else
    {
      if(buton_stergere == LOW)                             //dacă s-a apăsat butonul de ștergere al ultimului coș 
      {
        Com_Bluetooth.print("2");                           //se trimite mesajul stabilit pentru a se acționa corespunzător
      }
    }   
  }
  delay(10);                                                //se introduce o întârziere de 10 milisecunde în care nu se întâmplă nimic, după care se reia de la început codul din funcția loop
}

//VERSIUNEA FINALA
#include <BluetoothSerial.h>    //biblioteca care este folosită pentru comunicarea prin Bluetooth
#define PIN_SENZOR1 22          //senzorul de la baza inelului care transmite dacă ”bariera” dintre emițător și receptor a fost tăiată de minge
#define PIN_SENZOR2 23          //senzorul de la baza inelului care transmite dacă ”bariera” dintre emițător și receptor a fost tăiată de minge
#define PIN_SENZOR3 19          //senzorul de la finalul plasei care transmite dacă ”bariera” dintre emițător și receptor a fost tăiată de minge

#define TREI_PUNCTE 35          //distanța dintre inel și semicercul de 3 puncte
BluetoothSerial SerialBT;       //crearea obiectului SerialBT prin care se va face comunicarea prin Bluetooth

String comandă = "";            //șirul de caractere care prelucrează mesajele venite și extrage informația necesară
float distanță_minge_inel =0;   //distanța de la minge la inel ce se extrage din mesajul venit prin Bluetooth
bool înscriere_permisă;         //ține cont de perioada de joc și indică dacă meciul se poate înscrie. Doar dacă nu este pauză, acest lucru este posibil
int ultima_aruncare;            //ține minte valoarea ultimului coș înscris pentru a-l putea scădea dacă arbitrul apasă pe butonul de anulare al ultimului coș marcat

unsigned long timp_curent = 0;  //reprezintă timpul curent, ce se măsoară în milisecunde
unsigned long timp_anterior = 0;//reprezintă timpul anterior față de măsurarea curentă, folosit pentru a determina intervalul de timp ce s-a scurs, și se măsoară în milisecunde

int scor;                       //scorul ce se înregistrează pe tabela de marcaj 
int stare_senzor1_inel= 1;      //memorează starea senzorului de pe inel
int stare_senzor2_inel= 1;      //memorează starea senzorului de pe inel
int stare_senzor3_inel= 1;      //memorează starea senzorului de pe inel

int scor_stergere=0;
char comandă_curentă;           //comanda curentă în funcție de care se iau deciziile pe parcursul programului

void setup()                    //metodă ce se apelează o singură dată, la începutul programului, și este responsabilă pentru inițializarea variabilelor
{  
  Serial.begin(9600);                     //viteza de transmitere a informației în comunicarea serială (o folosesc aici pentru verificare), 9600 biți/secundă
  SerialBT.begin("ESP_Inel2_Dispozitiv"); //inițializarea comunicării prin Bluetooth, iar dispozitivul va fi găsit cu numele de ”ESP_Inel2_Dispozitiv”
  pinMode(PIN_SENZOR1, INPUT_PULLUP);     //se configurează PIN_SEZOR1 ca și pin de intrare 
  pinMode(PIN_SENZOR2, INPUT_PULLUP);     //se configurează PIN_SEZOR2 ca și pin de intrare 
  pinMode(PIN_SENZOR3, INPUT_PULLUP);     //se configurează PIN_SEZOR3 ca și pin de intrare 
  scor=0;                                 //se inițializarea valoarea scorului, pentru a fi siguri că pornește de la 0
  ultima_aruncare =0;                     //se inițializarea valoarea ultimei aruncări înscrise, pentru a fi siguri că nu pornește de la altă valoare
}

void loop()                                     //metodă ce se execută, în buclă, permanent
{
  if (comandă.equals("RESET"))                  //se verifică dacă s-a trimis comanda de ”RESET”, pentru a inițializa variabilele importante, cu valoarea 0
  {                                             //dacă acest lucru nu s-ar fi întâmplat, variabilele s-ar fi resetat doar după ce flash-uia un nou cod
    scor = 0;
    ultima_aruncare = 0;
    comandă = "";                               
  }
  stare_senzor1_inel = digitalRead(PIN_SENZOR1);    //citirea senzorului 1
  stare_senzor2_inel = digitalRead(PIN_SENZOR2);    //citirea senzorului 2
  while (SerialBT.available())                      //cât timp există date ce sunt transmise prin Bluetooth către acest IMU, acestea vor fi interpretate
  {
    char c = SerialBT.read();                       //mesajul trimis este citit caracter cu caracter
    if (c == '\n')                                  //caracterul de ”linie noua” = '\n', indică finalul comenzii. După ce acesta este primit, se începe interpretare mesajului primit
    {                                               //se poate începe prelucrarea comenzii
      comandă.trim();                               //elimină orice spațiu de la începutul și sfârșitul comenzii
      if(comandă[0]=='3')                           //dacă comanda începe cu cifra 3, înseamnă că mesajele ce vin, se ocupă de gestionarea timpului de joc și a scorului
      {
        String sir = String(comandă.c_str() +1);    //se elimină primul caracter pentru că nu face parte din mesajul în sine, ci ne ajută să ne dăm seama cum trebuie interpretată comanda
        if (sir.equals("S"))                        //dacă comanda venită este S, atunci înseamnă că timpul de joc a pornit, și se pot înscrie puncte
        {
          înscriere_permisă = true;                 //variabila este setată pe adevărat și va permite înscrierea de puncte
          comandă_curentă = 'S';                    //reținerea comenzii curente
          Serial.println("Received S");             //afișare mesajului ajuns, folosit la testare
        }
        if (sir.equals("P"))                        //dacă comanda este P, înseamnă că este pauză, și nu se pot înscrie puncte
        {
          înscriere_permisă = false;                //variabila este setată pe fals, și nu va permite înscrierea punctelor
          Serial.println("Received P");
        }
        if (sir.equals("L"))                        //dacă mesajul este L, înseamnă că suntem în timpul sfetului și timpul nu merge, ceea ce înseamnă că se pot marca aruncări libere
        {
          înscriere_permisă = true;                 //este permisă aruncarea la coș 
          comandă_curentă = 'L';                    //stabilim că este aruncare liberă, deci valorează un punct
          Serial.println("Received L");
        }
        if (sir.equals("B"))                        //dacă mesajul este B înseamnă că arbitrul a apăsat butonul de anulare al ultimului coș marcat,
        {                                           //dacă mesajul nu este însoțit și de b, atunci înseamnă că arbitrul a anulat ultimul coș pe perioada unei pauze, deci nu se mai poate marca nimic
          comandă_curentă = 'B';                    
          Serial.println("Received B");
        }
        if (sir.equals("b"))                        //dacă mesajul este b, înseamnă că arbitrul a decis anularea ultimei aruncări, 
        {                                           //dar suntem într-un interval de timp în care se pot înscrie aruncări libere
          comandă_curentă = 'b';
          înscriere_permisă = true;                 //pemite inscriere aruncărilor libere
          Serial.println("Received b");
        }
        //String subsir = comandă.substring(1);     //se mai elimină și următorul caracter din mesaj
        if(sir.startsWith("H"))                     //dacă mesajul începe cu 3H, pentru o simplitate a gestionarii codului în situația dată      
        {                                           //la pauza mare, panourile se schimbă, iar pentru a păstra corectitudinea pe tabela de marcaj, trebuie inițializat scorul după pauză
                                                    //cu punctele marcate de adversar în prima perioadă de joc
                                                    //mesajul trimis la pauza mare este de forma 3H*scorA-scorB
          int start = sir.indexOf('*');             //extragem indicele elementului *
          int stop = sir.indexOf('-');               //extragem indicele elementului -
          String val = sir.substring(start+1, stop); //scorul ce va fi după pauza mare, este scorul echipei A, deoarece acesta este codul ce rulează pentru panoul echipei B, inițial
          scor = val.toInt();                       //ce convertește la întreg valoarea
          Serial.println(scor);
        }
      }
      if(comandă[0]=='4')                           //dacă mesajul începe cu 4, înseamnă ca vine de la cameră și ne transmite distanța de la minge la cele 2 inele
      {
        String d = String(comandă.c_str() +1);      //eliminăm cifra 4 din mesaj, mesajul este de forma 4A distanta inel 1B distanta inel2
        Serial.println(d);
        String dist;            
        int indexB = d.indexOf('B');            //fiind considerat inelul 2, ne interesează distanța ce se află după litera B
        dist = d.substring(indexB+1);    //se extrage distanța, care se află de la B până la finalul mesajului
        distanță_minge_inel = dist.toFloat();       //se convertește în număr real
        Serial.println(distanță_minge_inel);
      }
      comandă = "";                                 //resetăm variabila comandă pentru următoarea citire
    } 
    else 
    {
      comandă += c;                                 //dacă comanda nu este alcătuită doar dintr-un caracter după cifră, atunci mesajul trebuie construit
                                                    //pentru că se citește caracter cu caracter, air aici se adăugă caracterul la comandă
    }
  } 
                                                    //dacă mesajul a fost compus în întregime, atunci se interperetează
  if((stare_senzor1_inel == 0 || stare_senzor2_inel==0) && înscriere_permisă)   //dacă mingea a tăiat partea superioară de inel și conform mesajelor, este permisă înscrierea punctelor
  {                                                                             //verificăm ce valoare are coșul marcat
    timp_anterior = millis();                                                   //pentru a asigura faptul că mingea a intrat în coș de sus în jos 
    timp_curent = millis();                                                     //în 700 de ms se așteaptă ca mingea să taie și senzorii pentru considera o detecție a unui coș marcat
    while(timp_curent - timp_anterior < 700)                                    //se iau măsurători timp de 700 de ms de la senzorul de jos pt a vedea dacă mingea a trecut pe acolo
    {
      stare_senzor3_inel = digitalRead(PIN_SENZOR3);
      if(stare_senzor3_inel == 0)                                               //dacă se consideră a aruncare validă (senzorul de jos se activează)
      { 
        if(comandă_curentă == 'L' ||  comandă_curentă == 'b')                   //suntem în situația când sunt permise doar aruncările libere
        {
          scor++;                                                               //actualizarea scorului, se incrementează doar cu un punct
          ultima_aruncare = 1;                                                  //pentru a ține minte valoarea ultimului coș marcat, în cazul în care se decide anularea lui
          SerialBT.printf("%d", scor);                                          //se trimite prin Bluetooth noua valoare
          break;                                                                //se iese din while pentru că s-a actualizat scorul
        }
        if(comandă_curentă == 'S')                                              //timpul merge, deci se pot înscrie 2 sau 3 puncte
        {
          Serial.print("luat");
          Serial.println(distanță_minge_inel);                                  //diverse afișari pentru a fi siguri că mesajele aua fost interpretate corect
          if(distanță_minge_inel < TREI_PUNCTE)                                 //se verifică dacă distanța este mai mică decât distanța până la semicercul de trei puncte
          {
            scor = scor+2;                                                      //se modifică scorul, adăugându-se 2 puncte
            ultima_aruncare = 2;                                                //pentru a ține minte valoarea ultimului coș marcat, în cazul în care se decide anularea lui
          }
          else
          {
            scor = scor+3;                                                      //dacă distanța e mai mare, atunci coșul valorează 3 puncte
            ultima_aruncare = 3;                                                //pentru a ține minte valoarea ultimului coș marcat, în cazul în care se decide anularea lui
          }
          SerialBT.printf("%d", scor);                                          //se trimte scorul actualizat prin Bluetooth
          break;
        }
      }
      timp_curent = millis();                                                   //se actualizează timpul curent, pentru a măsura cele 700 de ms
    }
  }
 if(comandă_curentă == 'B' && (scor != scor_stergere))                                                     //suntem în cazul în care arbitrul a decis anularea ultimului coș
  {
    scor = scor - ultima_aruncare;                                              //se actualizează noul scor
    scor_stergere = scor;
    ultima_aruncare = 0;                                                        //ultima aruncare se face 0 pentru a nu permite ștergerea multiplă, din greșeală
 }
  
  SerialBT.printf("%d", scor);                                                  //trimiterea în permanență a scorului
  delay(50);                                                                    //o mică întârziere, pentru a se procesa informația
}

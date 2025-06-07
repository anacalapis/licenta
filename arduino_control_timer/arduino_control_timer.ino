#include <Wire.h>                             //biblioteca pentru comunicarea prin protocolul I2C
#include <LiquidCrystal_I2C.h>                //bibliotecă pentru controlul LCD-ului

#define NR_SEC_SFERT 60                       //timpul, in secunde, pentru durata unui sfert
#define NR_SEC_PAUZA_MICA 3                   //timpul, in secunde, pentru durata unei pauze mici (între sf1/sf2 și sf3/sf4)
#define NR_SEC_PAUZA_MARE 5                   //timpul, in secunde, pentru durata pauzei mari 
#define NR_SEC_OVERTIME 10                    //timpul, in secunde, pentru durata unei reprize de prelungiri

LiquidCrystal_I2C lcd(0x27, 16, 2);           //se va conecta obiectul lcd la adresa 0x27 (adresa I2C a LDC-ului), care are un afișaj de 16 coloane, pe 2 rânduri

volatile bool e_pauza = false;                //variabilă ce se ocupă de oprirea timpului de joc și indică dacă este pauză (volatile pt a-i putea modifica valoarea și în afara funcție loop)
unsigned long timp_anterior = 0;              //variabilă ce reține ultima măsurătoare a timpului
unsigned long timp_curent =0;                 //variabila curentă folosită pentru determinarea timpului
const unsigned long interval = 1000;          //interval folosit pentru scăderea timpului de pe tabelă (1 secundă)
int interval_joc_curent =0;                   //numara in ce interval ne aflam, par este sfert, impar pauza
int nr_sfert=0;                               //numărul sfertului de joc
int nr_overtime =0;                           //numărul reprizelor de prelungire, dacă este cazul
bool overtime = false;                        //indică dacă va fi necesar de reprize de prelungire
int timp = 0;                                 //timpul, ce se măsoară in secunde
String comanda;                               //variabila ce citește comanda ce vine de pe serial
bool buton_stergere =false;                   //indică dacă a fost folosit butonul de ștergere pentru a nu permite ștergerea punctelor de la ambele echipe
int curent_scor1 =0, curent_scor2 =0;         //variabile ce memorează scorul actual
int anterior_scor1=0, anterior_scor2=0;       //rețin scorul anterior pentru a ne da seama dacă scorul s-a modificat, și astfel să indicăm care echipă a marcat ultima
int ultim_scor_marcat;                        //ține minte ce echipă a marcat ultima (daca este 1, semnifica ca ultimul cos a fost marcat de echipa A, iar daca este 2  de echipa B)

void setup()                                  //funcție responsabilă de initializări
{
  Serial.begin(9600);
  lcd.init();                                 //se inițiaza comunicarea cu ecranul LCD
  lcd.backlight();                            //se activează iluminarea de fundal, fără de care textul nu ar fi vizibil 
  lcd.setCursor(0, 0);                        //se setează poziția cursorului pentru a se scrie un mesaj de start
  lcd.print("  Start meci!");                 //se scrie, începând de la poziția indicată mai sus mesajul
  delay(500);                                 //se oprește execuția timp de jumate de secundă
  lcd.clear();                                //ecranul este șters pentru a afișa ce ne interesează
}

void loop() 
{
  switch(interval_joc_curent)                 //se execută diverse metode, în funcție de acest număr care indică în ce sfert/pauză/repriză de prelungire suntem
  {
    case 1:                                   //pauza dintre primul si al doilea sfert
    case 5:                                   //pauza dintre al treiea si al patrulea sfert
    {
      timp = NR_SEC_PAUZA_MICA;               //se copiază în variabila timp, numărul de secunde aferente acestor tipuri de pauze 
      afisare_pauza();                        //se apelează funcția destinată afișării pauzei
      break;
    }
    case 0:                                   //suntem în sfertul 1
    case 2:                                   //suntem în sfertul 2
    case 4:                                   //suntem în sfertul 3
    case 6:                                   //suntem în sfertul 4
    {
      timp = NR_SEC_SFERT;                    //se copiază în variabila timp, numărul de secunde aferent unui sfert
      nr_sfert++;                             //numărul efectiv al sfertului va crește de fiecare dată când se ajunge aici
      interpretare_sfert();                   //se apelează funcția destinată parcurgerii unui sfert și gestionarea situaților ce pot apărea
      break;
    }
    case 3: 
    { 
      timp = NR_SEC_PAUZA_MARE;               //se copiază în variabila timp, numărul de secunde aferent pauzei mari
      afisare_pauza();                        //se apelează funcția destinată afișării pauzei
      Serial.print("H*");                     //după finalul pauzei mari, se trimite un mesaj către cele 2 inele, prin care le obligă să ia valoarea celuilalt inel
      Serial.print(curent_scor1);             //din cauză că, începând cu sfertul al treilea, panourile de atac al celor 2 echipe se schimbă, dar afișarea pe tabelă nu se modifică
      Serial.print("-");                      //mesajul va fi de forma H*scor1-scor2
      Serial.println(curent_scor2);           
      break;
    }
    case 7:                                   //se verifică dacă sunt necesare reprize de prelungire
    {
      while(curent_scor1 == curent_scor2)     //atâta timp cât cele 2 scoruri sunt identice, avem nevoie o repriză nouă de prelungire
      {
        overtime = true;                      //se setează variabila prin care se indică că ne aflăm într-o repriză de prelungire, pentru a modifica afișările pe ecran
        timp = NR_SEC_PAUZA_MICA;             //se copiază în variabila timp, numărul de secunde aferente unei pauze
        afisare_pauza();                      //se apelează funcția destinată afișării pauzei
        timp = NR_SEC_OVERTIME;               //se copiază în variabila timp, numărul de secunde aferente unei reprize de prelungire
        nr_overtime++;                        //numărul ce indică repriza de prelungire va crește de fiecare dată când se ajunge aici
        interpretare_sfert();                 //se apelează funcția care se ocupă de gestionarea unui interval de joc
      }
      break;
    }
    case 8:                                   //finalul meciului
    {
      lcd.setCursor(0, 0);                    //se setează un mesaj ce indică finalul de meci
      lcd.print(" Final de meci!");
      lcd.setCursor(0, 1);
      lcd.print("EchA ");
      lcd.print(curent_scor2);
      lcd.print("-");
      lcd.print(curent_scor1);
      lcd.print(" EchB");
      while(true);                            //codul rămâne blocat aici după finalul de partidă
    }
  }
  interval_joc_curent ++;                     //incrementarea intervalului de joc pentru a indica perioada curentă
}

void afisare_timp(int perioada)               //afișarea timpului de joc sau cel din pauză în funcție de argumentul primit
{
  int minutes = timp / 60;                    //numărul de minute ce se calculează în funcție de secundele rămase din intervalul de joc/pauză
  int secunde = timp % 60;                    //numărul de secunde dintr-un minut ce se calculează în funcție de secundele rămase din intervalul de joc/pauză
  lcd.clear();                                //ștergerea ecranului LCD
  lcd.setCursor(0, 0);                        //setarea cursorului la capătul primul rând
  if(perioada == 0)                           //funcția este apelată pentru a afișa timpul rămas pe parcursul pauzei
  {
    lcd.print("Pauza:  ");
  }
  else                                        //suntem într-un interval de joc
  {
    if(overtime)                              //dacă a fost activată variabila de overtime, înseamnă că afișam timpul rămas din repriza de prelungire
    {
      lcd.print("OT ");
      lcd.print(perioada);
    }
    else                                      //suntem în unul din cele 4 sferturi de joc efectiv
    {
      lcd.print("Sf ");
      lcd.print(perioada);
    }
    lcd.print(":   ");
  }
  if (minutes < 10)                           //se afișează timpul rămas din interval
  {
    lcd.print("0");                           //dacă sunt mai puțin de 10 minute, se pune un 0 pe prima poziție
  }
  lcd.print(minutes);                         //afișarea numărului de minute
  lcd.print(":");
  if (secunde < 10)                           //pentru a replica cronometrul real, în cazul în care sunt mai puțin de 10 secunde, se va afisa un 0 in față                      
  {
    lcd.print("0");
  }
  lcd.print(secunde);                         //se afișează numărul de secunde
  afisare_scor();                              //se apelează funcția ce se ocupă de afișarea scorului
}

void interpretare_sfert()                     //gestoionarea tuturor evenimentelor ce pot apărea pe parcursul unui interval de joc
{
  if(timp == NR_SEC_SFERT || timp == NR_SEC_OVERTIME) //dacă timpul este egal cu una din cele 2 variabile, atunci înseamnă că suntem la începutul ei
  {
    int minutes, secunde;                     //varibile ce vor fi folosite pentru a afișa timpul, în format normal, cu minute:secunde, în urma convertiri numărului de secunde total
    if(overtime)                              //dacă suntem într-o repriză de prelungiri, se pleacă de la timpul alocat ei
    {
      minutes = NR_SEC_OVERTIME / 60;
      secunde = NR_SEC_OVERTIME % 60;
    }
    else                                      //în cazul actual, suntem la începutul unuia dintre cele 4 sferturi, iar numărul de minute și cel am secundelor se calculează după altă variabilă
    {
      minutes = NR_SEC_SFERT / 60;
      secunde = NR_SEC_SFERT % 60;
    }
    lcd.clear();                              //ștergerea ecranului LCD
    lcd.setCursor(0, 0);                      //setarea cursorului la capătul primul rând
    if (overtime)                             //se afișează tipul intervalului de joc
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
    if(minutes<10)                            //se afișează într-un mod elegant, timpul de la care se pornește, în urma calculelor făcute anterior
    {                                         //dacă numărul minutelor și cel al secundelor este format dintr-o singură cifră, se scrie un 0 în față pentru a arăta mai frumos
      lcd.print("0");
    }
    lcd.print(minutes);
    lcd.print(":");
    if(secunde<10)
    {
      lcd.print("0");
    }
    lcd.print(secunde);
    if(nr_sfert == 3)                         //datorită schimbării scorului după terminarea pauzei mari, acesta se va inversa, iar pentru a nu se modifica pe tabelă se face următorul lucru
    {                                         //în cadrul funcției de afișare_scor, ordinea de afișare a celor 2 scoruri depinde de sfertul în care se află
      nr_sfert--;                             //dacă suntem înainte de pauza mare, se afișeaza scor_echipa_1 - scor_echipa_2, dar după pauza mare, cele 2 sunt inversate datorită schimbării panourilor
      afisare_scor();                         //pentru a evita modificare pe tabelă, doar în acest caz, decrementez nr_sfert pentru a se afișa normal
      nr_sfert++;                             //după care revin inapoi ca sa nu imi distrug afisajul pe mai departe și practic totul e ok pe mai departe
    }
    else                                      //dacă suntem în orice altă situație
    { 
      afisare_scor();                         //se afișează scorul normal
    }
    comanda = Serial.readStringUntil('\n');   //se citește de pe portul serial un șir de caractere până la apariția caracterului de linie nouă '\n'
    comanda.trim();                           //se elimină spațiile albe de la începutul și finalul mesajului
    buton_stergere=false;                     //suntem înainte de începutul sfertului, iar ștergerea ultimelor puncte este posibilă. Se setează această valoare pt a nu șterge de la ambele echipe
    while(!comanda.equals("00"))              //e început de sfert și se așteaptă ca timpul să fie pornit de arbitru
    {
      comanda = Serial.readStringUntil('\n'); //se cițeste ce vine pe serial
      comanda.trim();                         //se elimină spațiile albe de la începutul și finalul mesajului
      if (comanda.equals("02") && buton_stergere ==false) //dacă se apasă butonul de ștergere pentru prima dată în acest interval, se vor șterge ultimele puncte
      {
        if(ultim_scor_marcat == 1)            //dacă ultima echipă ce a înscris este echipa de la panoul 1
        {
          Serial.println("A");                //se trimite un mesaj pe serial, pentru a se efectua ștergerea în cadrul modulului ce se ocupă de panoul 1
          ultim_scor_marcat = 1;
        }
        if(ultim_scor_marcat == 2)            //dacă ultima echipă ce a înscris este echipa de la panoul 2
        {
          Serial.println("B");                //se trimite un mesaj pe serial, pentru a se efectua ștergerea în cadrul modulului ce se ocupă de panoul 2
          ultim_scor_marcat =2;
        }
        buton_stergere=true;                  //dacă s-a efectuat o ștergere, variabila se pune pe True pentru a nu se permite ștergerea și de la cealaltă echipă
      }
      afisare_scor();                         //se afișează scorul actualizat
    }
    buton_stergere=true;                      //pentru a ”încheia” acest interval în care se pot șterge ultimele puncte, se setează pe True variabila
  }
  while(timp !=0)                             //suntem in timpul sfertului, unde timpul se scurge
  {
    comanda = Serial.readStringUntil('\n');   //se citește de pe portul serial un șir de caractere până la apariția caracterului de linie nouă '\n'
    comanda.trim();                           //se elimină spațiile albe de la începutul și finalul mesajului
    if(comanda.equals("01"))                  //dacă comanda venită este de la fluier
    {
      Serial.println("L");                    //se transmite mai departe că suntem în cadrul sfertului, iar acest flueir face ca și coșurile ce urmează să se înscrie să fie de 1 pct
      e_pauza = true;                         //variabilă ce oprește timpul 
      delay(100);
    }
    afisare_scor();                           //afișarea scorului
    if (comanda.equals("00"))                 //dacă comanda venită este de la butonul de start
    {
      Serial.println("S");                    //se transmite mai departe faptul că coșurile ce urmează sa fie înscrise sunt de 2 sau 3 puncte
      e_pauza = false;                        //variabilă ce reia timpul
      buton_stergere = false;                 //se setează pe False pentru a nu permite ca în timpul jocului, când cronometrul merge, să se șteargă ultimele puncte
      delay(100); 
    }
    if (!e_pauza)                             //timpul de joc din timpul sfertului merge
    {
      timp_curent = millis();                 //se ia timpul curent pentru a știi când a trecut o secundă pentru a se actualiza și pe tabelă            
      if (timp_curent - timp_anterior >= interval && timp > 0)  //dacă a trecut o secundă, iar timpul nu a ajuns la final
      {
        timp_anterior = timp_curent;          //se actualizează timpul anterior
        timp--;                               //scade timpul din numărul de secunde ce sunt destinate intervalului de joc
        if(overtime)                          //dacă suntem în overtime, se va apela funcția de afisare_timp cu argumentul specific, care va afișează mesajul pentru prelungiri pe ecran
        {
          afisare_timp(nr_overtime); 
        }
        else                                  //dacă suntem într-un sfert normal, se va apela funcția de afisare_timp cu argumentul specific, care va afișează mesajul pentru sferturi pe ecran
        {
          afisare_timp(nr_sfert); 
        }
      }
    }
    else                                      //dacă timpul de joc este oprit în perioada sfertului, înseamnă că suntem in perioada aruncarilor libere
    {
      if (comanda.equals("02"))               //datorită faptului că timpul este oprit, se poate anula ultimul coș marcat
      {
        if(ultim_scor_marcat == 1)            //dacă s-a apăsat butonul de ștergere, iar ultima echipă ce a marcat este echipa ce înscrie la panoul 1
        {
          Serial.println("A");                //atunci se trimite mesajul care va șterge ultimele puncte marcate la inelul 1
          ultim_scor_marcat = 1;
        }
        if(ultim_scor_marcat == 2)            //dacă s-a apăsat butonul de ștergere, iar ultima echipă ce a marcat este echipa ce înscrie la panoul 2
        {
          Serial.println("B");                //atunci se trimite mesajul care va șterge ultimele puncte marcate la inelul 2
          ultim_scor_marcat =2;
        }
        delay(100); 
        afisare_scor();                       //se afișează noul scor
        if(ultim_scor_marcat == 1)            //dacă s-a apăsat butonul de ștergere, iar ultima echipă ce a marcat este echipa ce înscrie la panoul 1
        {
          Serial.println("a");                //se trimite mesajul care permite înscrierea aruncărilor de 1 punct în urma ștergerii a ultimelor puncte marcate de echipa de la inelul 1
        }
        else
        {
          Serial.println("b");                //se trimite mesajul care permite înscrierea aruncărilor de 1 punct în urma ștergerii a ultimelor puncte marcate de echipa de la inelul 2
        }
        int scor_aici1 = curent_scor1;        //previne ștergerea multiplă de puncte din cadrul ambelor echipe
        int scor_aici2 = curent_scor2;        //se ia scorul curent, după ce s-a înregistrat ștergerea
        while (scor_aici1 == curent_scor1 && scor_aici2 == curent_scor2) //în acest caz, se ignoră apăsarea multiplă a butonului și se ia în considerare doar dacă se pornește timpul sau se înscrie
        {
          comanda = Serial.readStringUntil('\n');//se citește de pe portul serial un șir de caractere până la apariția caracterului de linie nouă '\n'
          comanda.trim();                     //se elimină spațiile albe de la începutul și finalul mesajului
          if (comanda.equals("00"))           //mesaj care indică pornirea timpului de joc
          {
            Serial.println("S");              //se transmite că se pot marca coșuri de 2 sau 3 puncte
            e_pauza = false;                  //variabilă ce reia timpul
            buton_stergere = false;           //se setează variabila care nu permite ștergerea ultimului coș
            delay(100); 
            break;
          }
          if(comanda.startsWith("1"))         //după ce se înscrie, se poate apăsa din nou butonul de ștergere, deci se iese din bucla while
          {
            curent_scor1 =atoi(comanda.substring(1).c_str()); //se actualizează noul scor
          }
          if(comanda.startsWith("2"))         //dacă începe cu 2, scorul provine de la echipa ce atacă la inelul 2
          {
            curent_scor2 =atoi(comanda.substring(1).c_str()); //se actualizează noul scor
          }
        }
      }
    }
  }
}

void afisare_pauza()                          //se afișează pauza
{
  Serial.println("P");                        //se trimite mesajul către cele 2 inele prin care se anunță că este pauză și că nu se poate înscrie
  int minutes = timp / 60;                    //se calculează minutele de pauză în funcție de numărul de secunde alocate acestui interval
  int secunde = timp % 60;                    //se calculează secundele din cadrul minutelor de pauză în funcție de numărul de secunde alocate acestui interval
  if(timp==NR_SEC_PAUZA_MICA || timp==NR_SEC_PAUZA_MARE)    //dacă suntem la început de pauză
  {
    lcd.clear();                              //ștergerea ecranului LCD
    lcd.setCursor(0, 0);                      //setarea cursorului la capătul primul rând
    lcd.print("Pauza   ");                    //se afișează mesajul ”Pauza  ” împreună cu timpul rămas, în format cunoscut, minute:secunde
    if(minutes<10)                            //dacă sunt mai puțin de 10 minute, se adaugă un 0 pentru a arăta frumos
    {
      lcd.print("0");
    }
    lcd.print(minutes);                       //se afișează minutele
    lcd.print(":");
    if(secunde<10)                            //se procedează la fel și în cazul secundelor
    {
      lcd.print("0");
    }
    lcd.print(secunde);
    afisare_scor();                           //se afișează scorul

  }
  buton_stergere=false;                       //se permite ștergerea ultimelor puncte marcat pe parcursul pauzei
  while(timp!=0)                              //dacă pauza este în derulare
  {
    timp_curent = millis();                   //se ia timpul curent pentru a știi când a trecut o secundă pentru a se actualiza și pe tabelă 
    comanda = Serial.readStringUntil('\n');   //se citește de pe portul serial un șir de caractere până la apariția caracterului de linie nouă '\n'
    comanda.trim();                           //se elimină spațiile albe de la începutul și finalul mesajului
    if (comanda.equals("02") && buton_stergere ==false)   //dacă se apasă pentru prima dată pe butonul de ștergere
    {
      if(ultim_scor_marcat == 1)              //dacă ultimul coș marcat a fost de echipa ce înscrie la inelul 1
        {
          Serial.println("A");                //se trimite mesajul aferent
          ultim_scor_marcat =1;
        }
      else                                    //dacă ultimul coș marcat a fost de echipa ce înscrie la inelul 2
        {
          Serial.println("B");                //se trimite mesajul aferent
          ultim_scor_marcat =2;
        }
      delay(100); 
      afisare_scor();                         //se afișează noul scor actualizat după ștergere
      buton_stergere=true;                    //se setează variabila pe True pentru a nu mai permite ștergerea și a altor puncte
    }
    afisare_scor();                           //se afișează mereu scorul pe tabelă în timpul pauzei
    if (timp_curent - timp_anterior >= interval && timp > 0) //dacă a trecut o secundă, iar timpul nu a ajuns la final
    {
      timp_anterior = timp_curent;          //se actualizează timpul anterior
      timp--;                               //scade timpul din numărul de secunde ce sunt destinate intervalului de joc
      afisare_timp(0);
    }
  }
}

void afisare_scor()                         //se citește de pe serial scorul în permanență
{
  comanda = Serial.readStringUntil('\n');   //se citește de pe portul serial un șir de caractere până la apariția caracterului de linie nouă '\n'
  comanda.trim();                           //se elimină spațiile albe de la începutul și finalul mesajului
  if(comanda.startsWith("1"))               //dacă mesajul începe cu 1, înseamnă că vine din partea inelului 1, și conține scorul aferent echipei ce atacă la acel panou
    {
      int stop= comanda.indexOf('*');       //oprim citerea la caracterul *, caracter special pus la final pentru a nu citi, din întâmplare și alt mesaj
      String  scor_nr= comanda.substring(1, stop);  //se extrage scorul actual din cadrul mesajului
      curent_scor1 =scor_nr.toInt();        //se convertește în număr întreg
      if(anterior_scor1 != curent_scor1)    //dacă scorul s-a modificat
      {
        ultim_scor_marcat =1;               //setăm variabila care reține la ce inel s-a înscris cel mai recent, pentru a știi de unde să șteargă în cazul în care se apasă pe butonul de ștergere
      }
      anterior_scor1=curent_scor1;          //actualizăm scorul
    }
    if(comanda.startsWith("2"))             //dacă mesajul începe cu 2, înseamnă că vine din partea inelului 2, și conține scorul aferent echipei ce atacă la acel panou
    {
      int stop= comanda.indexOf('/');       //oprim citerea la caracterul /, caracter special pus la final pentru a nu citi, din întâmplare și alt mesaj
      String  scor_nr= comanda.substring(1, stop); //se extrage scorul actual din cadrul mesajului
      curent_scor2 =scor_nr.toInt();        //se convertește în număr întreg
      if(anterior_scor2 != curent_scor2)    //dacă scorul s-a modificat
      {
        ultim_scor_marcat =2;               //setăm variabila care reține la ce inel s-a înscris cel mai recent, pentru a știi de unde să șteargă în cazul în care se apasă pe butonul de ștergere
      }
      anterior_scor2=curent_scor2;          //actualizam scorul
    }  
  lcd.setCursor(0, 1);                      //se setează cursorul la începutul celui de-al doiela rând
  lcd.print("EchA ");                       //se afișează echipa A
  if(nr_sfert<3)                            //dacă ne aflăm în prima jumătate a meciului, echipa care atacă la inelul 1 este echipa A, iar echipa ce atacă la inelul 2 este echipa B
  {
    if(curent_scor1<10)                     //afișarea unui spațiu, în cazul în care scorul este mai mic decât 10
    {
      lcd.print(" ");
    }
    lcd.print(curent_scor1);                //afișarea scorului echipei A
    lcd.print("-");
    lcd.print(curent_scor2);                //afișarea scorului echipei B
    if(curent_scor2<10)                     //afișarea mai multor spații, în cazul în care scorul este mai mic decât 10
    {
      lcd.print("  ");
    }
    else
    {
      lcd.print(" ");
    }  
  }
 else                                       //dacă suntem după pauza mare și panourile s-au inversat, trebuie să ne adaptăm și noi pentru a nu se inversa scorul pe tabelă
 {
    if(curent_scor2<10)                     //afișarea unui spațiu, în cazul în care scorul este mai mic decât 10
    {
      lcd.print(" ");
    }
    lcd.print(curent_scor2);                //se afișează prima dată ce vine de la inelul 2, echivalent cu scorul ecipei A, după pauza mare
    lcd.print("-");
    lcd.print(curent_scor1);                //se afișează după, ce vine de la inelul 1, echivalent cu scorul ecipei B, după pauza mare
    if(curent_scor1<10)                     //afișarea mai multor spații, în cazul în care scorul este mai mic decât 10
    {
      lcd.print("  ");
    }
    else
    {
      lcd.print(" ");
    }
 }
  lcd.print(" EchB");                       //se afișează echipa B
}

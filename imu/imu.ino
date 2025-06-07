#include <Wire.h>                           //bibliotecă folosită pentru protocolul de comunicare I2C dintre ESP32 si MPU6050
#include <Adafruit_MPU6050.h>               //biblioteci folosite pentru senzorul MPU6050
#include <Adafruit_Sensor.h>  
#include <BluetoothSerial.h>                //bibliotecă folosită pentru comunicare Bluetooth ce se realizează între ESP32 și RaspberryPi

BluetoothSerial SerialBT;                   //obiect pentru comunicarea Bluetooth dintre ESP32 și Raspberry Pi
Adafruit_MPU6050 imuu;                      //obiect folosit pentru a lucra cu MPU6050 (imu este cuvânt specific, imi dadea eroare de compilare)

#define CAPACITATE_VECTOR 30                //capacitatea celor 2 vectori 
#define FEREASTRA 10                        //numărul de măsurători citite în avans față, acea fereastră care este mai înaintată
float vector_1[CAPACITATE_VECTOR]={0};      //primul vector folosit în obținerea valorii maxime
float vector_2[CAPACITATE_VECTOR]={0};      //al doilea vector folosit în obținerea valorii maxime
int poziție_vector1=0;                      //indică pozitia elementelor din cadrul primului vector la prima inserare
int poziție_vector2=0;                      //indica poziția elementelor din cadrul celui de al doilea vector la prima inserare
bool start_prelucrare=false;                //este folosit pentru a popula cei 2 vectori la inceput deoarece este un caz special față de restul codului
bool final_vector1=false;                   //folosită pentru a indica care dintre cei 2 vectori conține date mai recente și este mai înaintat pe ”axa timpului”
float maxim_prelucrare_anterioara =0;       //pentru a compara cu valoarea maximă anterioară

void setup()                                //se execută o singură dată la începutul execuției
{
  SerialBT.begin("ESP_IMU");                //se inițiază modulul Bluetooth de pe ESP32 și se oferă un nume sub care va fi găsit pe Raspberry Pi
  Wire.setClock(400000);                    //setează viteza de transfer a datelor (frecvența SCL) la 400kHz - fast mode
  Wire.begin();                             //inițiază comunicarea I2C
  delay(250);
  imuu.begin();                             //se inițializează modulul MPU6050 care se va conecta, prin I2C, la ESP32
}

void loop()
{
  if(start_prelucrare == false)                           //dacă este prima trecere prin program, trebuie populați cei 2 vectori în altă maniera față de cum va urma în cadrul buclei
  {
    prelucrare_initiala();                                //apelarea funcției de populare a vectorilor
    start_prelucrare=true;                                //setarea variabilei pe true pentru a nu se mai intra pe aici niciodată
  }
  float rezultat = prelucrare_vector();                   //se ia valoarea maximă din cadrul ferestrei ce se mută, în permanență, peste alte 30 de elemente
  if(maxim_prelucrare_anterioara <= rezultat)             //se verifică dacă valoarea curentă este mai mare decât cea precedentă
  {
    maxim_prelucrare_anterioara=rezultat;                 //înseamnă că suntem în continuă creștere și încă nu s-a detectat vârful ascensiunii
  }
  else                                                    //dacă se găsește o valoare mai mică decât precedenta înseamnă că s-a descoperit vârful accelerației, ceea ce prezintă interes
  {
    if((int)maxim_prelucrare_anterioara != (int)rezultat) //aici se ajunge în cazul în care rezultatul curent  < maxim_prelucrare_anterioara
    {                                                     //pentru a evita diferențele la nivelul virgulei, si pentru a reduce mesajele ce urmează să fie transmise
                                                          //si pentru a crește precizia momentului pe care îl căutăm, am decis să iau în considerare doar partea întreagă a rezultatului
                                                          //dacă cele 2 valori diferă și la nivelul unității, sunt mai șanse să fi determinat vărful accelerației
      int masuratoare= (int)maxim_prelucrare_anterioara;  //prelucrări pentru a trimite doar partea întreagă deoarece valoarea în sine nu contează, ci doar momentul în care a fost trimisă
      SerialBT.println(masuratoare);                      //trimiterea prin Bluetooth a măsurători
      maxim_prelucrare_anterioara=0;                      //resetarea variabilei pentru a începe un nou proces de detecție a vârfului accelerației
    }
  }
  delay(85);                                              //întârziere
}

void prelucrare_initiala()                                //prima citire a datelor în cadrul a celor 2 vectori
{
  int nr_elemente =0;
  while(nr_elemente < CAPACITATE_VECTOR + FEREASTRA)      //atâta timp cât nu au fost ambii vectori populați
  {
    sensors_event_t accel;                                //este un tip de dată specific, ce încapsulează date provenite de la senzor 
    imuu.getAccelerometerSensor()->getEvent(&accel);      //ia accelerația din tipul de dată de mai sus
    float acceleratie = sqrt(                             //calculează rezultanta accelerației 
        accel.acceleration.x * accel.acceleration.x +
        accel.acceleration.y * accel.acceleration.y +
        accel.acceleration.z * accel.acceleration.z
    );
    if(nr_elemente<FEREASTRA)                             //primele 10 elemente vor fi memorate exclusiv în primul vector 
    {
      vector_1[poziție_vector1++]= acceleratie;
    }
    else
    {
      if(nr_elemente<CAPACITATE_VECTOR)                   //elementele citite între a 10 si a 30 iterație vor fi memorate în ambii vectori
      {
        vector_1[poziție_vector1++]=acceleratie;
        vector_2[poziție_vector2++]=acceleratie;
      }
      if(nr_elemente>=CAPACITATE_VECTOR && nr_elemente<CAPACITATE_VECTOR + FEREASTRA) //adaugă elemente doar în al doilea vector pentru a avea si el 30 de elemente inițial
      {
        vector_2[poziție_vector1++]=acceleratie;
      }
    }
    nr_elemente++;                                        //incrementarea numărului de elemente
  }
}

float prelucrare_vector()
{
  float maxim_vector1=maxim_vector(vector_1);             //se determină elementul maxim din vectorul 1
  float maxim_vector2=maxim_vector(vector_2);             //se determină elementul maxim din vectorul 2

  //înainte de a returna valoarea maximă dintre cei 2 vectori, este nevoie de citirea în continuare a elementelor
  if(final_vector1==false)                                //înseamnă că vectorul 2 este mai înaintat        
  {
    for(int i=0; i<10; i++)                               //se crează noul vector 1
    {
      vector_1[i]=vector_1[i+20];                         //se păstrează ultimele 10 cele mai recente măsurători din cadrul aceluiași vector 1
      vector_1[i+10]= vector_2[20+i];                     //se completează cu cele 10 măsurători citite ”în avans” din cadrul vectorului 2
    }
    for(int i=20; i< CAPACITATE_VECTOR; i++)              //se parcurge vectorul până la final
    {
      sensors_event_t accel;
      imuu.getAccelerometerSensor()->getEvent(&accel);
      float acceleratie = sqrt(
        accel.acceleration.x * accel.acceleration.x +
        accel.acceleration.y * accel.acceleration.y +
        accel.acceleration.z * accel.acceleration.z
      );
      vector_1[i]=acceleratie;                            //se completează până la finalul vectorului cu noi măsurători
    }
    final_vector1=true;                                   //se setează variabila pentru următoarea iterație prin care ne spuna că în momentul de față, vectorul 1 este mai înaintat
  }
  else                                                    //vectorul 1 conține măsurători mai actuale
  {
    for(int i=0; i<10; i++)                               //se creează noul vector 2
    {
      vector_2[i]=vector_2[i+20];                         //se păstrează ultimele 10 cele mai recente măsurători din cadrul aceluiași vector 2
      vector_2[i+10]= vector_1[i+20];                     //se completează cu cele 10 măsurători citite ”în avans” din cadrul vectorului 1
    }
    for(int i=20; i< CAPACITATE_VECTOR; i++)              //se parcurge vectorul până la final
    {
      sensors_event_t accel;
      imuu.getAccelerometerSensor()->getEvent(&accel);
      float acceleratie = sqrt(
        accel.acceleration.x * accel.acceleration.x +
        accel.acceleration.y * accel.acceleration.y +
        accel.acceleration.z * accel.acceleration.z
      );
      vector_2[i]=acceleratie;                            //se completează până la finalul vectorului cu noi măsurători
    }
    final_vector1=false;                                  //se setează variabila pentru următoarea iterație prin care ne spune că în acest moment, vectorul 2 conține cele mai recente date
  }
  return max(maxim_vector1, maxim_vector2);               //se returnează valoarea maximă din cadrul acestei ferestre de 30 de elemente
}

float maxim_vector(float vector[])            //funcție care returnează valoarea maximă din cadrul unui vector
{
  float maxim=vector[0];                      //se setează ca și valoare maximă inițială primul element
  for(int i=1; i<CAPACITATE_VECTOR; i++)      //parcurgerea elementelor
  {
    if(vector[i]>maxim)                       //dacă se găsește o valoare mai mare decât valoarea maximă găsită până acum
    {
      maxim=vector[i];                        //se actualizează noul maxim
    }
  }
  return maxim;                               //se returnează valoarea maximă din cadrul vectorului
}
#include <Wire.h>
#include <Adafruit_MPU6050.h>
#include <Adafruit_Sensor.h>  
#include <BluetoothSerial.h>

BluetoothSerial SerialBT;
Adafruit_MPU6050 imuu;

#define CAPACITATE_VECTOR 30
float vector_1[CAPACITATE_VECTOR]={0}, vector_2[CAPACITATE_VECTOR]={0};
int nr_elemente=0; //nr de elem din primul buffer
int i=0, j=0;
float  maxim_vector1=0, maxim_vector2=0, maxim=0;
bool start_prelucrare=false, final_vector1=false;
float maxim_prelucrare_anterioara =0; 

void setup() 
{
  SerialBT.begin("ESP_IMU"); 
  Wire.setClock(400000);
  Wire.begin();
  delay(250);
  if (!imuu.begin()) {
  Serial.println("Eroare IMU!");
  while (1);
}
}

void loop()
{
  if(start_prelucrare == false)
  {
    prelucrare_initiala(nr_elemente);
    start_prelucrare=true;
  }
  float rezultat = final_vector();
  if(maxim_prelucrare_anterioara <= rezultat)
  {
    maxim_prelucrare_anterioara=rezultat;
  }
  else
  {
    if((int)maxim_prelucrare_anterioara != (int)rezultat)
    {
      int masuratoare= (int)maxim_prelucrare_anterioara;
      SerialBT.println(masuratoare);
      maxim_prelucrare_anterioara=0;
    }
  }
  delay(85);
}


int prelucrare_initiala(int nr_elemente)
{
  while(nr_elemente<40)
  {
    sensors_event_t accel;
    imuu.getAccelerometerSensor()->getEvent(&accel);
    float acceleratie = sqrt(
        accel.acceleration.x * accel.acceleration.x +
        accel.acceleration.y * accel.acceleration.y +
        accel.acceleration.z * accel.acceleration.z
    );
    if(nr_elemente<10)
    {
      vector_1[i++]= acceleratie;
    }
    else
    {
      if(nr_elemente<30)
      {
        vector_1[i++]=acceleratie;
        vector_2[j++]=acceleratie;
      }
      if(nr_elemente>=30 && nr_elemente<40)
      {
        vector_2[j++]=acceleratie;
      }
    }
    nr_elemente++;

  }
  return nr_elemente; 
}

float final_vector()
{
  float maxim_vector1=maxim_vector(vector_1);
  float maxim_vector2=maxim_vector(vector_2);

  if(final_vector1==false) //cand e gata buffer B, adica (nr_elemente-30)%20 ==0
  {
    for(int i=0; i<10; i++)
    {
      vector_1[i]=vector_1[i+20];
      vector_1[i+10]= vector_2[20+i];
    }
    for(int i=20; i< CAPACITATE_VECTOR; i++)
    {
      sensors_event_t accel;
      imuu.getAccelerometerSensor()->getEvent(&accel);
      float acceleratie = sqrt(
        accel.acceleration.x * accel.acceleration.x +
        accel.acceleration.y * accel.acceleration.y +
        accel.acceleration.z * accel.acceleration.z
      );
      vector_1[i]=acceleratie;
    }
    final_vector1=true;
  }
  else
  {
    for(int i=0; i<10; i++)
    {
      vector_2[i]=vector_2[i+20];
      vector_2[i+10]= vector_1[20+i];
    }
    for(int i=20; i< CAPACITATE_VECTOR; i++)
    {
      sensors_event_t accel;
      imuu.getAccelerometerSensor()->getEvent(&accel);
      float acceleratie = sqrt(
        accel.acceleration.x * accel.acceleration.x +
        accel.acceleration.y * accel.acceleration.y +
        accel.acceleration.z * accel.acceleration.z
      );
      vector_2[i]=acceleratie;
    }
    final_vector1=false;
  }
  return max(maxim_vector1, maxim_vector2);
}

float maxim_vector(float vector[])
{
  float maxim=vector[0];
  for(int i=1; i<=CAPACITATE_VECTOR; i++)
  {
    if(vector[i]>maxim)
    {
      maxim=vector[i];
    }
  }
  return maxim;
}
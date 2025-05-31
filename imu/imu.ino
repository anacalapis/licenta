#include <Wire.h>
#include <Adafruit_MPU6050.h>
#include <Adafruit_Sensor.h>  
#include <BluetoothSerial.h>

BluetoothSerial SerialBT;
Adafruit_MPU6050 imuu;

#define BUFFER_SIZE 30
float buffer1[BUFFER_SIZE]={0}, buffer2[BUFFER_SIZE]={0};
int cnt=0; //nr de elem din primul buffer
int i=0, j=0;
float  max_buff1=0, max_buff2=0, maxim=0;
int start=0, finalA=0;
float maxim_anterior =0; 

void setup() {
  Serial.begin(9600); 
  // imuu.begin();
  SerialBT.begin("ESP_IMU"); 

  Wire.setClock(400000);
  Wire.begin();
  delay(250);
  // Wire.beginTransmission(0x68); //începe o transmisie către dispozitivul I2C cu adresa 0x68,
  // Wire.write(0x6B);             //gestionarea alimentării senzorului
  // Wire.write(0x00);             //senzorul va ieși din modul de repaus și va începe să fie activ
  // Wire.endTransmission();
  if (!imuu.begin()) {
  Serial.println("Eroare IMU!");
  while (1);
}

  // imuu.setAccelerometerRange(MPU6050_RANGE_8_G);
  // imuu.setGyroRange(MPU6050_RANGE_500_DEG);
  // imuu.setFilterBandwidth(MPU6050_BAND_21_HZ);
  //Wire.begin();
}

void loop()
{
  
  if(start==0)
  {
    prelucrare_initiala(cnt);
    start=1;
  }
  float fct = final_vector();
  if(maxim_anterior <= fct)
  {
    maxim_anterior=fct;
  }
  else
  {
    if((int)maxim_anterior != (int)fct)
    {
      int masuratoare= (int)maxim_anterior;
      Serial.println(masuratoare);
      SerialBT.println(masuratoare);
      maxim_anterior=0;
    }
    
  }
  //SerialBT.println("1");
  delay(85);
}


int prelucrare_initiala(int cnt)
{
  while(cnt<40)
  {
    sensors_event_t accel;
    imuu.getAccelerometerSensor()->getEvent(&accel);
    float acceleratie = sqrt(
        accel.acceleration.x * accel.acceleration.x +
        accel.acceleration.y * accel.acceleration.y +
        accel.acceleration.z * accel.acceleration.z
    );
    if(cnt<10)
    {
      buffer1[i++]= acceleratie;
    }
    else
    {
      if(cnt<30)
      {
        buffer1[i++]=acceleratie;
        buffer2[j++]=acceleratie;
      }
      if(cnt>=30 && cnt<40)
      {
        buffer2[j++]=acceleratie;
      }
    }
    cnt++;

  }
  return cnt;
  
}

float final_vector()
{
  float max_buff1=maxim_vector(buffer1);
  float max_buff2=maxim_vector(buffer2);

  if(finalA==0) //cand e gata buffer B, adica (cnt-30)%20 ==0
  {
    for(int i=0; i<20; i++)
    {
      buffer1[i]=buffer1[i+10];
    }
    finalA=1;
  }
  else
  {
    for(int i=0; i<20; i++)
    {
      buffer2[i]=buffer2[i+10];
    }
    finalA=0;
  }
  for(int j=20; j<BUFFER_SIZE; j++)
  {
    sensors_event_t accel;
    imuu.getAccelerometerSensor()->getEvent(&accel);
    float acceleratie = sqrt(
        accel.acceleration.x * accel.acceleration.x +
        accel.acceleration.y * accel.acceleration.y +
        accel.acceleration.z * accel.acceleration.z
    );
    buffer1[j]=acceleratie;
    buffer2[j]=acceleratie;
  }
  cnt=cnt+10; //pt ca s-au citit alte 10 elem noi

  return max(max_buff1, max_buff2);
}

float maxim_vector(float vector[])
{
  float maxim=vector[0];
  for(int i=1; i<=BUFFER_SIZE; i++)
  {
    if(vector[i]>maxim)
    {
      maxim=vector[i];
    }
  }
  return maxim;
}
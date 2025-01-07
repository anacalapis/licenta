#include <Wire.h>
#include <Adafruit_MPU6050.h>
#include <Adafruit_Sensor.h>
#include <MPU6050.h>
#include <BluetoothSerial.h>

BluetoothSerial SerialBT;

#define CRESTERE_VIT_UNGHI 2
#define OSCILATIE 0.1
Adafruit_MPU6050 imuu;
//MPU6050 imuu;
float anterior_vit_unghi = 0;
float curent_vit_unghi =0;
float curent_acceleratie = 0, total=0, medie=0;
int nr_rep=0;
//float acc_x, acc_y, acc_z;
//float giro_x, giro_y, giro_z;

unsigned long currentMillis = 0;
unsigned long previousMillis = 0;

void setup() {
  Serial.begin(9600); 
  imuu.begin();
  SerialBT.begin("ESP_IMU"); 

  Wire.setClock(400000);
  Wire.begin();
  delay(250);
  Wire.beginTransmission(0x68); 
  Wire.write(0x6B);
  Wire.write(0x00);
  Wire.endTransmission();

  // imuu.setAccelerometerRange(MPU6050_RANGE_8_G);
  // imuu.setGyroRange(MPU6050_RANGE_500_DEG);
  // imuu.setFilterBandwidth(MPU6050_BAND_21_HZ);
  //Wire.begin();
}


//se bazeaza pe un buffer circular care tine minte ultimele 10 masuratori

// #define BUFFER_SIZE 10
// float viteza_unghiulara[BUFFER_SIZE] ={0};
// float acceleratie[BUFFER_SIZE] ={0};
// int initializare = 0;
// float medie1=0, medie2=0;
// void loop()
// {
//   if(initializare == 0)
//   {
//     initializare = 1;
//     umplere_buffer(viteza_unghiulara, imuu, 'g');
//   }
//   else
//   {
//     actualizare_vector(viteza_unghiulara, imuu);
//     // Serial.println(viteza_unghiulara[BUFFER_SIZE-1]);
//     medie1= calculare_medie(viteza_unghiulara, 0, BUFFER_SIZE/2);
//     medie2= calculare_medie(viteza_unghiulara, BUFFER_SIZE/2 + 1 , BUFFER_SIZE -1);
//     // Serial.print(" medie 1 ");
//     // Serial.print(medie1);
//     // Serial.print(" medie 2 ");
//     // Serial.println(medie2);
//     if(abs(medie2 - medie1) >CRESTERE_VIT_UNGHI)
//     {
//       SerialBT.print("0"); //presupunem ca incepe arucarea la cos
//       previousMillis = millis();
//       currentMillis = millis();
//       float suma_acc=0;
//       int nr_rep =0;
//       while(currentMillis - previousMillis < 200)
//       {
//         umplere_buffer(acceleratie, imuu, 'a');
//         suma_acc= suma_acc + calculare_medie(acceleratie, 0, BUFFER_SIZE-1);
//         nr_rep ++;
//         currentMillis = millis();
//       }
//       float medie_acc = suma_acc/nr_rep;
//       if ((medie_acc > 9.81 - OSCILATIE) && (medie_acc < 9.81 + OSCILATIE))
//       {
//         SerialBT.print("1");  //validam si asteptam dupa 1 ca sa fie sigur
//         delay(200);
//       }
      
//     }

//   }

// }

// void umplere_buffer(float* vector, Adafruit_MPU6050& imuu, char caracter)
// {
//   for(int i=0; i<BUFFER_SIZE; i++)
//   {
//     if(caracter=='g')
//     {
//       sensors_event_t giro;
//       imuu.getGyroSensor()->getEvent(&giro);
//       vector[i]= sqrt(giro.gyro.x * giro.gyro.x + giro.gyro.y * giro.gyro.y + giro.gyro.z * giro.gyro.z);
//       //Serial.println(vector[i]);
//     }
//     if(caracter=='a')
//     {
//       sensors_event_t acc;
//       imuu.getAccelerometerSensor()->getEvent(&acc);
//       vector[i] = sqrt(acc.acceleration.x * acc.acceleration.x + acc.acceleration.y * acc.acceleration.y + acc.acceleration.z * acc.acceleration.z);
//       //Serial.print("a");
//     }
    
//   }
// }
// void actualizare_vector(float* viteza_unghiulara, Adafruit_MPU6050& imuu)
// {
//   for(int i=0; i<BUFFER_SIZE-1; i++)
//   {
//     viteza_unghiulara[i]=viteza_unghiulara[i+1];
//   }
//   sensors_event_t giro;
//   imuu.getGyroSensor()->getEvent(&giro);
//   viteza_unghiulara[BUFFER_SIZE-1]= sqrt(giro.gyro.x * giro.gyro.x + giro.gyro.y * giro.gyro.y + giro.gyro.z * giro.gyro.z);
// }
// float calculare_medie(float* vector, int stanga, int dreapta)
// {
//   float suma = 0;
//   for(int i= stanga; i<=dreapta; i++)
//   {
//     suma= suma + vector[i];
//   }
//   return suma/(dreapta-stanga+1);
// }




//se bazeaza pe acc x si pe acc y
//merge cam de 6-7 doar ca trimite ambele mesaje cand a aterizat
#define BUFFER_SIZE 20
#define PRAG_ACC_X 13
#define PRAG_ACC_Z 8
#define OSCILATIE 0.2


int bufferIndex = 0;

float acc_x[BUFFER_SIZE]={0};
float acc_z[BUFFER_SIZE]={0};
float accelBuffer[BUFFER_SIZE] = {0};
void loop()
{
  gyro_signals();
  accel_signals();

  actualizare_medie_acc(accelBuffer);
  umplere_acc(acc_x, imuu, 'x');
  
  if(calculeaza_media(accelBuffer, 0, BUFFER_SIZE-1) < (9.81 - OSCILATIE))
  {
    //SerialBT.print("0");
    if((analiza(acc_x) !=0) && (analiza(acc_x) !=1) && (analiza(acc_x) >PRAG_ACC_X ))
    {
      SerialBT.print("1");
      umplere_acc(acc_z, imuu, 'z');
      //delay(50);
      // float varf = analiza(acc_z);
      // SerialBT.print(varf);
      // float media_z = calculeaza_media(acc_z, 0, BUFFER_SIZE - 1);
      //   if (abs(media_z - 9.8) < OSCILATIE) {
      //       SerialBT.print("0"); 
      //   }
      if((analiza(acc_z) !=0))   //&& (analiza(acc_z) !=1)) //&& (analiza(acc_z) > PRAG_ACC_Z))
      //if(calculeaza_media(acc_z, 0, BUFFER_SIZE/2) > calculeaza_media(acc_z, BUFFER_SIZE/2 +1, BUFFER_SIZE-1))
      {
        SerialBT.print("2");
        delay(300);
      }
    
   }
  }
   
    
  
}
void umplere_acc(float* vector, Adafruit_MPU6050& imuu, char axa)
{
  for(int i=0; i<BUFFER_SIZE; i++)
  {
    sensors_event_t acc;
    imuu.getAccelerometerSensor()->getEvent(&acc);
    if(axa=='x')
    {
      vector[i] = acc.acceleration.x;
    }
    if(axa=='z')
    {
      vector[i] = acc.acceleration.z;
    }
  }
}
 void actualizare_medie_acc(float* accelBuffer) 
 {
  sensors_event_t accel;
  imuu.getAccelerometerSensor()->getEvent(&accel);
  float accelMagnitude = sqrt(
      accel.acceleration.x * accel.acceleration.x +
      accel.acceleration.y * accel.acceleration.y +
      accel.acceleration.z * accel.acceleration.z
  );
  accelBuffer[bufferIndex] = accelMagnitude;
  bufferIndex = (bufferIndex + 1) % BUFFER_SIZE;
}


float analiza(float* vector)
{
  for(int i=1; i<BUFFER_SIZE; i++)
  {
    if(vector[i-1]> vector[i])
    {
      for(int j=i; j<BUFFER_SIZE -1; j++)
      {
        if(vector[i]<vector[i+1])
        {
          return 0;   //are mai mult de o "cocoasa" , deci nu ne ajuta
        }
      }
      return vector[i-1];  //cazul in care s-a atins punctul maxim
    }
  }
  return 1; //cazul in care sunt in ordine crescatoare
}
float calculeaza_media(float* vector, int stanga, int dreapta)
{
  int sum =0;
  for(int i=stanga; i<dreapta; i++)
  {
    sum= sum + vector[i];
  }
  return sum/(dreapta-stanga+1);
}
void gyro_signals(void) {
  Wire.beginTransmission(0x68);
  Wire.write(0x1A);
  Wire.write(0x05);
  Wire.endTransmission(); 
  Wire.beginTransmission(0x68);
  Wire.write(0x1B); 
  Wire.write(0x8); 
  Wire.endTransmission(); 
  Wire.beginTransmission(0x68);
  Wire.write(0x43);
  Wire.endTransmission();
  Wire.requestFrom(0x68,6);
}

void accel_signals(void) {
  Wire.beginTransmission(0x68);
  Wire.write(0x1C);
  Wire.write(0x10); 
  Wire.endTransmission();
  Wire.beginTransmission(0x68);
  Wire.write(0x3B);
  Wire.endTransmission();
  Wire.requestFrom(0x68, 6);

}










//afiseaza plotul de la IMU
// void loop()
// {
//   sensors_event_t acc, giro, temp;
//   imuu.getEvent(&acc, &giro, &temp);
//   Serial.print("Acc_X:");Serial.println(acc.acceleration.x);
//   Serial.print("Acc_Y:");Serial.println(acc.acceleration.y);
//   Serial.print("Acc_Z:");Serial.println(acc.acceleration.z);

//   Serial.print("Giro_X:");Serial.println(giro.gyro.x);
//   Serial.print("Giro_Y:");Serial.println(giro.gyro.y);
//   Serial.print("Giro_Z:");Serial.println(giro.gyro.z);
//   delay(100);

// }






// imi place ca trimite fix cand e in aer 0, dar se si blocheaza din cauza variabilei inAir. trimite mult prea multe date..
// #define OSCILATIE 0.1
// #define BUFFER_SIZE 20
// float accelBuffer[BUFFER_SIZE] = {0};
// int bufferIndex = 0;
// bool inAir = false;

// void loop() {
//   // Citește accelerometrul
//   sensors_event_t accel;
//   imuu.getAccelerometerSensor()->getEvent(&accel);

//   // Calculează magnitudinea accelerației
//   float accelMagnitude = sqrt(
//       accel.acceleration.x * accel.acceleration.x +
//       accel.acceleration.y * accel.acceleration.y +
//       accel.acceleration.z * accel.acceleration.z
//   );

//   // Actualizează bufferul
//   accelBuffer[bufferIndex] = accelMagnitude;
//   bufferIndex = (bufferIndex + 1) % BUFFER_SIZE;

//   // Verifică starea mingii
//   detectState(accelBuffer);

//   delay(50); // Interval de citire
// }

// void detectState(float *buffer) {
//   float avgAccel = 0.0;

//   // Calculează media accelerației din buffer
//   for (int i = 0; i < BUFFER_SIZE; i++) {
//     avgAccel += buffer[i];
//   }
//   avgAccel /= BUFFER_SIZE;

//   // Verifică dacă mingea este în aer sau a ajuns jos
//   // 
//   if (!inAir && avgAccel < (9.81 - OSCILATIE)) {
//     // Mingea a fost aruncată
//     inAir = true;
//     SerialBT.print("0");
//   } else if (inAir && avgAccel > (9.81 + OSCILATIE)) {
//     // Mingea a ajuns jos
//     inAir = false;
//     SerialBT.print("1");
    
//   }
// }


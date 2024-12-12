#define SENSOR1_PIN 22 // Pinul pentru primul receptor IR
#define SENSOR2_PIN 23 // Pinul pentru al doilea receptor IR

int score = 0;
int sensor1State= 1;
int sensor2State= 1;
void setup() {
  pinMode(SENSOR1_PIN, INPUT_PULLUP); // Configurează primul pin ca intrare
  pinMode(SENSOR2_PIN, INPUT_PULLUP); // Configurează al doilea pin ca intrare
  Serial.begin(9600);        // Inițializează Monitorul Serial
}

void loop() {
  sensor1State = digitalRead(SENSOR1_PIN); 

  if (sensor1State == 0)
  {
    delay(30);
    sensor2State = digitalRead(SENSOR2_PIN);
    if(sensor2State == 0)
    { 
      score++;
    }
    Serial.print("        senz2 ");
  Serial.print(sensor2State);

  }
  Serial.print("senz1 ");
  Serial.print(sensor1State);
  
  Serial.print("        score ");
  Serial.println(score);
  delay(50); 
}

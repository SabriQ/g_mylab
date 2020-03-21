/*
  this version works without lick port signal.
  water is delivered when infrared_left/right_signal have changed.
*/

int ON = 7;
int pump_left = 10;
int pump_right = 9;
int infrared_left = A2;
int infrared_right = A3;


int left_count = 0;
int right_count = 0;



void setup() {
  // put your setup code here, to run once:
  pinMode(ON, INPUT);  
  pinMode(pump_left, OUTPUT);
  digitalWrite(pump_left, LOW);
  pinMode(pump_right, OUTPUT);
  digitalWrite(pump_right, LOW);

  pinMode(infrared_left, INPUT);
  pinMode(infrared_right, INPUT);
  Serial.begin(9600);
}

float Read_analog(int analog, int times) {
  float sum = 0;
  for (int i = 0; i <= times; i++) {
    int value = analogRead(analog);
    sum = sum + value;
  }
  //Serial.println(sum/times);
  return sum / times;
}

float Read_digital(int digital, int times) {
  float sum = 0;
  for (int i = 0; i <= times; i++) {
    int value = digitalRead(digital);
    sum = sum + value;
  }
  return sum / times;
}

void loop() {
  // put your main code here, to run repeatedly:
  float on_signal = Read_digital(ON, 500);
//  Serial.println(on_signal);
//  float infrared_left_value = Read_analog(infrared_left, 100);
//  float infrared_right_value = Read_analog(infrared_right, 100);
  
//    Serial.print(infrared_left_value);
//    Serial.print("  ");
//    Serial.println(infrared_right_value);
//    delay(100);
  //Serial.print("    ");
  if (on_signal >= 0.90)
  {
    float infrared_left_value = Read_analog(infrared_left, 100);
    float infrared_right_value = Read_analog(infrared_right, 100);
    //
    //          Serial.print(infrared_left_value);
    //        Serial.print("  ");
    //         Serial.println(infrared_right_value);

    if (infrared_left_value >= 500 && left_count <= right_count)
    {
      water_deliver(pump_left,9 );
      left_count = left_count + 1;
      unsigned long current_time = millis();
      Serial.print(current_time);
      Serial.print(" left_count ");
      Serial.println(left_count);
      // wait for 4s to open the door and
    }
    if (infrared_right_value >= 500 && right_count < left_count)
    {
      water_deliver(pump_right, 9);
      right_count = right_count + 1;
      unsigned long current_time = millis();
      Serial.print(current_time);
      Serial.print(" right_count ");
      Serial.println(right_count);
    }
  }
  else
  {
    digitalWrite(pump_left, LOW);
    digitalWrite(pump_right, LOW);
    left_count = 0;//if turn of the on_signal and turn on agian,
    // count will start from 1 again
    right_count = 0;
  }
  // if py_signal comes, left_count = right_count = 0
}



void water_deliver (int pump, int milliseconds) {
  digitalWrite(pump, HIGH);
  delay(milliseconds);
  digitalWrite(pump, LOW);
}

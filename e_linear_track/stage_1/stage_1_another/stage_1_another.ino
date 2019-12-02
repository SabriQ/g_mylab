int an_ON = 6;
int an_pump_left = 7;
int an_pump_right = 8;
int an_infrared_left = A2;
int an_infrared_right = A3;

int an_left_count = 0;
int an_right_count = 0;
void setup() {
  // put your setup code here, to run once:
  pinMode(an_ON, INPUT);
  pinMode(an_pump_left, OUTPUT);
  digitalWrite(an_pump_left, LOW);
  pinMode(an_pump_right, OUTPUT);
  digitalWrite(an_pump_right, LOW);

  pinMode(an_infrared_left, INPUT);
  pinMode(an_infrared_right, INPUT);

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
//  float an_infrared_left_value = Read_analog(an_infrared_left, 100);
//  float an_infrared_right_value = Read_analog(an_infrared_right, 100);
//  Serial.print(an_infrared_left_value);
//  Serial.print("  ");
//  Serial.println(an_infrared_right_value);
//  delay(100);
  float an_on_signal = Read_digital(an_ON, 500);
//    Serial.println(an_on_signal);
//    delay(100);
  ///////////////////// the another side
  if (an_on_signal >= 0.90)
  {
    float an_infrared_left_value = Read_analog(an_infrared_left, 100);
    float an_infrared_right_value = Read_analog(an_infrared_right, 100);
    if (an_infrared_left_value >= 5 && an_left_count <= an_right_count)
    {
      water_deliver(an_pump_left, 6);
      an_left_count = an_left_count + 1;
      unsigned long an_current_time = millis();
      Serial.print(an_current_time);
      Serial.print(" an_left_count ");
      Serial.println(an_left_count);
      // wait for 4s to open the door and
    }
    if (an_infrared_right_value >= 5 && an_right_count < an_left_count)
    {
      water_deliver(an_pump_right, 5);
      an_right_count = an_right_count + 1;
      unsigned long an_current_time = millis();
      Serial.print(an_current_time);
      Serial.print(" an_right_count ");
      Serial.println(an_right_count);
    }
  }
  else
  {
    digitalWrite(an_pump_left, LOW);
    digitalWrite(an_pump_right, LOW);
    an_left_count = 0;//if turn of the on_signal and turn on agian,
    // count will start from 1 again
    an_right_count = 0;
  }
}

void water_deliver (int pump, int milliseconds) {
  digitalWrite(pump, HIGH);
  delay(milliseconds);
  digitalWrite(pump, LOW);
}

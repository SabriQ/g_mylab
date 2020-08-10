int pump_l = A4;
int pump_r = A5;
int pump_led_l = 2;
int pump_led_r = 3;

int ir_l = A0;
int ir_r = A1;
int ir[2];
unsigned long t0=0;
unsigned long t1;
int interval=15000;//15s

void setup() {
  // put your setup code here, to run once:
pinMode(pump_l,OUTPUT);digitalWrite(pump_l,LOW);
pinMode(pump_r,OUTPUT);digitalWrite(pump_r,LOW);
pinMode(pump_led_l,OUTPUT);digitalWrite(pump_led_l,HIGH);
pinMode(pump_led_r,OUTPUT);digitalWrite(pump_led_r,HIGH);
pinMode(ir_l,INPUT);digitalWrite(ir_l,LOW);
pinMode(ir_r,INPUT);digitalWrite(ir_r,LOW);
Serial.begin(9600);
}

void loop() {
  // put your main code here, to run repeatedly:
while(ir[0]==0){Read_ir();}
t1 = millis();
//Serial.println(ir[0]);
if(t1-t0>interval || t0==0){
  Signal(48);
  t0=t1;
  t1=0;}
Read_ir();
}

void Signal(int s){
  /*除了自身控制之外，还可以由python控制输入，比如控制给水
  0 for left pump
  1 for right pump
  */
  switch (s)
  {
    case 48://ll_pump,nosepoke
        water_deliver(pump_l,8);
        digitalWrite(pump_led_r,LOW);
        delay(100);
        digitalWrite(pump_led_r,HIGH);
      break;
      
    case 49://lr_pump
      water_deliver(pump_r,10);
      break;
      
    default:
      break;}
    }
  

void Read_ir(){

    float ir_l_value = Read_analog(ir_l,5);
    float ir_r_value = Read_analog(ir_r,5);
    if (ir_l_value< 800 && ir_l_value>5) {ir[0] = 1;}else{ir[0] = 0;} 
    if (ir_r_value< 400 && ir_r_value>5) {ir[1] = 1;}else{ir[1] = 0;} 

    if (ir[0]+ir[1]==1){
      if (ir[0]==1){
      digitalWrite(pump_led_l,LOW);}
      else{
        digitalWrite(pump_led_r,LOW);
      }
    }else{
      digitalWrite(pump_led_l,HIGH);
      digitalWrite(pump_led_r,HIGH);
    }
//      
//  Serial.print(ir_l_value);Serial.print(" ");
//  Serial.print(ir_r_value);Serial.print(" ");
//  Serial.print(ir[0]);Serial.print(" ");
//  Serial.println(ir[1]); 
//  delay(100);
  }
  
float Read_analog(int analog, int times) {
  float sum = 0;
  for (int i = 1; i <= times; i++) {
    int value = analogRead(analog);
    sum = sum + value;
  }
  //Serial.println(sum/times);
  return sum / times;
}

float Read_digital(int digital, int times) {
  float sum = 0;
  for (int i = 1; i <= times; i++) {
    int value = digitalRead(digital);
    sum = sum + value;
  }
  return sum / times;
}

void water_deliver(int pump, int milliseconds){
  digitalWrite(pump,HIGH);
  delay(milliseconds);
  digitalWrite(pump,LOW);  }

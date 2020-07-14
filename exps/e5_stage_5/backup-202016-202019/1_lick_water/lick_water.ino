#include <Wire.h>
byte send2slave1=0;

int ON = 13;

int pump_left = 5;
int pump_right = 6;

int ir_left = A0;
int ir_enter = A1;
int ir_exit = A2;
int ir_right =A3;
//A4 A5 are used for IIC communication

int ir[4];
float on_signal;
int trial_length = 60;
int i=0;
int Trial_num = 0;


unsigned long left_time;
unsigned long enter_time;
unsigned long exit_time;
unsigned long right_time;
unsigned long r_enter_time;
unsigned long r_exit_time;


void setup() {
  // put your setup code here, to run once:
pinMode(ON,INPUT);
pinMode(pump_left,OUTPUT);digitalWrite(pump_left,LOW);
pinMode(pump_right,OUTPUT);digitalWrite(pump_right,LOW);

pinMode(ir_left,INPUT);digitalWrite(ir_left,LOW);
pinMode(ir_enter,INPUT);digitalWrite(ir_enter,LOW);
pinMode(ir_exit,INPUT);digitalWrite(ir_exit,LOW);
pinMode(ir_right,INPUT);digitalWrite(ir_right,LOW);

Wire.begin();
Serial.begin(9600);
}
////////////////////////////////////////////////
void loop() {
  // put your main code here, to run repeatedly:  

  for (i=0;i<trial_length;i++){
    if (i==0 && on_signal > 0.90){
        Signal(48);Signal(49);
    }
    process(0);//left
    process(1);//enter
    process(2);//exit
    process(3);//right
    process(4);//r_enter
    process(5);//r_exit
    Serial.print("Sum: ");
    Serial.print(Trial_num);Serial.print(" ");
    Serial.print(left_time);Serial.print(" ");
    Serial.print(enter_time);Serial.print(" ");
    Serial.print(exit_time);Serial.print(" ");
    Serial.print(right_time);Serial.print(" ");
    Serial.print(r_enter_time);Serial.print(" ");
    Serial.println(r_exit_time);}
    
   process(6);
}
///////////////////////////////////////////////
/*
void process(int process)
  experiments could be devided into several process:
    process 0: waiting for nosepoke
    process 1: waiting for choice 
void Signal(int py_Signal)
void Read_ir()
void water_deliver(int pump, int milliseconds)
void write2slave(int slave,byte send2slave1)
*/
void process(int p){
  switch (p)
  {
    case 0://waiting for left
      do{Read_ir();}while(ir[0]==0);      
      left_time = millis();
      Serial.println("Stat1: left");
      Signal(48);
      Trial_num =Trial_num+1;
      break;
    case 1://waiting for enter
      do{Read_ir();}while(on_signal >  0.50 && ir[1]==0);
      enter_time = millis();
      Serial.println("Stat2: enter");    
      break;
    case 2://waiting for exit
      do{Read_ir();}while(on_signal >  0.50 &&ir[2]==0);
      exit_time = millis();
      Serial.println("Stat3: exit");
      break;
    case 3://waiting for right
      do{Read_ir();}while(on_signal >  0.50 &&ir[3]==0);
      right_time = millis();
      Serial.println("Stat4: right");
      Signal(49);
      break;
    case 4://waiting for r_enter
      do{Read_ir();}while(on_signal >  0.50 &&ir[2]==0);
      r_enter_time = millis();
      Serial.println("Stat5: r_enter");
      break;      
    case 5://waiting for r_exit
      do{Read_ir();}while(on_signal >  0.50 &&ir[1]==0);
      r_exit_time = millis();
      Serial.println("Stat6: r_exit");
      break;
    case 6://all done
      Serial.println("Stat7: All_done");
      break;
    default:
      break;
  }}  

void Signal(int s){
  /*除了自身控制之外，还可以由python控制输入，比如控制给水*/
  switch (s)
  {
    case 48://left_pump
      water_deliver(pump_left,10);
      break;
    case 49://right_pump
      water_deliver(pump_right,10);
      break;
    default:
    break;}}
  

void Read_ir(){
//int ir_left = A0;
//int ir_enter = A1;
//int ir_exit = A2
//int ir_right =A3;
  on_signal = Read_digital(ON, 10);
//  Serial.print(on_signal);Serial.print(" ");
  if(on_signal >= 0.90){ 
      if (Serial.available()){int py_Signal = Serial.read();Signal(py_Signal);}
      float ir_left_value = Read_analog(ir_left,5);
      float ir_enter_value = Read_analog(ir_enter,5);
      float ir_exit_value = Read_analog(ir_exit,5);      
      float ir_right_value = Read_analog(ir_right,5); 
      
      if (ir_left_value< 80 && ir_left_value>5) {ir[0] = 1;}else{ir[0] = 0;} 
      if (ir_enter_value< 80 ) {ir[1] = 1;}else{ir[1] = 0;} 
      if (ir_exit_value< 80 ) {ir[2] = 1;}else{ir[2] = 0;} 
      if (ir_right_value< 80 && ir_right_value>5) {ir[3] = 1;}else{ir[3] = 0;} 
//
//      Serial.print(ir_left_value);Serial.print(" ");
//      Serial.print(ir_enter_value);Serial.print(" ");
//      Serial.print(ir_exit_value);Serial.print(" ");
//      Serial.print(ir_right_value);Serial.println(" ");
//    
    //  Serial.print(ir[0]);Serial.print(" ");
    //  Serial.print(ir[1]);Serial.print(" ");
    //  Serial.print(ir[2]);Serial.print(" ");
    //  Serial.println(ir[3]);Serial.print(" ");
//      delay(200);
  }else{
    i = 0;
    Trial_num = 0;  
  }  }
//////////////////////////////////////////
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

void write2slave(int slave,byte send2slave1){
  Wire.beginTransmission(slave);
  Wire.write(send2slave1);
  Serial.print("send ");
  Serial.print(send2slave1);
  Serial.print(" to slave");
  Serial.println(slave);
  Wire.endTransmission();}

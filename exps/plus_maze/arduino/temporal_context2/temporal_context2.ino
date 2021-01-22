#include <Wire.h>

int ON=13;
int pump_led=2;
int miniscope_trigger = 8;
int miniscope_event = 7; 

int ir_1 = A0;
int ir_2 = A1;
int ir_3 = A2;
int ir_4 = A3;
int pump_1 = 6;
int pump_2 = 5;
int pump_3= 4;
int pump_4 = 3;

int ir[4];
float on_signal;

int Trial_num = 0;
int current_choice = -1;
int last_choice = -1;
int Choice_class = 0;
int exp_start = 0;//用来指示实验的开始时刻，开关合上之前为0，合上之后变为1,仅用来作为 实验开始时初始化的条件
int mini_interval = 3000; //if it takes less than the mini_interval for continuous licking in the same port, noted as one trial, otherwise, two trials.

unsigned long before_lick;
unsigned long after_lick;
unsigned long interval;
unsigned long nose_poke_time;
unsigned long ir_1_time;
unsigned long ir_2_time;
unsigned long ir_3_time;
unsigned long ir_4_time;

void setup() {
  // put your setup code here, to run once:
pinMode(ON,INPUT);
pinMode(miniscope_trigger,OUTPUT);digitalWrite(miniscope_trigger,LOW);
pinMode(miniscope_event,OUTPUT);digitalWrite(miniscope_event,LOW);

pinMode(pump_1,OUTPUT);digitalWrite(pump_1,LOW);
pinMode(pump_2,OUTPUT);digitalWrite(pump_2,LOW);
pinMode(pump_3,OUTPUT);digitalWrite(pump_3,LOW);
pinMode(pump_4,OUTPUT);digitalWrite(pump_4,LOW);

pinMode(ir_1,INPUT);digitalWrite(ir_1,LOW);
pinMode(ir_2,INPUT);digitalWrite(ir_2,LOW);
pinMode(ir_3,INPUT);digitalWrite(ir_3,LOW);
pinMode(ir_4,INPUT);digitalWrite(ir_4,LOW);

Serial.begin(9600);
}
////////////////////////////////////////////////
void loop() {
  // put your main code here, to run repeatedly:  
//  digitalWrite(miniscope_trigger,HIGH);
  Read_ir();
  if (exp_start==1){
    process(0);
  }
//    process(0);
}
///////////////////////////////////////////////

void process(int p){
  switch (p)
  {
    case 0://strategy
      before_lick = millis();
      while(ir[0]+ir[1]+ir[2]+ir[3]==0){Read_ir();}
      after_lick = millis();
      interval=after_lick-before_lick;
      //jump out of while means lick of any port, current_choice is one of [1,2,3,4], last_choice is one of [-1,1,2,3,4]

      if (current_choice == last_choice && interval < mini_interval ){
        break;
      }else{
        Trial_num =Trial_num+1;
        nose_poke_time = millis();
        miniscope_event_on();
        Serial.print(Trial_num);
        if (last_choice == -1){
          // if the first trial could be any port.
          Signal(current_choice+48);Serial.print(" Stat1: port_");Serial.print(current_choice);Serial.print(" ");
          // if the first trial must be licking port_1
//          if (current_choice == 1){
//            Signal(48);Serial.print(" Stat1: port_1 ");
//          }else{ Serial.print(" Stat0: wrong_choice "); Serial.println(nose_poke_time);break;}
        }else if (current_choice==1 && last_choice==2){
          Signal(49);Serial.print(" Stat1: port_1 ");
        }else if(current_choice==2 && last_choice==4){
          Signal(50);Serial.print(" Stat1: port_2 ");
        }else if(current_choice==3 && last_choice==1){
          Signal(51);Serial.print(" Stat1: port_3 ");
        }else if(current_choice==4 && last_choice==3){
          Signal(52);Serial.print(" Stat1: port_4 ");
        }else{
          Serial.print(" Stat0: port_");Serial.print(current_choice);Serial.print(" ");
        }       
        Serial.println(nose_poke_time);        
        last_choice = current_choice;
        break;
      } 
      break;
      
    default:
      break;
  }}  

void Signal(int s){
  switch (s)
  {
    case 49:
      water_deliver(pump_1,8);
      break;      
    case 50:
      water_deliver(pump_2,6);
      break;      
    case 51:
//      Serial.println("pump3");
      water_deliver(pump_3,8);
      break;      
    case 52:
//      Serial.println("pump4");
      water_deliver(pump_4,8);      
      break;
    default:
      break;}
    }
  

void Read_ir(){
  on_signal = Read_digital(ON, 4);
  
  if (exp_start ==0 && on_signal>=0.90){
    unsigned long exp_start_time=millis();
    digitalWrite(miniscope_trigger,HIGH);
    Serial.print("Stat0: exp_and_miniscope_start ");
    Serial.println(exp_start_time);
    exp_start=1;
  }
    
  if(on_signal >= 0.90){ 
      if (Serial.available()){int py_Signal = Serial.read();Signal(py_Signal);}
      
      float ir_1_value = Read_analog(ir_1,2);
      float ir_2_value = Read_analog(ir_2,2);
      float ir_3_value = Read_analog(ir_3,2);
      float ir_4_value = Read_analog(ir_4,2);
 
      if (ir_1_value< 260 && ir_1_value>5) {ir[0] = 1;current_choice=1;}else{ir[0] = 0;} 
      if (ir_2_value< 260 && ir_2_value>5) {ir[1] = 1;current_choice=2;}else{ir[1] = 0;} 
      if (ir_3_value< 260 && ir_3_value>5) {ir[2] = 1;current_choice=3;}else{ir[2] = 0;}
      if (ir_4_value< 260 && ir_4_value>5) {ir[3] = 1;current_choice=4;}else{ir[3] = 0;}

      if (ir[0]+ir[1]+ir[2]+ir[3]==1){
        digitalWrite(pump_led,LOW);
      }else if(ir[0]+ir[1]+ir[2]+ir[3]>1){
        digitalWrite(pump_led,LOW);
        delay(200);
        digitalWrite(pump_led,HIGH);
        delay(200);
      }else{
        digitalWrite(pump_led,HIGH);
      }      
//      Serial.print(ir_1_value);Serial.print(" ");
//      Serial.print(ir_2_value);Serial.print(" ");
//      Serial.print(ir_3_value);Serial.print(" ");
//      Serial.print(ir_4_value);Serial.print(" ");
//      Serial.print(ir[0]);Serial.print(" ");
//      Serial.print(ir[1]);Serial.print(" ");
//      Serial.print(ir[2]);Serial.print(" ");
//      Serial.println(ir[3]); 
//      delay(100);
  }else{
    Trial_num = 0;  
    current_choice = -1;
    last_choice = -1;
    if (exp_start==1){
      Serial.println("Stat2: Terminated");
    }
    exp_start = 0;
    digitalWrite(pump_led,LOW);
    digitalWrite(miniscope_trigger,LOW);
    
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


void miniscope_event_on(){
  digitalWrite(miniscope_event,HIGH);
  delay(50);
  digitalWrite(miniscope_event,LOW);
}

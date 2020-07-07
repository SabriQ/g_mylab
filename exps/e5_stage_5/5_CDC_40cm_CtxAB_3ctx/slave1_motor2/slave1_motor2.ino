
#include <Wire.h>

int ena=2;
int dir=3;
int pul=4;
//input
int c_0=5;
int c_1=6;
int c_2=7;

byte num=-1;//default to turn off the led 
//variables
int ctx[3];
int c_ctx;

int m_count_start = 0;
int m_change_speed = 0;
int de_i;
int de_init[60]={334,447,430,313,314,327,495,494,422,379,
                399,471,307,437,330,327,490,316,433,397,
                341,313,493,413,455,325,363,498,301,318,
                370,394,450,463,484,345,304,366,435,387,
                443,326,465,395,425,392,446,326,415,489,
                481,382,467,401,370,325,437,489,384,439};


int de_sto;
int de_stop[60] = {21,26,16,23,24,17,15,17,19,26,
              18,22,15,19,29,26,27,25,18,23,
              25,15,22,26,23,22,29,17,19,28,
              18,26,17,29,26,28,19,24,22,20,
              23,24,16,22,23,25,29,21,21,21,
              16,29,25,17,26,20,27,15,28,21};
int de_ste;
int de_step[60]={1,2,2,1,2,1,1,1,1,2,
                  2,2,1,1,1,2,1,1,2,1,
                  1,1,2,2,1,2,1,1,1,2,
                  2,2,1,1,2,2,1,2,2,2,
                  1,2,2,2,1,1,1,1,1,1,
                  2,1,1,1,2,2,1,1,2,1};



void setup() {
  // put your setup code here, to run once:
pinMode(ena,OUTPUT);digitalWrite(ena,HIGH);
pinMode(dir,OUTPUT);digitalWrite(dir,LOW);
pinMode(pul,OUTPUT);digitalWrite(pul,LOW);
pinMode(c_0,INPUT);
pinMode(c_1,INPUT);
pinMode(c_2,INPUT);

Wire.begin(1);
Wire.onReceive(receiveinfo);
Serial.begin(9600);
}

void loop() {  
//  if (Serial.available()){num = Serial.read();}
//  Serial.println(num);
  rec();
}

void rec(){
  switch (num)
  {
    case 0:// go to context 0
     
      Serial.println("move to context 0");
      digitalWrite(ena,LOW);
      digitalWrite(dir,LOW);//leaving motor
      do{Read_ctx();pulse_stepper(pul);}while(ctx[0]==0); 
      m_change_speed = 1;
      Serial.println(" Done");
      digitalWrite(ena,HIGH);
      c_ctx=0;
      Serial.println(c_ctx);
      num=-1;
      break;
      
    case 1://go to context 1
      Serial.println("move to context 1");
      digitalWrite(ena,LOW);
      if (c_ctx==0){       
        digitalWrite(dir,HIGH);//approaching motor
        }
      if (c_ctx==2){  
        digitalWrite(dir,LOW);//leaving motor        
        }else{;}
      do{Read_ctx();pulse_stepper(pul);}while(ctx[1]==0);
      m_change_speed = 1;
      Serial.println(" Done");
      digitalWrite(ena,HIGH);
      c_ctx=1;
      Serial.println(c_ctx);
      num=-1;
      break;

      case 2://go to context 2
      Serial.println("move to context 2");
      digitalWrite(ena,LOW);
      digitalWrite(dir,HIGH);//approaching motor
      do{Read_ctx();pulse_stepper(pul);}while(ctx[2]==0); 
      m_change_speed = 1;
      Serial.println(" Done");
      digitalWrite(ena,HIGH);
      c_ctx=2;
      Serial.println(c_ctx);
      num=-1;
      break;

    default:
      Read_ctx();
      if (ctx[0]==1){
        c_ctx=0;
      }
      if (ctx[1]==1){
        c_ctx=1;
      }
      if (ctx[2]==1){
        c_ctx=2;
      }
      if (ctx[0]==0 && ctx[0]==0 && ctx[0]==0){
        do{Read_ctx();pulse_stepper(pul);}while(ctx[2]==0);
      }
      break;}}

void Read_ctx(){
  if (Read_digital(c_0,5)>0.9){ctx[0]=1;}else{ctx[0]=0;}
  if (Read_digital(c_1,5)>0.9){ctx[1]=1;}else{ctx[1]=0;}
  if (Read_digital(c_2,5)>0.9){ctx[2]=1;}else{ctx[2]=0;}
//  Serial.print(Read_digital(c_0,10));Serial.print(" ");
//  Serial.print(Read_digital(c_1,10));Serial.print(" ");
//  Serial.println(Read_digital(c_2,10));
//  delay(100);
}
void receiveinfo() {  
  while (Wire.available()) {
    num = Wire.read();
//    if(num==0){go_ctx=0;}
//    else if (num==1){go_ctx=1;}
//    else if (num==2){go_ctx=2;}
//    else{go_ctx = go_ctx;}
    
    Serial.print("Recieve: ");
    Serial.println(num);
    }}


void pulse_stepper(int port_out)
{
  if (m_change_speed = 1){
    int de_i = de_init[m_count_start];
    int de_sto = de_stop[m_count_start];
    int de_ste = de_step[m_count_start];
    m_change_speed = 0;
    m_count_start = m_count_start +1;
    if (m_count_start == 60){
      m_count_start = 0;
    }
    m_change_speed=0;
  }
    if (de_i>de_sto){
    de_i = de_i-de_ste;
  }
  digitalWrite(port_out, HIGH);
  delayMicroseconds(de_i);
  digitalWrite(port_out, LOW);
  delayMicroseconds(de_i);
}
float Read_digital(int digital, int times) {
  float sum = 0;
  for (int i = 0; i < times; i++) {
    int value = digitalRead(digital);
    sum = sum + value;
  }
  return sum / times;
}

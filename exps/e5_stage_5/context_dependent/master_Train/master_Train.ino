<<<<<<< HEAD
#include <Wire.h>
byte send2slave1_motor=0;

int ON = 13;

int pump_nose = 4;
int pump_left = 5;
int pump_right = 6;

int ir_nose = A0;
int ir_enter = A1;
int ir_exit = A2;
int ir_left = A3;
int ir_right =A6;
//A4 A5 are used for IIC communication
int ir[5];
float on_signal;
//in trial[60], 0 for context A , 1 for context B
int trial[60] = {0,1,0,1,0,1,1,0,1,0,
                1,0,1,1,0,1,0,0,1,0,
                0,1,1,0,0,1,1,1,0,0,
                1,0,0,1,1,0,1,0,1,0,
                0,1,1,0,0,1,0,1,0,1,
                0,1,0,1,0,1,1,0,1,0};
int trial_length = 60;

int i =0;
int Trial_num = 0;
int left_choice = 0;
int right_choice = 0;
int Choice_class = 0;
int cur_context = 0;


unsigned long nose_poke_time;
unsigned long enter_time;
unsigned long exit_time;
unsigned long choice_time;
unsigned long r_enter_time;
unsigned long r_exit_time;

void setup() {
  // put your setup code here, to run once:
pinMode(ON,INPUT);

pinMode(pump_nose,OUTPUT);digitalWrite(pump_nose,LOW);
pinMode(pump_left,OUTPUT);digitalWrite(pump_left,LOW);
pinMode(pump_right,OUTPUT);digitalWrite(pump_right,LOW);

pinMode(ir_nose,INPUT);digitalWrite(ir_nose,LOW);
pinMode(ir_enter,INPUT);digitalWrite(ir_enter,LOW);
pinMode(ir_exit,INPUT);digitalWrite(ir_exit,LOW);
pinMode(ir_left,INPUT);digitalWrite(ir_left,LOW);
pinMode(ir_right,INPUT);digitalWrite(ir_right,LOW);

//默认切换至context 0 
Signal(51);

Wire.begin();
Serial.begin(9600);
}
////////////////////////////////////////////////
void loop() {
  // put your main code here, to run repeatedly:  
 
  for (i=0;i<trial_length;i++){
    if (i==0){
      Signal(48);//默认第一个trial的开始nose poke给水
    }
    process(0);
    process(1);
    process(2);
    process(3);
    process(4);
    process(5);
    Serial.print("Sum: ");
    Serial.print(Trial_num);Serial.print(" ");
    Serial.print(cur_context);Serial.print(" ");

    Serial.print(left_choice);Serial.print(" ");
    Serial.print(right_choice);Serial.print(" ");
    Serial.print(Choice_class);Serial.print(" ");
    if (Choice_class==1){
      i = i;}
    else if(Choice_class==0){
      i = i-1;}
    else{
      i=0;}   
    Serial.print(nose_poke_time);Serial.print(" ");
    Serial.print(enter_time);Serial.print(" ");
    Serial.print(exit_time);Serial.print(" ");
    Serial.print(choice_time);Serial.print(" ");
    Serial.print(r_enter_time);Serial.print(" ");
    Serial.print(r_exit_time);Serial.print(" ");
  }

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
void write2slave(int slave,byte send2slave1_motor)
*/
void process(int p){
  switch (p)
  {
    case 0://waiting for nosepoke
      do{Read_ir();}while(on_signal < 0.90 || ir[0]==0);//while循环，直到小鼠完成nosepoke
      Signal(48);//给水
      nose_poke_time = millis();//记录时间
      Serial.println("Stat1: nose_poke");//打印stat
      Trial_num =Trial_num+1;//Trial_num 加一      
      if (trial[i]==0){Signal(51);cur_context=0;}else{Signal(52);cur_context=1;}; //切换context       
      break;
    case 1://waiting for enter
      do{Read_ir();}while(on_signal < 0.90 || ir[1]==0);//while循环，直到小鼠enter context
      enter_time = millis();//记录时间
      Serial.println("Stat2: enter");//打印stat 
      break;
    case 2://waiting for exit
      do{Read_ir();}while(on_signal < 0.90 || ir[2]==0);//while循环知道小鼠exit context
      exit_time = millis();//记录时间
      Serial.println("Stat3: exit");//打印stat
      break;
    case 3://waiting for choice
      do{Read_ir();}while(on_signal>0.5 && ir[1]==0 && ir[2]==0); //while 循环，直到小鼠exit context
      choice_time = millis(); //记录时间
      Serial.print("Stat2: choice");//打印stat 
      if (ir[3]==1){
        Serial.print("_l");
        left_choice= left_choice + 1;   
        if (trial[i]==0){
          Signal(49);//左边给水
          Serial.println(" correct");
          Choice_class = 1; }else{
          Serial.println(" wrong");
          Choice_class = 0;}
      }
       else if (ir[4]==1){
        Serial.print("_r") ;
        right_choice=right_choice + 1;          
        if (trial[i]==1){  
          Signal(50);//右边给水
          Serial.println(" correct");
          Choice_class = 1; }else{
          Serial.println(" wrong");
          Choice_class = 0; }   
       }
       else {
          Serial.println(" terminated");
          Choice_class = 2;
       }
      break;
    case 4://waiting for r_enter
      do{Read_ir();}while(on_signal < 0.90 || ir[2]==0);
      r_enter_time = millis();
      Serial.println("Stat5: r_enter");
      break;      
    case 5://waiting for r_exit
      do{Read_ir();}while(on_signal < 0.90 || ir[1]==0);
      r_exit_time = millis();
      Serial.println("Stat6: r_exit");
      break;
    case 6://all done
      Serial.println("Stat7: All_done");
        //打印choice的时间点，判断选择类型，决定是否给水
    default:
      break;
  }}  

void Signal(int s){
  /*除了自身控制之外，还可以由python控制输入，比如控制给水
  0 for nose pump
  1 for left pump
  2 for right pump
  3 for motor, swith to context0
  4 for motor, swith to context1
  */
  switch (s)
  {
    case 48://nose_pump
      water_deliver(pump_nose,5);
      break;
    case 49://left_pump
      water_deliver(pump_left,7);
      break;
    case 50://right_pump
      water_deliver(pump_right,5);
      break;
    case 51://to context0
      //from context1 to context0
      if (cur_context == 1){
        send2slave1_motor=0;
        write2slave(1,send2slave1_motor);
      }       
      break;
    case 52://to context1
      //from context0 to context1
      if (cur_context == 1) {
        send2slave1_motor=2;
        write2slave(1,send2slave1_motor);
      }      
      break;    
    default:
    break;}
    }
  

void Read_ir(){
//int ir_nose = A0;
//int ir_enter = A1;
//int ir_exit = A2
//int ir_left = A3;
//int ir_right =A6;

  on_signal = Read_digital(ON, 20);
//  Serial.print(on_signal);Serial.print(" ");
  if(on_signal >= 0.90){ 
      if (Serial.available()){int py_Signal = Serial.read();Signal(py_Signal);}
      float ir_nose_value = Read_analog(ir_nose,5);
      float ir_enter_value = Read_analog(ir_nose,5);
      float ir_exit_value = Read_analog(ir_nose,5);
      float ir_left_value = Read_analog(ir_left,5);
      float ir_right_value = Read_analog(ir_right,5); 
      if (ir_nose_value< 500 && ir_nose_value>5) {ir[0] = 1;}else{ir[0] = 0;} 
      if (ir_enter_value< 500 && ir_nose_value>5) {ir[1] = 1;}else{ir[1] = 0;}
      if (ir_exit_value< 500 && ir_nose_value>5) {ir[2] = 1;}else{ir[2] = 0;}
      if (ir_left_value< 900 && ir_left_value>5) {ir[3] = 1;}else{ir[3] = 0;} 
      if (ir_right_value< 800 && ir_right_value>5) {ir[4] = 1;}else{ir[4] = 0;} 
    //  Serial.print(ir_nose_value);Serial.print(" ");
    //  Serial.print(ir_enter_value);Serial.print(" ");
    //  Serial.print(ir_exit_value);Serial.print(" ");
    //  Serial.print(ir_left_value);Serial.print(" ");
    //  Serial.print(ir_right_value);Serial.print(" ");
    //  Serial.print(ir[0]);Serial.print(" ");
    //  Serial.print(ir[1]);Serial.print(" ");
    //  Serial.print(ir[2]);Serial.print(" ");
    //  Serial.print(ir[3]);Serial.print(" ");
    //  Serial.println(ir[4]); 
    //  delay(200);
  }else{
    i = 0;
    Trial_num = 0;  
    left_choice = 0;
    right_choice = 0;
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

void write2slave(int slave,byte send2slave1_motor){
  Wire.beginTransmission(slave);
  Wire.write(send2slave1_motor);
  Serial.print("send ");
  Serial.print(send2slave1_motor);
  Serial.print(" to slave");
  Serial.println(slave);
  Wire.endTransmission();}
=======
#include <Wire.h>
byte send2slave1_motor=0;

int ON = 13;

int pump_nose = 4;
int pump_left = 5;
int pump_right = 6;

int ir_nose = A0;
int ir_enter = A1;
int ir_exit = A2;
int ir_left = A3;
int ir_right =A6;
//A4 A5 are used for IIC communication
int ir[5];
float on_signal;
//in trial[60], 0 for context A , 1 for context B
int trial[60] = {0,1,0,1,0,1,1,0,1,0,
                1,0,1,1,0,1,0,0,1,0,
                0,1,1,0,0,1,1,1,0,0,
                1,0,0,1,1,0,1,0,1,0,
                0,1,1,0,0,1,0,1,0,1,
                0,1,0,1,0,1,1,0,1,0};
int trial_length = 60;

int i =0;
int Trial_num = 0;
int left_choice = 0;
int right_choice = 0;
int Choice_class = 0;
int cur_context = 0;


unsigned long nose_poke_time;
unsigned long enter_time;
unsigned long exit_time;
unsigned long choice_time;
unsigned long r_enter_time;
unsigned long r_exit_time;

void setup() {
  // put your setup code here, to run once:
pinMode(ON,INPUT);

pinMode(pump_nose,OUTPUT);digitalWrite(pump_nose,LOW);
pinMode(pump_left,OUTPUT);digitalWrite(pump_left,LOW);
pinMode(pump_right,OUTPUT);digitalWrite(pump_right,LOW);

pinMode(ir_nose,INPUT);digitalWrite(ir_nose,LOW);
pinMode(ir_enter,INPUT);digitalWrite(ir_enter,LOW);
pinMode(ir_exit,INPUT);digitalWrite(ir_exit,LOW);
pinMode(ir_left,INPUT);digitalWrite(ir_left,LOW);
pinMode(ir_right,INPUT);digitalWrite(ir_right,LOW);

//默认切换至context 0 
Signal(51);

Wire.begin();
Serial.begin(9600);
}
////////////////////////////////////////////////
void loop() {
  // put your main code here, to run repeatedly:  
 
  for (i=0;i<trial_length;i++){
    if (i==0){
      Signal(48);//默认第一个trial的开始nose poke给水
    }
    process(0);
    process(1);
    process(2);
    process(3);
    process(4);
    process(5);
    Serial.print("Sum: ");
    Serial.print(Trial_num);Serial.print(" ");
    Serial.print(cur_context);Serial.print(" ");

    Serial.print(left_choice);Serial.print(" ");
    Serial.print(right_choice);Serial.print(" ");
    Serial.print(Choice_class);Serial.print(" ");
    if (Choice_class==1){
      i = i;}
    else if(Choice_class==0){
      i = i-1;}
    else{
      i=0;}   
    Serial.print(nose_poke_time);Serial.print(" ");
    Serial.print(enter_time);Serial.print(" ");
    Serial.print(exit_time);Serial.print(" ");
    Serial.print(choice_time);Serial.print(" ");
    Serial.print(r_enter_time);Serial.print(" ");
    Serial.print(r_exit_time);Serial.print(" ");
  }

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
void write2slave(int slave,byte send2slave1_motor)
*/
void process(int p){
  switch (p)
  {
    case 0://waiting for nosepoke
      do{Read_ir();}while(on_signal < 0.90 || ir[0]==0);//while循环，直到小鼠完成nosepoke
      Signal(48);//给水
      nose_poke_time = millis();//记录时间
      Serial.println("Stat1: nose_poke");//打印stat
      Trial_num =Trial_num+1;//Trial_num 加一      
      if (trial[i]==0){Signal(51);cur_context=0;}else{Signal(52);cur_context=1;}; //切换context       
      break;
    case 1://waiting for enter
      do{Read_ir();}while(on_signal < 0.90 || ir[1]==0);//while循环，直到小鼠enter context
      enter_time = millis();//记录时间
      Serial.println("Stat2: enter");//打印stat 
      break;
    case 2://waiting for exit
      do{Read_ir();}while(on_signal < 0.90 || ir[2]==0);//while循环知道小鼠exit context
      exit_time = millis();//记录时间
      Serial.println("Stat3: exit");//打印stat
      break;
    case 3://waiting for choice
      do{Read_ir();}while(on_signal>0.5 && ir[1]==0 && ir[2]==0); //while 循环，直到小鼠exit context
      choice_time = millis(); //记录时间
      Serial.print("Stat2: choice");//打印stat 
      if (ir[3]==1){
        Serial.print("_l");
        left_choice= left_choice + 1;   
        if (trial[i]==0){
          Signal(49);//左边给水
          Serial.println(" correct");
          Choice_class = 1; }else{
          Serial.println(" wrong");
          Choice_class = 0;}
      }
       else if (ir[4]==1){
        Serial.print("_r") ;
        right_choice=right_choice + 1;          
        if (trial[i]==1){  
          Signal(50);//右边给水
          Serial.println(" correct");
          Choice_class = 1; }else{
          Serial.println(" wrong");
          Choice_class = 0; }   
       }
       else {
          Serial.println(" terminated");
          Choice_class = 2;
       }
      break;
    case 4://waiting for r_enter
      do{Read_ir();}while(on_signal < 0.90 || ir[2]==0);
      r_enter_time = millis();
      Serial.println("Stat5: r_enter");
      break;      
    case 5://waiting for r_exit
      do{Read_ir();}while(on_signal < 0.90 || ir[1]==0);
      r_exit_time = millis();
      Serial.println("Stat6: r_exit");
      break;
    case 6://all done
      Serial.println("Stat7: All_done");
        //打印choice的时间点，判断选择类型，决定是否给水
    default:
      break;
  }}  

void Signal(int s){
  /*除了自身控制之外，还可以由python控制输入，比如控制给水
  0 for nose pump
  1 for left pump
  2 for right pump
  3 for motor, swith to context0
  4 for motor, swith to context1
  */
  switch (s)
  {
    case 48://nose_pump
      water_deliver(pump_nose,5);
      break;
    case 49://left_pump
      water_deliver(pump_left,7);
      break;
    case 50://right_pump
      water_deliver(pump_right,5);
      break;
    case 51://to context0
      //from context1 to context0
      if (cur_context == 1){
        send2slave1_motor=0;
        write2slave(1,send2slave1_motor);
      }       
      break;
    case 52://to context1
      //from context0 to context1
      if (cur_context == 1) {
        send2slave1_motor=2;
        write2slave(1,send2slave1_motor);
      }      
      break;    
    default:
    break;}
    }
  

void Read_ir(){
//int ir_nose = A0;
//int ir_enter = A1;
//int ir_exit = A2
//int ir_left = A3;
//int ir_right =A6;

  on_signal = Read_digital(ON, 20);
//  Serial.print(on_signal);Serial.print(" ");
  if(on_signal >= 0.90){ 
      if (Serial.available()){int py_Signal = Serial.read();Signal(py_Signal);}
      float ir_nose_value = Read_analog(ir_nose,5);
      float ir_enter_value = Read_analog(ir_nose,5);
      float ir_exit_value = Read_analog(ir_nose,5);
      float ir_left_value = Read_analog(ir_left,5);
      float ir_right_value = Read_analog(ir_right,5); 
      if (ir_nose_value< 500 && ir_nose_value>5) {ir[0] = 1;}else{ir[0] = 0;} 
      if (ir_enter_value< 500 && ir_nose_value>5) {ir[1] = 1;}else{ir[1] = 0;}
      if (ir_exit_value< 500 && ir_nose_value>5) {ir[2] = 1;}else{ir[2] = 0;}
      if (ir_left_value< 900 && ir_left_value>5) {ir[3] = 1;}else{ir[3] = 0;} 
      if (ir_right_value< 800 && ir_right_value>5) {ir[4] = 1;}else{ir[4] = 0;} 
    //  Serial.print(ir_nose_value);Serial.print(" ");
    //  Serial.print(ir_enter_value);Serial.print(" ");
    //  Serial.print(ir_exit_value);Serial.print(" ");
    //  Serial.print(ir_left_value);Serial.print(" ");
    //  Serial.print(ir_right_value);Serial.print(" ");
    //  Serial.print(ir[0]);Serial.print(" ");
    //  Serial.print(ir[1]);Serial.print(" ");
    //  Serial.print(ir[2]);Serial.print(" ");
    //  Serial.print(ir[3]);Serial.print(" ");
    //  Serial.println(ir[4]); 
    //  delay(200);
  }else{
    i = 0;
    Trial_num = 0;  
    left_choice = 0;
    right_choice = 0;
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

void write2slave(int slave,byte send2slave1_motor){
  Wire.beginTransmission(slave);
  Wire.write(send2slave1_motor);
  Serial.print("send ");
  Serial.print(send2slave1_motor);
  Serial.print(" to slave");
  Serial.println(slave);
  Wire.endTransmission();}
>>>>>>> 3e5e80d3d802b7544725bcebc321093076ed3631

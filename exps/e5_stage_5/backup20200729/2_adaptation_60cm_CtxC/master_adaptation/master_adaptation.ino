//2_adaptation_40cm_CtxC
#include <Wire.h>
byte send2slave1_motor=0;

int ON = 13;


int pump_ll = 2;
int pump_lr = 3;
int pump_rl = 4;
int pump_rr = 5;
int pump_led = 6;


int ir_ll = A0;
int ir_lr = A1;
int ir_enter = A2;
int ir_exit = A3;
int ir_rl = A6;
int ir_rr =A7;
//A4 A5 are used for IIC communication
int ir[6];
float on_signal;
//in trial[60], 0 for context A , 1 for context B
//half 0 half1
int trial[60] = {0,1,0,1,0,1,1,0,1,0,
                1,0,1,1,0,1,0,0,1,0,
                0,1,1,0,0,1,1,1,0,0,
                1,0,0,1,1,0,1,0,1,0,
                0,1,1,0,0,1,0,1,0,1,
                0,1,0,1,0,1,1,0,1,0};
//35 0; 25 1
//int trial[60] = {0,1,0,1,0,1,0,0,1,0,
//                1,0,1,0,0,1,0,0,1,0,
//                0,1,1,0,0,1,0,1,0,0,
//                1,0,0,1,1,0,1,0,1,0,
//                0,1,1,0,0,0,0,1,0,1,
//                0,1,0,0,0,1,1,0,1,0};
//25 0; 35 1
//int trial[60] = {1,1,0,1,0,1,1,0,1,0,
//                1,0,1,1,0,1,1,0,1,0,
//                0,1,1,0,0,1,1,1,0,1,
//                1,0,0,1,1,0,1,0,1,1,
//                0,1,1,0,1,1,0,1,0,1,
//                0,1,1,1,0,1,1,0,1,0};

int trial_length = 60;

int i =0;
int Trial_num = 0;
int left_choice = 0;
int right_choice = 0;
int Choice_class = 0;
int cur_enter_context = 0;
int cur_exit_context = 0;
int exp_start = 0;//用来指示实验的开始时刻，开关合上之前为0，合上之后变为1,仅用来作为 实验开始时初始化的条件
//,such as, initialization of context, start of miniscope,


unsigned long nose_poke_time;
unsigned long enter_time;
unsigned long exit_time;
unsigned long choice_time;
unsigned long r_enter_time;
unsigned long r_exit_time;
unsigned long exp_start_time;
void setup() {
  // put your setup code here, to run once:
pinMode(ON,INPUT);

pinMode(pump_ll,OUTPUT);digitalWrite(pump_ll,LOW);
pinMode(pump_lr,OUTPUT);digitalWrite(pump_lr,LOW);
pinMode(pump_rl,OUTPUT);digitalWrite(pump_rl,LOW);
pinMode(pump_rr,OUTPUT);digitalWrite(pump_rr,LOW);
pinMode(pump_led,OUTPUT);digitalWrite(pump_led,HIGH);

pinMode(ir_ll,INPUT);digitalWrite(ir_ll,LOW);
pinMode(ir_lr,INPUT);digitalWrite(ir_ll,LOW);
pinMode(ir_enter,INPUT);digitalWrite(ir_enter,LOW);
pinMode(ir_exit,INPUT);digitalWrite(ir_exit,LOW);
pinMode(ir_rl,INPUT);digitalWrite(ir_rl,LOW);
pinMode(ir_rr,INPUT);digitalWrite(ir_rr,LOW);

//默认切换至context 0 

Wire.begin();
Serial.begin(9600);
}
////////////////////////////////////////////////
void loop() {
  // put your main code here, to run repeatedly:  
  Signal(53);cur_enter_context=0;//每次开始的时候归档至 context 0
  for (i=0;i<trial_length;i++){
    process(0);
    process(1);
    process(2);
    process(3);
    process(4);
    process(5);
    Serial.print("Sum: ");
    Serial.print(Trial_num);Serial.print(" ");
    Serial.print(cur_enter_context);Serial.print(" ");
    Serial.print(cur_exit_context);Serial.print(" ");
    Serial.print(Choice_class);Serial.print(" ");
    Serial.print(left_choice);Serial.print(" ");
    Serial.print(right_choice);Serial.print(" ");   
    if (Choice_class==1){
      i = i;}
    else if(Choice_class==0){
      i = i;}
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

void process(int p){
  switch (p)
  {
    case 0://waiting for nosepoke
      do{Read_ir();}while(ir[0]==0);//while循环，直到小鼠完成nosepoke
      Signal(48);//pump_ll给水
      nose_poke_time = millis();//记录时间
      Serial.println("Stat1: nose_poke");//打印stat
      Trial_num =Trial_num+1;//Trial_num 加一      
      break;

    case 1://waiting for enter
      do{Read_ir();}while(on_signal >  0.50 && ir[2]==0);//while循环，直到小鼠enter context
      enter_time = millis();//记录时间
      Serial.println("Stat2: enter");//打印stat 
      break;

    case 2://waiting for exit
      do{Read_ir();}while(on_signal >  0.50 && ir[3]==0);//while循环知道小鼠exit context
      exit_time = millis();//记录时间
      Serial.println("Stat3: exit");//打印stat
      break;

    case 3://waiting for choice
      do{Read_ir();}while(on_signal>0.5 && ir[4]==0 && ir[5]==0); //while 循环，直到小鼠exit context
      choice_time = millis(); //记录时间
      Serial.print("Stat4: choice");//打印stat 
      if (ir[4]==1){
        Serial.print("_l");
        left_choice= left_choice + 1;
        Signal(50);//pump_rl给水   
        if (trial[i]==0){
          Serial.println(" correct");
          Choice_class = 1; }else{
          Serial.println(" wrong");
          Choice_class = 0;}
      }
       else if (ir[5]==1){
        Serial.print("_r") ;
        right_choice=right_choice + 1;          
        if (trial[i]==1){  
          Signal(51);//pump_rr给水
          Serial.println(" correct");
          Choice_class = 1; }else{
          Serial.println(" wrong");
          Signal(50);//pump_rl给水
          Choice_class = 0; }   
       }
       else {
          Serial.println(" terminated");
          Choice_class = 2;
       }

       // Signal(54);
       cur_exit_context=cur_enter_context;
      break;

    case 4://waiting for r_enter
      do{Read_ir();}while(on_signal >  0.50 &&  ir[3]==0);
      r_enter_time = millis();
      Serial.println("Stat5: r_enter");
      break;      

    case 5://waiting for r_exit
      do{Read_ir();}while(on_signal >  0.50 &&  ir[2]==0);
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
  /*除了自身控制之外，还可以由python控制输入，比如控制给水
  0 for ll pump, also named as nosepoke
  1 for lr pump
  2 for rl pump
  3 for rr pump
  4 for motor, switch to context0
  5 for motor, switch to context1
  6 for motor, switch to context2
  */
  switch (s)
  {
    case 48://ll_pump,nosepoke
      if (Trial_num<10){
      water_deliver(pump_ll,8);
      }else{
        water_deliver(pump_ll,8);
      }

//      if (choice_class==1){
//      water_deliver(pump_ll,6);
//      }else{
//      water_deliver(pump_ll,3);
//      }

      break;
    case 49://lr_pump
      water_deliver(pump_lr,10);
      break;
      
    case 50://rl_pump 
        water_deliver(pump_rl,8);
      //如果bias 太严重,增加unprefer这一边的水量一倍
      if (2*left_choice < right_choice || left_choice +10 <=right_choice && Trial_num >= 10){
        water_deliver(pump_rl,8); 
      }
      break;
      
    case 51://rr_pump
      water_deliver(pump_rr,8);      
      if (2*right_choice < left_choice || right_choice +10 <= left_choice && Trial_num >= 10){
        water_deliver(pump_rr,8); 
      }
      break;
      
    case 52://to context0 4
      //from context1 to context0
        send2slave1_motor=0;
        write2slave(1,send2slave1_motor);
      break;
      
    case 53://to context1 5
      //from context0 to context1
        send2slave1_motor=1;
        write2slave(1,send2slave1_motor);
      break;    
    case 54://to context2 6
        send2slave1_motor=2;
        write2slave(1,send2slave1_motor);
        break;
    default:
      break;}
    }
  

void Read_ir(){
  on_signal = Read_digital(ON, 4);
//  Serial.print(on_signal);Serial.print(" ");
    if (exp_start ==0 && on_signal>=0.90){
      Signal(48);//默认第一个trial的开始nose poke给水
      exp_start_time=millis();
      Serial.print("Stat0: exp_start ");
      Serial.println(exp_start_time);
      exp_start=1;
    }
  if(on_signal >= 0.90){ 
      if (Serial.available()){int py_Signal = Serial.read();Signal(py_Signal);}
      float ir_ll_value = Read_analog(ir_ll,5);
      float ir_lr_value = Read_analog(ir_lr,5);
      float ir_enter_value = Read_analog(ir_enter,5);
      float ir_exit_value = Read_analog(ir_exit,5);
      float ir_rl_value = Read_analog(ir_rl,5);
      float ir_rr_value = Read_analog(ir_rr,5); 
      if (ir_ll_value< 800 && ir_ll_value>5) {ir[0] = 1;}else{ir[0] = 0;} 
      if (ir_lr_value< 800 && ir_lr_value>5) {ir[1] = 1;}else{ir[1] = 0;} 
      if (ir_enter_value< 200 ) {ir[2] = 1;}else{ir[2] = 0;}
      if (ir_exit_value< 100) {ir[3] = 1;}else{ir[3] = 0;}
      if (ir_rl_value< 800 && ir_rl_value>5) {ir[4] = 1;}else{ir[4] = 0;} 
      if (ir_rr_value< 800 && ir_rr_value>5) {ir[5] = 1;}else{ir[5] = 0;} 
      if (ir[0]+ir[1]+ir[4]+ir[5]==1){
        digitalWrite(pump_led,LOW);
      }else if(ir[0]+ir[1]+ir[4]+ir[5]==0){
        digitalWrite(pump_led,HIGH);
      }else if(ir[0]+ir[1]+ir[2]+ir[3]+ir[4]+ir[5]>1){
        digitalWrite(pump_led,LOW);
        delay(500);
        digitalWrite(pump_led,HIGH);
        delay(500);
      }else{
        digitalWrite(pump_led,HIGH);
      }
      
//      Serial.print(ir_ll_value);Serial.print(" ");
//      Serial.print(ir_lr_value);Serial.print(" ");
//      Serial.print(ir_enter_value);Serial.print(" ");
//      Serial.print(ir_exit_value);Serial.print(" ");
//      Serial.print(ir_rl_value);Serial.print(" ");
//      Serial.print(ir_rr_value);Serial.print(" ");
//      Serial.print(ir[0]);Serial.print(" ");
//      Serial.print(ir[1]);Serial.print(" ");
//      Serial.print(ir[2]);Serial.print(" ");
//      Serial.print(ir[3]);Serial.print(" ");
//      Serial.print(ir[4]);Serial.print(" ");
//      Serial.println(ir[5]); 
//      delay(200);
  }else{
    i = 0;
    Trial_num = 0;  
    left_choice = 0;
    right_choice = 0;
    exp_start = 0;
    digitalWrite(pump_led,LOW);
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
//  Serial.print("send ");
//  Serial.print(send2slave1_motor);
//  Serial.print(" to slave");
//  Serial.println(slave);
  Wire.endTransmission();}

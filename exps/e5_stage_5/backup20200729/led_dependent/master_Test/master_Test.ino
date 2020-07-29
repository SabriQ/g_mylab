#include <Wire.h>
byte send2slave1_led=0;
int ON = 13;
int pump_nose = 4;
int pump_left = 5;
int pump_right = 6;

int ir_nose = A0;
int ir_left = A1;
int ir_right =A2;
//A4 A5 are used for IIC communication
int ir[3];
float on_signal;
//in trial[60], 0 for left, 1 for right
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
unsigned long nose_poke_time;
unsigned long choice_time;

void setup() {
  // put your setup code here, to run once:
pinMode(ON,INPUT);

pinMode(pump_nose,OUTPUT);digitalWrite(pump_nose,LOW);
pinMode(pump_left,OUTPUT);digitalWrite(pump_left,LOW);
pinMode(pump_right,OUTPUT);digitalWrite(pump_right,LOW);
pinMode(ir_nose,INPUT);digitalWrite(ir_nose,LOW);
pinMode(ir_left,INPUT);digitalWrite(ir_left,LOW);
pinMode(ir_right,INPUT);digitalWrite(ir_right,LOW);
Wire.begin();
Serial.begin(9600);
}
////////////////////////////////////////////////
void loop() {
  // put your main code here, to run repeatedly:  
 
  for (i=0;i<trial_length;i++){
    process(0);
//    Serial.print("|");Serial.print(trial[i]);Serial.print("--");Serial.print(Choice_class);Serial.println("");  
    process(1);
//    Serial.print("-");Serial.print(trial[i]);Serial.print("--");Serial.print(Choice_class);Serial.println("");
    Serial.print("Sum: ");
    Serial.print(Trial_num);Serial.print(" ");
    Serial.print(left_choice);Serial.print(" ");
    Serial.print(right_choice);Serial.print(" ");
    if (Choice_class==1){
      i=i;
      Serial.print("correct ");}
    else if(Choice_class==0){
      i = i;
      Serial.print("wrong ");}
    else{
      i=0;
      Serial.print("terminated ");}   
//     Serial.print("--");Serial.print(i);Serial.println("");
      Serial.print(nose_poke_time);Serial.print(" ");
      Serial.println(choice_time);
     }
   Serial.println("All done!");
}
///////////////////////////////////////////////
/*
void process(int process)
  experiments could be devided into several process:
    process 0: waiting for nosepoke
    process 1: waiting for choice 
void signal(int py_signal)
void Read_ir()
void water_deliver(int pump, int milliseconds)
void write_data(int slave,byte send2slave1_led)
*/
void process(int p){
  switch (p)
  {
    case 0://waiting for nosepoke
      //while循环，直到小鼠完成nosepoke
      do{Read_ir();}while(ir[0]==0);
      
      //打印nosepoke的时间点，Trial_num 加 1
      nose_poke_time = millis();
      Serial.println("Stat1: nose_poke");
      signal(48);
      Trial_num =Trial_num+1;
      
      //如果随机的trial值为0，那么通知slave1_led执行3(flash)；如果随机的trial值为1，那么通知slave1_led执行4(on)；
      if (trial[i]==0){send2slave1_led=3;}else{send2slave1_led=4;}
      write_data(1,send2slave1_led)；
      
      break;

    case 1://waiting for choice           
      //while循环，直到小鼠选择choose left(ir[1]==1) or right (ir[2]==1)，通知led执行5（off）
      do{Read_id();}while(on_signal>0.5 && ir[1]==0 && ir[2]==0);   
      send2slave1_led=5;
      write_data(1,send2slave1_led);      

      //打印choice的时间点，判断选择类型，决定是否给水
      choice_time = millis();    
      Serial.print("Stat2: choice");    
      if (ir[1]==1){
        Serial.print("_l");
        left_choice= left_choice + 1;   
        if (trial[i]==0){
          signal(49);
          Serial.println(" correct");
          Choice_class = 1; }else{
          Serial.println(" wrong");
          Choice_class = 0;}
      }
       else if (ir[2]==1){
        right_choice=right_choice + 1;
        Serial.print("_r") ;  
        if (trial[i]==1){  
          signal(50);
          Serial.println(" correct");
          Choice_class = 1; }else{
          Serial.println(" wrong");
          Choice_class = 0; }   
       }
       else {
          Serial.println(" terminated");
//          Serial.print("on_signal: ");
//          Serial.println(on_signal);
          Choice_class = 2; 
       }
      break;
    default:
      break;
  }}  

void signal(int s){
  /*除了自身控制之外，还可以由python控制输入，比如控制给水*/
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
    case 51://led_flash for ~2s
      send2slave1_led=3;
      write_data(1,send2slave1_led);
      for (int k = 200;k>0;k--){
        Read_ir();
        delay(10);}
      send2slave1_led=5;
      write_data(1,send2slave1_led);
      break;
    case 52: //led_continuous on for ~2s
      send2slave1_led=4;
      write_data(1,send2slave1_led);
      for (int k = 200;k>0;k--){
        Read_ir();
        delay(10);}
      send2slave1_led=5;
      write_data(1,send2slave1_led);
      break;
    case 53: //led_off
      send2slave1_led=5;
      write_data(1,send2slave1_led);
    default:
    break;}}
  

void Read_ir(){
//int ir_nose = A0;
//int ir_left = A1;
//int ir_right =A2;
  on_signal = Read_digital(ON, 20);
//  Serial.print(on_signal);Serial.print(" ");
  if(on_signal >= 0.90){ 
      if (Serial.available()){int py_signal = Serial.read();signal(py_signal);}
      float ir_nose_value = Read_analog(ir_nose,5);
      float ir_left_value = Read_analog(ir_left,5);
      float ir_right_value = Read_analog(ir_right,5); 
      if (ir_nose_value< 500 && ir_nose_value>5) {ir[0] = 1;}else{ir[0] = 0;} 
      if (ir_left_value< 900 && ir_left_value>5) {ir[1] = 1;}else{ir[1] = 0;} 
      if (ir_right_value< 800 && ir_right_value>5) {ir[2] = 1;}else{ir[2] = 0;} 
    //  Serial.print(ir_nose_value);Serial.print(" ");
    //  Serial.print(ir_left_value);Serial.print(" ");
    //  Serial.print(ir_right_value);Serial.print(" ");
    //  Serial.print(ir[0]);Serial.print(" ");
    //  Serial.print(ir[1]);Serial.print(" ");
    //  Serial.println(ir[2]); 
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
void write_data(int slave,byte send2slave1_led){
  Wire.beginTransmission(slave);
  Wire.write(send2slave1_led);
  Serial.print("send ");
  Serial.print(send2slave1_led);
  Serial.print(" to slave");
  Serial.println(slave);
  Wire.endTransmission();}

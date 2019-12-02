int ena=2;
int dir=3;
int pul=4;
int p_ll = 9;//pump at left left lick
int p_lr = 10;//pump at left right lick
int p_rl = 11;//pump at right left lick
int p_rr = 12;//pump at right right lick
//input
int c_A=5;
int c_B=6;
int c_C=7;
int c_D=8;

int ctx[2];
void setup() {
  // put your setup code here, to run once:
pinMode(ena,OUTPUT);digitalWrite(ena,LOW);
pinMode(dir,OUTPUT);digitalWrite(dir,LOW);
pinMode(pul,OUTPUT);digitalWrite(pul,LOW);
pinMode(p_ll,OUTPUT);digitalWrite(p_ll,LOW);
pinMode(p_lr,OUTPUT);digitalWrite(p_lr,LOW);
pinMode(p_rl,OUTPUT);digitalWrite(p_rl,LOW);
pinMode(p_rr,OUTPUT);digitalWrite(p_rr,LOW);
pinMode(c_A,INPUT);int c_A_value = 0;
pinMode(c_B,INPUT);int c_B_value = 0;
pinMode(c_C,INPUT);int c_C_value = 0;
pinMode(c_D,INPUT);int c_D_value = 0;

Serial.begin(9600);
}

void loop() {
  // put your main code here, to run repeatedly:
  if (Serial.available()>0){
    rec_py_signal();  } 
  //Serial.println("000");
}
void pulse_stepper(int port_out, float Freq)
{
  digitalWrite(port_out, HIGH);
  delayMicroseconds(int(float(500000 / 800) / Freq));
  //delayMicroseconds(483);
  digitalWrite(port_out, LOW);
  delayMicroseconds(int(float(500000 / 800) / Freq));
  //delayMicroseconds(483);
}
void water_deliver (int pump, int milliseconds) {
  digitalWrite(pump, HIGH);
  delay(milliseconds);
  digitalWrite(pump, LOW);
}
float Read_digital(int digital, int times) {
  float sum = 0;
  for (int i = 0; i <= times; i++) {
    int value = digitalRead(digital);
    sum = sum + value;
  }
  return sum / times;
}
void Read_ctx(){
  if (Read_digital(c_A,10)>0.9){ctx[0]=1;}else{ctx[0]=0;}
  if (Read_digital(c_B,10)>0.9){ctx[1]=1;}else{ctx[1]=0;}
//  Serial.print(Read_digital(c_A,10));Serial.print(" ");
//  Serial.println(Read_digital(c_B,10));
//  delay(100);
}
void rec_py_signal(){
  int py_signal = Serial.read();  
  switch (py_signal)
  {
    case 48://0 left and right doors go left (approaching motor)
      digitalWrite(ena,LOW);
      digitalWrite(dir,LOW);
      do{Read_ctx();pulse_stepper(pul, 1.5);}while(ctx[0]==0);
      digitalWrite(ena,HIGH);
      break;
    case 49://1
      digitalWrite(ena,LOW);
      digitalWrite(dir,HIGH);
      do{Read_ctx();pulse_stepper(pul, 1.5);}while(ctx[0]==0 && ctx[1]==0);
      digitalWrite(ena,HIGH);
      break;
    case 50://2
      digitalWrite(ena,LOW);
      digitalWrite(dir,LOW);
      do{Read_ctx();pulse_stepper(pul, 1.5);}while(ctx[0]==0 && ctx[1]==0);
      digitalWrite(ena,HIGH);
      break;
    case 51://3
      digitalWrite(ena,LOW);
      digitalWrite(dir,HIGH);
      do{Read_ctx();pulse_stepper(pul, 1.5);}while(ctx[1]==0);
      digitalWrite(ena,HIGH);
      break;
    case 52://4
      water_deliver(p_ll,50);
      break;
    case 53://5
      water_deliver(p_lr,8); 
      break;
    case 54://6
      water_deliver(p_rl,8);
      break;
    case 55://7
      water_deliver(p_rr,8);
      break;
    default:
      break;
  }
}

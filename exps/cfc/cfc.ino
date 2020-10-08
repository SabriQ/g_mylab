int shock = 2; //shock
int led = 3; // led for shock
int laser_y = 6; //laser yellow
int laser_b = 7; // laser blue

int laser_b_s = 0; // laser blue stat

unsigned long starttime;
unsigned long stoptime;
unsigned long looptime;
void setup() {
  // put your setup code here, to run once:
pinMode(shock,OUTPUT);digitalWrite(shock,LOW);
pinMode(led,OUTPUT);digitalWrite(led,LOW);
pinMode(laser_y,OUTPUT);digitalWrite(laser_y,LOW);
pinMode(laser_b,OUTPUT);digitalWrite(laser_b,LOW);
Serial.begin(9600);
}

void loop() {
  // put your main code here, to run repeatedly:
if (Serial.available()>0)
 {
   int py_signal = Serial.read();
   Serial.println(py_signal);
   switch(py_signal)
   {
    case 48://python输入为0（对应ASCII49）shock & led on
      digitalWrite(shock,HIGH);
      digitalWrite(led,HIGH);
      break;
    case 49://python输入为1（对应ASCII50）shock & led off
      digitalWrite(shock,LOW);
      digitalWrite(led,LOW);
      break;
    case 50://python输入为2（对应ASCII51）yellow_laser on
      digitalWrite(laser_y,HIGH);
      break;
    case 51://python输入为3（对应ASCII52）yellow_laser off
      digitalWrite(laser_y,LOW);
      break;
    case 52://python输入为4（对应ASCII51）blue_laser on
      laser_b_s=1;
      break;
    case 53://python输入为5（对应ASCII51）blue_laser off
      laser_b_s=0;
      break;
    default:
      break;
   }
}

if(laser_b_s==1){
  digitalWrite(laser_b,HIGH);
  delay(5);
  digitalWrite(laser_b,LOW);
  delay(45);
}else{
   digitalWrite(laser_b,LOW);
}

}

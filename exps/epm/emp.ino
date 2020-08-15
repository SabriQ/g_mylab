int led = 2;
int laser=3;
int stat=0;

void setup() {
  // put your setup code here, to run once:
pinMode(led,OUTPUT);
pinMode(laser,OUTPUT);
digitalWrite(led,LOW);
digitalWrite(laser,LOW);
Serial.begin(9600);
}

void loop() {
  // put your main code here, to run repeatedly:
//  digitalWrite(laser,HIGH);
//  digitalWrite(led,HIGH);
//  delay(1000);
//  digitalWrite(laser,LOW);
//  digitalWrite(led,LOW);
 
 if (Serial.available()>0)
 {
   int py_signal = Serial.read();
   Serial.println(py_signal);
   if (py_signal == 49)
   {
     stat = 1;
     //Serial.println(stat);
   }
   if (py_signal == 50)
   {
    stat = 0;
   }
 }
 //Serial.println(stat);
 
 if (stat==1)
 {
  //20HZ
  digitalWrite(laser,HIGH);
  digitalWrite(led,HIGH);
  delay(5);
  digitalWrite(laser,LOW);
  delay(45);
 }
 else
 {
 digitalWrite(laser,LOW); 
 digitalWrite(led,LOW);
 }
}

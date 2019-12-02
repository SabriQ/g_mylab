
// dr means door left
// dr means door right
// c means contexts
// ls means left stop
// rs means right stop
int ON = 2;

int dl_pul = 3;
int dl_dir = 4;
int dl_ena = 5;
int dl_ls = 6;
int dl_rs = 7;

int dr_pul = 8;
int dr_dir = 9;
int dr_ena = 10;
int dr_ls = 11;
int dr_rs = 12;

//int c_pul = A0;
//int c_dir = A1;
//int c_ena = A2;
//int c_A = A3;
//int c_B = A4;
//int c_C = A5;
//int c_ls = A6;
//int c_rs = A7;

int c_pul = 14;
int c_dir = 15;
int c_ena = 16;
int c_A = 17;
int c_B = 18;
int c_C = 19;
int c_ls = 20;
int c_rs = 21;
//int dl_ls_value = 0;
//int dl_rs_value = 0;
//int dr_ls_value = 0;
//int dr_rs_value = 0;
//int c_A_value = 0;
//int c_B_value = 0;
//int c_C_value = 0;
//int c_ls_value = 0;
//int c_rs_value = 0;

void setup() {
  // put your setup code here, to run once:
  pinMode(ON, OUTPUT);
  pinMode(dl_pul, OUTPUT);
  pinMode(dl_dir, OUTPUT);
  pinMode(dl_ena, OUTPUT);
  digitalWrite(dl_ena, LOW);
  pinMode(dl_ls, INPUT);
  pinMode(dl_rs, INPUT);

  pinMode(dr_pul, OUTPUT);
  pinMode(dr_dir, OUTPUT);
  pinMode(dr_ena, OUTPUT);
  digitalWrite(dr_ena, LOW);
  pinMode(dr_ls, INPUT);
  pinMode(dr_rs, INPUT);

  pinMode(c_pul, OUTPUT);
  pinMode(c_dir, OUTPUT);
  pinMode(c_ena, OUTPUT);
  digitalWrite(c_ena, LOW);
  pinMode(c_A, INPUT);
  pinMode(c_B, INPUT);
  pinMode(c_C, INPUT);
  pinMode(c_ls, INPUT);
  pinMode(c_rs, INPUT);


  Serial.begin(9600);
}

void loop() {
  // put your main code here, to run repeatedly:

  if (Serial.available() > 0)
  {
    digitalWrite(ON, HIGH);
    rec_py_signal();
    /*
       case 48 0 left and right doors go left
       case 49 1 left and right doors go right

       case 50 2 left door goes left
       case 51 3 left door goes right

       case 52 4 right door goes left
       case 53 5 right door goes right

       case 54 6 move to context A, approaching stepper(left)
       case 55 7 move to context A, leaving stepper(right)

       case 56 8 move to context B, approaching stepper(left)
       case 57 9 move to context B, leaving stepper(right)

       case 97 a stand by for more contexts
       case 98 b stand by
       case 99 c stand by
       case    d stand by
       ... ...
    */
  } else
  {
    digitalWrite(ON, LOW);
  }
}

////// for control one stepper moter
void pulse_stepper(int port_out, float Freq)
{
  digitalWrite(port_out, HIGH);
  delayMicroseconds(int(float(500000 / 800) / Freq));
  //delayMicroseconds(483);
  digitalWrite(port_out, LOW);
  delayMicroseconds(int(float(500000 / 800) / Freq));
  //delayMicroseconds(483);
}
////// for control two stepper motors together
void pulse_steppers(int port_out_A, int port_out_B, float Freq)
{
  digitalWrite(port_out_A, HIGH);
  digitalWrite(port_out_B, HIGH);
  delayMicroseconds(int(float(500000 / 800) / Freq));
  //delayMicroseconds(483);
  digitalWrite(port_out_A, LOW);
  digitalWrite(port_out_B, LOW);
  delayMicroseconds(int((500000 / 800) / Freq));
  //delayMicroseconds(483);
}
////// for recognize all the python signal
void rec_py_signal()
{
  int py_signal = Serial.read();
  switch (py_signal)
  {
    case 48://0 left and right doors go left (approaching motor)
      digitalWrite(dl_dir, LOW);
      digitalWrite(dr_dir, LOW);
      while (1 == 1) {
        int dl_ls_value = digitalRead(dl_ls);
        int dl_rs_value = digitalRead(dl_rs);
        int dr_ls_value = digitalRead(dr_ls);
        int dr_rs_value = digitalRead(dr_rs);
        if (dl_ls_value == 0 && dr_ls_value == 0) {
          pulse_steppers(dl_pul, dr_pul, 3);
        } else if (dl_ls_value == 0 && dr_ls_value == 1) {
          pulse_stepper(dl_pul, 2.8);
        } else if (dl_ls_value == 1 && dr_ls_value == 0) {
          pulse_stepper(dr_pul, 2.8);
        } else {
          digitalWrite(ON, LOW);
          break;
        }
      }
      break;
    case 49://1 left and right doors go right (leaving motor)
      digitalWrite(dl_dir, HIGH);
      digitalWrite(dr_dir, HIGH);
      while (1 == 1) {
        int dl_ls_value = digitalRead(dl_ls);
        int dl_rs_value = digitalRead(dl_rs);
        int dr_ls_value = digitalRead(dr_ls);
        int dr_rs_value = digitalRead(dr_rs);
        if (dl_rs_value == 0 && dr_rs_value == 0) {
          pulse_steppers(dl_pul, dr_pul, 3);
        } else if (dl_rs_value == 0 && dr_rs_value == 1) {
          pulse_stepper(dl_pul, 2.8);
        } else if (dl_rs_value == 1 && dr_rs_value == 0) {
          pulse_stepper(dr_pul, 2.8);
        } else {
          digitalWrite(ON, LOW);
          break;
        }
      }
      break;


    case 50://2 left door goes left
      digitalWrite(dl_dir,LOW);
      while (1 == 1) {        
        int dl_ls_value = digitalRead(dl_ls);
        int dl_rs_value = digitalRead(dl_rs);
        if (dl_ls_value == 0) {
          pulse_stepper(dl_pul, 2.8);
        } else {
          digitalWrite(ON, LOW);
          break;
        }
      }
      break;
    case 51://3 left door goes right
      digitalWrite(dl_dir, HIGH);
      while (1 == 1) {
        int dl_rs_value = digitalRead(dl_rs);
        int dl_ls_value = digitalRead(dl_ls);
        if (dl_rs_value == 0) {
          pulse_stepper(dl_pul, 2.8);
        } else {
          digitalWrite(ON, LOW);
          break;
        }
      }
      break;


    case 52://4 right door goes left
      digitalWrite(dr_dir, LOW);
      while (1 == 1) {
        int dr_ls_value = digitalRead(dr_ls);
        int dr_rs_value = digitalRead(dr_rs);
        if (dr_ls_value == 0) {
          pulse_stepper(dr_pul, 2.8);
        } else {
          digitalWrite(ON, LOW);
          break;
        }
      }
      break;
    case 53://5 right door goes right
      digitalWrite(dr_dir, HIGH);
      while (1 == 1) {
        int dr_ls_value = digitalRead(dr_ls);
        int dr_rs_value = digitalRead(dr_rs);
        if (dr_rs_value == 0) {
          pulse_stepper(dr_pul, 2.8);
        } else {
          digitalWrite(ON, LOW);
          break;
        }
      }
      break;


    case 54:// 6 move to context A, approaching stepper
      digitalWrite(c_dir, LOW); ///////////not sure
      while (1 == 1) {
        int c_A_value = digitalRead(c_A);
        int c_ls_value =  digitalRead(c_ls);
        int c_rs_value =  digitalRead(c_rs);
        //        Serial.print(c_A_value);
        //        Serial.print(" ");
        //        Serial.print(c_ls_value);
        //        Serial.print(" ");
        //        Serial.println(c_rs_value);
        if (c_A_value == 0 && c_ls_value == 0 && c_rs_value == 0) {
          pulse_stepper(c_pul, 2);
        } else {
          digitalWrite(ON, LOW);
          break;
        }
      }
      break;
    case 55://7  move to context A, leaving stepper
      digitalWrite(c_dir, HIGH);
      while (1 == 1) {
        int c_A_value = digitalRead(c_A);
        int c_ls_value =  digitalRead(c_ls);
        int c_rs_value =  digitalRead(c_rs);
        //        Serial.print(c_A_value);
        //        Serial.print(" ");
        //        Serial.print(c_ls_value);
        //        Serial.print(" ");
        //        Serial.println(c_rs_value);
        if (c_A_value == 0 && c_ls_value == 0 && c_rs_value == 0) {
          pulse_stepper(c_pul, 2);
        } else {
          digitalWrite(ON, LOW);
          break;
        }
      }
      break;

    case 56://8 move to context B, approaching stepper
      digitalWrite(c_dir, LOW);
      while (1 == 1) {
        int c_B_value = digitalRead(c_B);
        int c_ls_value =  digitalRead(c_ls);
        int c_rs_value =  digitalRead(c_rs);
        //        Serial.print(c_B_value);
        //        Serial.print(" ");
        //        Serial.print(c_ls_value);
        //        Serial.print(" ");
        //        Serial.println(c_rs_value);
        if (c_B_value == 0 && c_ls_value == 0 && c_rs_value == 0) {
          pulse_stepper(c_pul, 2);
        } else {
          digitalWrite(ON, LOW);
          break;
        }
      }
      break;
    case 57://9 move to context B, leaving stepper
      digitalWrite(c_dir, HIGH);
      while (1 == 1) {
        int c_B_value = digitalRead(c_B);
        int c_ls_value =  digitalRead(c_ls);
        int c_rs_value =  digitalRead(c_rs);
        //        Serial.print(c_B_value);
        //        Serial.print(" ");
        //        Serial.print(c_ls_value);
        //        Serial.print(" ");
        //        Serial.println(c_rs_value);
        if (c_B_value == 0 && c_ls_value == 0 && c_rs_value == 0) {
          pulse_stepper(c_pul, 2);
        } else {
          digitalWrite(ON, LOW);
          break;
        }
      }
      break;
    // ... to add more cases ...//
    default:
      digitalWrite(ON, LOW);
      break;

  }
}

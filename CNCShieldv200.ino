//const int led = 7;
const int dirZpin = 7;
//const int dirY = 6;
const int dirXpin = 5;
const int stepZpin = 4;
//const int stepY = 3;
const int stepXpin = 2;
const int laserpin = 12; //spindle enable
const int stepperEnablepin = 8;
const int limitXAxispin = 9;// in v200 there are no more switches limits, but limits are set by software
const int limitYAxispin = 10;
const int limitZAxispin = 11;
boolean interrupted = false;
int zDir=0; // 0 = inactive -1 = Dir1 +1 = Dir2
int xDir =0;
int stepByStep = 0;
int zStepState = 0;
int xStepState = 0;
//int cptTimer1 = 1250;//16 000 000 /8 /1250 = 1600 interrupts per sec => 800 fronts hauts par sec => 800 1/4 pas par sec = 200 pas par sec = 1 tour / 1 seconde
int cptTimer1 = 5000;
int xSteps=0;
int zSteps=0;
int xPos = 0;
int zPos = 0;
const int maxxPos = 2000;
const int minxPos = -2000;
const int maxzPos = 2000;
const int minzPos = 0;
String cmd;
char s;


void getcmd()
{
  s=(char)Serial.read();
  if (s == '\n') {
    if(cmd=="laseron") {  
      digitalWrite(laserpin, HIGH); 
      Serial.println("Laser is On"); 
    }
    else if(cmd=="laseroff")  {  
      digitalWrite(laserpin, LOW);   
      Serial.println("laser is Off"); 
    }
    else if (cmd == "poweron") {
      digitalWrite(stepperEnablepin,LOW); 
      Serial.println("Power is On");
    }
    else if (cmd == "poweroff") {
      digitalWrite(stepperEnablepin,HIGH); 
      Serial.println("Power is Off");
    }
    else if (cmd=="z+"){
      zDir=1;
      stepByStep = 0;
      Serial.println("Z+");
    }
    else if (cmd=="z-"){
      zDir = -1;
      stepByStep = 0;
      Serial.println("Z-");
    }
    else if (cmd=="x+"){
      xDir =1;
      stepByStep = 0;
      Serial.println("X+");
    }
    else if (cmd=="x-"){
      xDir = -1;
      stepByStep = 0;
      Serial.println("X-");
    }
    else if (cmd=="zoff"){
      zDir = 0;
      stepByStep = 0;
      //zSteps = 0;
      //stepByStep =1;
      Serial.println("Zoff");
    }
    else if (cmd=="xoff"){
      xDir = 0;
      stepByStep = 0;
      //xSteps = 0;
      //stepByStep = 0;
      Serial.println("Xoff");
    }
    else if (cmd.startsWith("move"))
    {
      int indX = cmd.indexOf("x") ;
      int indZ = cmd.indexOf("z");
      String subX = cmd.substring(indX+1);
      String subZ = cmd.substring(indZ+1);
      xSteps =subX.toInt();
      zSteps = subZ.toInt();
      String XMove = "XMove "+String(xSteps);
      String ZMove = "ZMove "+String(zSteps);
      Serial.println(XMove);
      Serial.println(ZMove);
        //xDir = constrain(xSteps-xPos, -1, 1);
        //zDir =constrain(zSteps-zPos,-1,1);
        stepByStep = 1;
      
    }
    else {
      Serial.println("unknown Command :"+cmd);
    }
    // Serial.println(txtMsg); 
    //Serial.println("xpos "+String(xPos));
    //Serial.println("zpos "+String(zPos));
    cmd = "";  
  } 
  else {  
    cmd +=s; 
  }
}

void setup() {
  // initialize serial:
  Serial.begin(115200);

  // initialize timer1 
  noInterrupts();           // disable all interrupts
  TCCR1A = 0;
  TCCR1B = 0;
  TCNT1  = 0;

  OCR1A = cptTimer1;            // compare match register 16MHz/8/1600Hz
  TCCR1B |= (1 << WGM12);   // CTC mode
  TCCR1B |= (1 << CS11);    // /8 prescaler 
  //  TCCR1B |= (1 << CS10);    // 64 prescaler
  TIMSK1 |= (1 << OCIE1A);  // enable timer compare interrupt
  interrupts();             // enable all interrupts
  // make the pins outputs:
  pinMode(laserpin, OUTPUT);
  digitalWrite(laserpin,LOW);
  pinMode(stepperEnablepin, OUTPUT);
  digitalWrite(stepperEnablepin,HIGH); 
  pinMode(dirZpin, OUTPUT);
  pinMode(dirXpin, OUTPUT);
  pinMode(stepZpin, OUTPUT);
  pinMode(stepXpin, OUTPUT);
  pinMode(limitXAxispin,INPUT_PULLUP);
  pinMode(limitZAxispin,INPUT_PULLUP);
  //pinMode(limitXAxis,INPUT);
  //pinMode(limitZAxis,INPUT);
}
void movex(int dir)
{
  digitalWrite(dirXpin,dir);
  if (dir == HIGH)
  {
    if (xPos < maxxPos)
    {
      xPos++;
      xStepState = 1-xStepState;
      digitalWrite(stepXpin,xStepState);
    }
  }
  else // dir == LOW
  {
    if (xPos > minxPos)
    {
      xPos--;
      xStepState = 1-xStepState;
      digitalWrite(stepXpin,xStepState);
    }
  }
}
void movez(int dir)
{
  digitalWrite(dirZpin,dir);
  if (dir == HIGH)
  {
    if (zPos < maxzPos)
    {
      zPos++;
      zStepState = 1-zStepState;
      digitalWrite(stepZpin,zStepState);
    }
  }
    else // dir == LOW
    {
      if (zPos > minzPos)
      {
        zPos--;
        zStepState = 1-zStepState;
        digitalWrite(stepZpin,zStepState);
      }
    }

  }



ISR(TIMER1_COMPA_vect)          //16 000 000 /8 /1250 = 1600 interrupts per sec => 800 fronts hauts par sec => 800 1/4 pas par sec = 200 pas par sec = 1 tour / 1 seconde
{// 1600 interrupts per sec
  if (interrupted){
    return;
  }
  interrupted = true;
  int zDirToWrite = (zDir >0?HIGH:LOW);
  int xDirToWrite = (xDir >0?HIGH:LOW);
  //int zcontact = !digitalRead(limitZAxispin);
  //int xcontact = !digitalRead(limitXAxispin);

  if (stepByStep==0) // We move continuously
  {
    if (zDir !=0)
    {
      int zDirToWrite = (zDir >0?HIGH:LOW);
      movez(zDirToWrite);
    }
    if (xDir !=0)
    {
      int xDirToWrite = (xDir >0?HIGH:LOW);
      movex(xDirToWrite);
    }

  }
  else // StepByStep = 1; we move to nbStpes (x or z) this vare should be named moveto
  {
    if (zSteps > zPos)
    { zDirToWrite = HIGH;
    movez(zDirToWrite);
    }
    else if (zSteps < zPos)
    {
      zDirToWrite = LOW;
      movez(zDirToWrite);
    }
    else {
      zDir = 0;
      //stepByStep = 0;
   }
      
if (xSteps > xPos)
    {
    xDirToWrite = HIGH;
    movex(xDirToWrite);
    }
    else if (xSteps < xPos)
    {
      xDirToWrite = LOW;
      movex(xDirToWrite);
    }
    else {
      xDir = 0;
     // stepByStep = 0;
    }
  }
  
  
  interrupted = false;
  return;
}

void loop() {
  while (Serial.available() > 0) {
    getcmd();

  }
}











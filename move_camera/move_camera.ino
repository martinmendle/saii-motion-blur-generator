// "D:\Program Files\Arduino CLI\arduino-cli.exe" compile -p COM7 --fqbn arduino:avr:uno mover_camara.ino
// "D:\Program Files\Arduino CLI\arduino-cli.exe" upload -p COM7 --fqbn arduino:avr:uno mover_camara.ino
// "D:\Program Files\Arduino CLI\arduino-cli.exe" monitor -p COM7 -c baudrate=9600

const int StepX = 2;
const int DirX = 5;
const int StepY = 3;
const int DirY = 6;
const int horizontal_steps = 25; 
const int vertical_steps = 25*4;

void setup() {
  Serial.begin(9600);
  pinMode(StepX, OUTPUT);
  pinMode(DirX, OUTPUT);
  pinMode(StepY, OUTPUT);
  pinMode(DirY, OUTPUT);
  
  Serial.println("System ready. Use W, A, S, D.");
}

void loop() {
  if (Serial.available() > 0) {
    char command = Serial.read();
    
    // Clear any extra characters (\n or \r) sent by the terminal
    while(Serial.available() > 0) { Serial.read(); }

    if (command == 'w' || command == 'W') {
        Serial.println("Moving up...");
        moveMotor(StepY, DirY, true, vertical_steps);
    } 
    else if (command == 's' || command == 'S') {
        Serial.println("Moving down...");
        moveMotor(StepY, DirY, false, vertical_steps);
    } 
    else if (command == 'a' || command == 'A') {
        Serial.println("Left...");
        moveMotor(StepX, DirX, false, horizontal_steps);
    } 
    else if (command == 'd' || command == 'D') {
        Serial.println("Right...");
        moveMotor(StepX, DirX, true, horizontal_steps);
    }
  }
}

void moveMotor(int stepPin, int dirPin, bool direction, int steps) {
  digitalWrite(dirPin, direction);
  delay(10); // Short pause to let the direction settle
  for(int i = 0; i < steps; i++) {
    digitalWrite(stepPin, HIGH);
    delayMicroseconds(800); // A bit slower to gain torque
    digitalWrite(stepPin, LOW);
    delayMicroseconds(800);
  }
}
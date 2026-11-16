
// CNC Shield Stepper  Control Demo
// Superb Tech
// www.youtube.com/superbtech

// "D:\Program Files\Arduino CLI\arduino-cli.exe" compile -p COM7 --fqbn arduino:avr:uno Movement.ino
// "D:\Program Files\Arduino CLI\arduino-cli.exe" upload -p COM7 --fqbn arduino:avr:uno Movement.ino

const int StepX = 2;
const int DirX = 5;
const int StepY = 3;
const int DirY = 6;

const int step_x = 1;
const int step_y = 2;
const int photos_x = 101;
const int photos_y = 101;

//const int StepZ = 4;
//const int DirZ = 7;
int vertical_counter = 0;
int photo_count = 0;
bool dir_y = true;
bool dir_x = true;
bool first_time = true;
int horizontal_counter = 1;


void setup() {
  Serial.begin(9600);
  pinMode(StepX,OUTPUT);
  pinMode(DirX,OUTPUT);
  pinMode(StepY,OUTPUT);
  pinMode(DirY,OUTPUT);
  //pinMode(StepZ,OUTPUT);
  //pinMode( DirZ,OUTPUT);

}

// In this case it takes a 15x15 grid of photos, but it can be modified to take as many photos as desired
void loop() {
  if (Serial.available() > 0) {
    char option = Serial.read(); // Always read to empty the buffer

    if (photo_count < photos_x*photos_y -1) {
      if (option >= '1' && option <= '9') {
        photo_count++;
        if(horizontal_counter < photos_x) {
          move_horizontal(dir_x, step_x); // Simplified: uses the state of 'dir_y'
          horizontal_counter++;
        } else {
          move_vertical(false, step_y);
          horizontal_counter = 1;
          dir_x = !dir_x;
        }
      }
    } else {
      if (photos_y % 2 == 0){
        // Optional: Tell Python that we are done
        // Serial.println("GRID COMPLETE");
        move_vertical(true, step_y*photos_y);
      } else {
        move_vertical(true, step_y*photos_y);
        move_horizontal(false, step_x*photos_x);
      }
    }
  }
}
 
  


void move_horizontal(bool direction, int steps){
  digitalWrite(DirX, direction);
  for(int x = 0; x<steps; x++) { // loop for 100 steps
    digitalWrite(StepX,HIGH);
    delayMicroseconds(500);
    digitalWrite(StepX,LOW); 
    delayMicroseconds(500);
    }
   delay(1000); // delay for 1 second
}

void move_vertical(bool direction, int steps){
  digitalWrite(DirY, direction);
  for(int x = 0; x<steps; x++) { // loop for 100 steps
    digitalWrite(StepY,HIGH);
    delayMicroseconds(500);
    digitalWrite(StepY,LOW); 
    delayMicroseconds(500);
    }
  delay(1000);
}


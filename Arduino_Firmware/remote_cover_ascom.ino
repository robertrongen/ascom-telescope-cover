#include <Servo.h>

constexpr auto DEVICE_GUID = "b45ba2c9-f554-4b4e-a43c-10605ca3b84d";

constexpr auto COMMAND_PING = "COMMAND:PING";
constexpr auto RESULT_PING = "RESULT:PING:OK:";

constexpr auto COMMAND_INFO = "COMMAND:INFO";
constexpr auto RESULT_INFO = "RESULT:DarkSkyGeek's Telescope Cover Firmware v1.0";

constexpr auto COMMAND_GETSTATE = "COMMAND:GETSTATE";
constexpr auto RESULT_STATE_UNKNOWN = "RESULT:STATE:UNKNOWN";
constexpr auto RESULT_STATE_OPEN = "RESULT:STATE:OPEN";
constexpr auto RESULT_STATE_CLOSED = "RESULT:STATE:CLOSED";

constexpr auto COMMAND_OPEN = "COMMAND:OPEN";
constexpr auto COMMAND_CLOSE = "COMMAND:CLOSE";

constexpr auto ERROR_INVALID_COMMAND = "ERROR:INVALID_COMMAND";

enum CoverState {
  closed,
  opening,
  open,
  closing
} state;

Servo servo;                  // create servo object to control a servo

int angle_closed = 103,       // servo closed position
  angle_open = 35;            // servo open position

char receiveVal = 0;
const int Switch = 9;         // switch input pin

void setup() {
  state = closed;
                              // Initialize serial port I/O.
  Serial.begin(57600);        // activates Serial port
  while (!Serial) {
    ;                         // Wait for serial port to connect. Required for native USB!
  }
  Serial.flush();
                              // Initialize servo.
  servo.write(angle_closed);  // Important: We assume that the cover is in the closed position!
  servo.attach(2);            // attaches the servo on pin 2 to the servo object
  delay(100);
  
  pinMode(Switch, INPUT);     // activates button input
}

void loop() {
  if (digitalRead(Switch) == HIGH) {
//     Serial.println("switch pressed");
    if (state == closed) {
      Serial.println("opencover btn");
      delay(35); // debounce
      openCover();
      return;  // Exit the loop to prevent processing of serial commands
    }
    else if (state == open) {
      Serial.println("closecover btn");
      delay(35); // debounce
      closeCover();
      return;  // Exit the loop to prevent processing of serial commands
    }
  }
  
  if (Serial.available() > 0) {
    String command = Serial.readStringUntil('\n');
    if (command == COMMAND_PING) {
      handlePing();
    }
    else if (command == COMMAND_INFO) {
      sendFirmwareInfo();
    }
    else if (command == COMMAND_GETSTATE) {
      sendCurrentState();
    }
    else if (command == COMMAND_OPEN && state != open) {
      Serial.println("opencover cmd");
      openCover();
    }
    else if (command == COMMAND_CLOSE && state != closed) {
      closeCover();
    }
    else if (command == COMMAND_CLOSE && state == closed) {
      Serial.println("Cover already closed");
    }
    else if (command == COMMAND_OPEN && state == open) {
      Serial.println("Cover already opened");
    } 
    else if (command == COMMAND_PING) {
      handlePing();
    }
    else {
      handleInvalidCommand();
    }
  }
}

void openCover() {
  state = opening;
  Serial.println("ACK:COMMAND:OPEN");
  // Serial.println("Opening the cover");
  int pos = servo.read();
  while(pos > angle_open) {
    servo.write(pos);
    delay(35);
    pos = servo.read()-1;
  }
  state = open;
  Serial.print("Cover is open at position ");
  Serial.println(pos);
}

void closeCover() {
  state = closing;
  Serial.println("ACK:COMMAND:OPEN");
  // Serial.println("Closing the cover");
  int pos = servo.read();
  while(pos < angle_closed) {
    servo.write(pos);
    delay(35);
    pos = servo.read()+1;
  }
  state = closed;
  Serial.print("Cover is closed at position ");
  Serial.println(pos);
}

void handlePing() {
  Serial.print(RESULT_PING);
  Serial.println(DEVICE_GUID);
}

void sendFirmwareInfo() {
  Serial.println(RESULT_INFO);
}

void sendCurrentState() {
  switch (state) {
    case open:
      Serial.println(RESULT_STATE_OPEN);
      break;
    case closed:
      Serial.println(RESULT_STATE_CLOSED);
      break;
    default:
      Serial.println(RESULT_STATE_UNKNOWN);
      break;
  }
}

void handleInvalidCommand() {
  Serial.println(ERROR_INVALID_COMMAND);
}

#include <SPI.h>
#include <MFRC522.h>
#include <Servo.h>

Servo myservo;  // create servo object to control a servo
int val = 0;
String cardID = "0";
unsigned long previousSendTime = 0;

#define SS_PIN 10
#define RST_PIN 5
#define light_sensor 8

#define door_open 0
#define door_closed 80

MFRC522 rfid(SS_PIN, RST_PIN);

void setup() {
  pinMode(light_sensor, INPUT);
  Serial.begin(115200);
  Serial.setTimeout(1);
  SPI.begin(); // init SPI bus
  rfid.PCD_Init(); // init MFRC522
  previousSendTime = millis();
}

void open(){
  // myservo.attach(9);  // attaches the servo on pin 9 to the servo object
  myservo.write(door_open);                  // sets the servo position according to the scaled value
  delay(500);                           // waits for the servo to get there
  myservo.write(door_closed);                  // sets the servo position according to the scaled value
  delay(500);                           // waits for the servo to get there
  // myservo.detach();
}

void servoPosition(int position){
  myservo.attach(9);  // attaches the servo on pin 9 to the servo object
  myservo.write(position);                  // sets the servo position according to the scaled value
  delay(2000);                           // waits for the servo to get there
  myservo.detach();
}
void loop() {
  if (Serial.available() > 0) {
    String incomingString = Serial.readString();
    incomingString.trim();
    if (incomingString.substring(0,1) == "o") {
      servoPosition(incomingString.substring(1).toInt());
    }
  }
  if (millis()  - previousSendTime > 1000) {
    previousSendTime = millis();
    Serial.println("rfid:" + cardID);
    cardID = "0";
  }

  if (rfid.PICC_IsNewCardPresent()) { // new tag is available
    if (rfid.PICC_ReadCardSerial()) { // NUID has been readed
      MFRC522::PICC_Type piccType = rfid.PICC_GetType(rfid.uid.sak);
      cardID = "";
      for (int i = 0; i < rfid.uid.size; i++) {
        cardID += String(rfid.uid.uidByte[i], HEX);
      }
      rfid.PICC_HaltA(); // halt PICC
      rfid.PCD_StopCrypto1(); // stop encryption on PCD
    }
  }
}
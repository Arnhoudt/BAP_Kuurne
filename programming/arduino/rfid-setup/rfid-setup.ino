#include <SPI.h>
#include <MFRC522.h>
#include <Stepper.h> // Include the header file

#define STEPS 32

Stepper stepper(STEPS, 4, 6, 5, 7);
int val = 0;
String cardID = "0";
unsigned long previousSendTime = 0;

#define SS_PIN 10
#define RST_PIN 9
#define light_pin 3
#define smoke_pin 2
#define light_sensor 8

#define door_open 0
#define door_closed 80

MFRC522 rfid(SS_PIN, RST_PIN);

void setup() {
  pinMode(light_pin, OUTPUT);
  pinMode(smoke_pin, OUTPUT);
  digitalWrite(light_pin, LOW); // high = off
  digitalWrite(smoke_pin, LOW); // high = off
  delay(500);
  digitalWrite(light_pin, HIGH); // high = off
  digitalWrite(smoke_pin, HIGH); // high = off
  pinMode(light_sensor, INPUT);
  Serial.begin(115200);
  Serial.setTimeout(1);
  SPI.begin(); // init SPI bus
  rfid.PCD_Init(); // init MFRC522
  previousSendTime = millis();
  stepper.setSpeed(200);
  open();
}

void open(){
  stepper.step(-600);
  stepper.step(400);
}

void servoPosition(int position){
  if(position < 45) { // fixing legacy code
    stepper.step(-600);
  } else {
    stepper.step(400);
  }
}
void loop() {
  if (Serial.available() > 0) {
    String incomingString = Serial.readString();
    incomingString.trim();
    if (incomingString.substring(0,1) == "o") { // open door
      servoPosition(incomingString.substring(1).toInt());
    }
    // This code is scratch for the future and DOES NOT WORK YET (it's not even close)
    if (incomingString.substring(0,1) == "d") { // decoration
      digitalWrite(light_pin, incomingString.substring(1,2) == "1" ? HIGH : LOW);
      digitalWrite(smoke_pin, incomingString.substring(1,2) == "1" ? HIGH : LOW);
    }
    // if (incomingString.substring(0,1) == "s") {
    //   digitalWrite(smoke_pin, incomingString.substring(1,2));
    // }
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
#include <SPI.h>
#include <MFRC522.h>
#include <Servo.h>

Servo myservo;  // create servo object to control a servo

#define SS_PIN 10
#define RST_PIN 5

MFRC522 rfid(SS_PIN, RST_PIN);

void setup() {
  Serial.begin(9600);
  Serial.setTimeout(1);
  SPI.begin(); // init SPI bus
  rfid.PCD_Init(); // init MFRC522

  Serial.println("Tap RFID/NFC Tag on reader");
}

void loop() {
  if (rfid.PICC_IsNewCardPresent()) { // new tag is available
    if (rfid.PICC_ReadCardSerial()) { // NUID has been readed
      MFRC522::PICC_Type piccType = rfid.PICC_GetType(rfid.uid.sak);
      //Serial.print("RFID/NFC Tag Type: ");
      //Serial.println(rfid.PICC_GetTypeName(piccType));

      // print NUID in Serial Monitor in the hex format
      for (int i = 0; i < rfid.uid.size; i++) {
        // Serial.print(rfid.uid.uidByte[i] < 0x10 ? " 0" : " ");
        Serial.print(rfid.uid.uidByte[i], HEX);
      }
      Serial.println();
        myservo.attach(9);  // attaches the servo on pin 9 to the servo object
        myservo.write(90);                  // sets the servo position according to the scaled value
        delay(1500);                           // waits for the servo to get there
        myservo.write(0);                  // sets the servo position according to the scaled value
        delay(1500);                           // waits for the servo to get there
        myservo.detach();

      rfid.PICC_HaltA(); // halt PICC
      rfid.PCD_StopCrypto1(); // stop encryption on PCD
    }
  }
}
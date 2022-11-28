# Reading RFID tags
## What are the tags used for
I want to be able to distinguish bottles using RFID tags. These will be placed at the bottom of the bottle. I will use an Arduino and an RFID reader to send the ID's using the serial communication.

## The RFID-RC522
The RFID-RC522 reader I will be using is a common RFID reader found in almost every starter Arduino package. Therefor finding code that works is pretty easy. The only downside to this reader is that the max range is between 3 and 5 cm which we will have to take into account when designing the build.

## Start coding
### Reading the RFID tag with an arduino
To get started I used this code as a base: https://arduinogetstarted.com/tutorials/arduino-rfid-nfc

``` cpp
#include <SPI.h>
#include <MFRC522.h>

#define SS_PIN 10
#define RST_PIN 5

MFRC522 rfid(SS_PIN, RST_PIN);

void setup() {
  Serial.begin(9600);
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
      Serial.print("UID:");
      for (int i = 0; i < rfid.uid.size; i++) {
        Serial.print(rfid.uid.uidByte[i] < 0x10 ? " 0" : " ");
        Serial.print(rfid.uid.uidByte[i], HEX);
      }
      Serial.println();

      rfid.PICC_HaltA(); // halt PICC
      rfid.PCD_StopCrypto1(); // stop encryption on PCD
    }
  }
}
```
The only modification I had to make to get started was to only send the ID of the card. And comment out the other prints.
```cpp
Serial.print(rfid.uid.uidByte[i], HEX);
```
Since the code already uses Serial to send it to the Serial monitor there really was no extra need for me to change this for the test setup.

### Receiving the tag in python
Here I will have to write a little more code.
First we want to connect to the arduino.
Therefor we have to import the serail and the serial list_ports libraries.
``` python
import serial
import serial.tools.list_ports
```
To check if the arduino is connected to the computer we can loop over all the ports and check if one of them has the same ID of the arduino we are using.
``` python
arduino = None

for port in list(serial.tools.list_ports.comports()):
    if port[2].startswith('USB VID:PID=1A86:7523'):
        print("Arduino found on port: " + port[0])
        arduino = serial.Serial(port=port[0], baudrate=9600, timeout=.1)

if arduino is None:
    print("No arduino has been found")
```
Now we are able to read what the arduino sends.
``` python
while True:
    value = arduino.readline().decode().strip()
    if value:
        print(value)
```
Since we want to map the RFID id's to a year we can make a map which translates these values
```python
cardMap = {
    "53D17233": 1810,
    "AB65C61B": 1815,
    "6359B733": 1847,
    "53B72233": 1888,
    "135CA33": 1950,
}
```
We can change the code above to display the correct year that matches the ID
```python!
while True:
    value = arduino.readline().decode().strip()
    if value:
        if value in cardMap:
            print(cardMap[value])
        else:
            print("Unknown card + " + value)
```
That's it for the test setup of the RFID reader

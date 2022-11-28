# Using the RFID tag to play a video
To playback video I use openCV this is an extremely versatile and fast library created in 2000. I used it because it is relatively easy and I might want to add computer vision to make the video interactive if I have extra time.
## The setup
We start by importing cv2 and MediaPlayer for video and audio respectively.
```python!
import cv2
from ffpyplayer.player import MediaPlayer
```
To we now need to create a 800x600 window on which we will draw our video as an image sequence.
```python!
cv2.namedWindow("900 jaar Kuurne", cv2.WND_PROP_FULLSCREEN)
cv2.resizeWindow("900 jaar Kuurne",(800,600)); 
```
Before we start the program cycle we also need to define:
* arduinoValue which will hold the send data of the arduino
* video which will hold the cv player
* player which will hold the MediaPlayer

For now they will be None. We could opt to not do this and check if the variable is undefined.
We will also add a video map and a key map. The video map will map a year to a video and the key map will map a keyboard key to a year. This will be used to debug without an RFID reader.
```python!
keyMap = {
    ord("a"): 1810,
    ord("s"): 1815,
    ord("d"): 1847,
    ord("f"): 1888,
    ord("g"): 1950,
}

videoMap = {
    1810: "./videos/1810.mp4",
    1815: "./videos/1815.mp4",
    1847: "./videos/1847.mp4",
    1888: "./videos/1888.mp4",
    1950: "./videos/1950.mp4",
} 
```
If we combine this with the arduino code from the previous post we get this
```python!
import serial
import serial.tools.list_ports
import cv2
from ffpyplayer.player import MediaPlayer

cardMap = {
    "53D17233": 1810,
    "AB65C61B": 1815,
    "6359B733": 1847,
    "53B72233": 1888,
    "135CA33": 1950,
}

keyMap = {
    ord("a"): 1810,
    ord("s"): 1815,
    ord("d"): 1847,
    ord("f"): 1888,
    ord("g"): 1950,
}

videoMap = {
    1810: "./videos/1810.mp4",
    1815: "./videos/1815.mp4",
    1847: "./videos/1847.mp4",
    1888: "./videos/1888.mp4",
    1950: "./videos/1950.mp4",
} 

arduino = None

for port in list(serial.tools.list_ports.comports()):
    if port[2].startswith('USB VID:PID=1A86:7523'):
        print("Arduino found on port: " + port[0])
        arduino = serial.Serial(port=port[0], baudrate=9600, timeout=.1)

if arduino is None:
    print("No arduino has been found")

# while True:
#     value = arduino.readline().decode().strip()
#     if value:
#         if value in cardMap:
#             print(cardMap[value])
#         else:
#             print("Unknown card + " + value)
video = None
player = None
arduinoValue = None
cv2.namedWindow("900 jaar Kuurne", cv2.WND_PROP_FULLSCREEN)
cv2.resizeWindow("900 jaar Kuurne",(800,600)); 
```

## The program cycle
The pytonic way to create this is using while True and breaking out if you need to, you may not like this but that is the official recommended way so its what I use.
We need to check if there is an arduino connected and if it has data to send.
```python!
if arduino and arduino.in_waiting > 0:
    arduinoValue = arduino.readline().decode().strip()
```
Now we will write they keyboard debug system.
If the Key is q the program will quit
If the Key is in the keymap it will play the matching video and audio
```python!
    key = cv2.waitKey(28) & 0xFF
    if key == ord("q"):
        break
    if key in keyMap:
        url = videoMap[keyMap[key]]
        video=cv2.VideoCapture(url)
        player = MediaPlayer(url)

```

We also need to get the value from the arduino and play the video accordingly
```python!
if arduinoValue:
    if arduinoValue in cardMap:
        url = videoMap[cardMap[arduinoValue]]
        video=cv2.VideoCapture(url)
        player = MediaPlayer(url)
    else:
        print("Unknown card + " + arduinoValue)
    arduinoValue = None
```
If there is a video defined we grab the video frame and the audio frame
```python!
if video:
    grabbed, frame=video.read()
    audio_frame, val = player.get_frame()
```
If this results in grabbed being false we know that the video has ended and we can release the video
```python!
if video is not None and not grabbed:
    video.release()
    video = None
    player = None
```
We can now display a default image which will tell the user that they need to scan another bottle
```python!
if video is None:
    frame = cv2.imread('./screens/default.png')
```
To show the video frame and play the audio frame we need to use this.
```python!
    cv2.imshow("900 jaar Kuurne", frame)
    if player is not None and val != 'eof' and audio_frame is not None:
        #audio
        img, t = audio_frame
```

To cleanly exit the program we might also want to add this after the while loop
```python!
cv2.destroyAllWindows()
```
If we combine everything we get this
```python=
import serial
# import time
import serial.tools.list_ports

# importing libraries
import cv2
from ffpyplayer.player import MediaPlayer


cardMap = {
    "53D17233": 1810,
    "AB65C61B": 1815,
    "6359B733": 1847,
    "53B72233": 1888,
    "135CA33": 1950,
}

keyMap = {
    ord("a"): 1810,
    ord("s"): 1815,
    ord("d"): 1847,
    ord("f"): 1888,
    ord("g"): 1950,
}

videoMap = {
    1810: "./videos/1810.mp4",
    1815: "./videos/1815.mp4",
    1847: "./videos/1847.mp4",
    1888: "./videos/1888.mp4",
    1950: "./videos/1950.mp4",
} 

arduino = None

for port in list(serial.tools.list_ports.comports()):
    if port[2].startswith('USB VID:PID=1A86:7523'):
        print("Arduino found on port: " + port[0])
        arduino = serial.Serial(port=port[0], baudrate=9600, timeout=.1)

if arduino is None:
    print("No arduino has been found")

video = None
player = None
arduinoValue = None

cv2.namedWindow("900 jaar Kuurne", cv2.WND_PROP_FULLSCREEN)
cv2.resizeWindow("900 jaar Kuurne",(800,600)); 
# cv2.setWindowProperty("900 jaar Kuurne",cv2.WND_PROP_FULLSCREEN,cv2.WINDOW_FULLSCREEN)

while True:
    if arduino and arduino.in_waiting > 0:
            arduinoValue = arduino.readline().decode().strip()
    key = cv2.waitKey(28) & 0xFF
    if key == ord("q"):
        break
    
    if arduinoValue:
        if arduinoValue in cardMap:
            url = videoMap[cardMap[arduinoValue]]
            video=cv2.VideoCapture(url)
            player = MediaPlayer(url)
        else:
            print("Unknown card + " + arduinoValue)
        arduinoValue = None

    if key in keyMap:
        url = videoMap[keyMap[key]]
        video=cv2.VideoCapture(url)
        player = MediaPlayer(url)

    if video:
        grabbed, frame=video.read()
        audio_frame, val = player.get_frame()
    
    if video is not None and not grabbed:
        video.release()
        video = None
        player = None      
    
    if video is None:
        frame = cv2.imread('./screens/default.png')

    cv2.imshow("900 jaar Kuurne", frame)
    if player is not None and val != 'eof' and audio_frame is not None:
        #audio
        img, t = audio_frame

cv2.destroyAllWindows()
```

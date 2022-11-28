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
# cv2.setWindowProperty("900 jaar Kuurne",cv2.WND_PROP_FULLSCREEN,cv2.WINDOW_FULLSCREEN)

while True:
    if arduino:
        if arduino.in_waiting > 0:
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


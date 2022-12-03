from multiprocessing import Process
from flask import Flask, render_template, request #importing the module

import serial
# import time
import sys
import time
# importing libraries
import cv2
from ffpyplayer.player import MediaPlayer
import re
from lib import ArduinoApi

IS_NUMBER_REGEX = '^[0-9]+$'

app=Flask(__name__) #instantiating flask object

arduino = None
video = None
player = None
arduinoValue = None

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

@app.route('/') #defining a route in the application
def func(): #writing a function to be executed 
       return render_template("index.html")

@app.route('/servo', methods = ['POST'])
def setServo():
    json = request.get_json()
    print(json)
    if "deg" in json:
        deg = json["deg"]
        if re.search(IS_NUMBER_REGEX, deg):
            return arduino.api(value=deg, target="servo", method="write")
        else:
            return "Deg should be a number", 400
    else:
        return "You should specify the angle in a variable called deg", 400

@app.route('/output', methods = ['get'])
def getSerialOutput():
    pass


def flask_loop():
    global keyMap
    global videoMap
    global video
    global player
    global arduinoValue
    
    while True:
        key = cv2.waitKey(28) & 0xFF
        if key == ord("q"):
            break

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


if __name__=='__main__': #calling  main 
    arduino = ArduinoApi.ArduinoApi()

    cv2.namedWindow("900 jaar Kuurne", cv2.WND_PROP_FULLSCREEN)
    cv2.resizeWindow("900 jaar Kuurne",(800,600)); 

    if arduino is None:
        print("No arduino has been found")
    app.debug=True #setting the debugging option for the application instance
    p = Process(target=flask_loop)
    p.start()
    app.run(port="5001",use_reloader=False) #launching the flask's integrated development webserver
    p.join()

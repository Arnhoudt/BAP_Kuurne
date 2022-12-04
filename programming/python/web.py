from multiprocessing import Process, Array, Value
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

video = None
player = None

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
    global webApiRequests
    global webApiRequestsWritePointer
    json = request.get_json()
    if "deg" in json:
        deg = json["deg"]
        if re.search(IS_NUMBER_REGEX, deg):
            stringToAdd = bytes(str('servo:' + deg+'\n'), 'utf-8')
            for i in range(len(stringToAdd)):
                webApiRequests[webApiRequestsWritePointer.value] = stringToAdd[i]
                webApiRequestsWritePointer.value += 1
                if webApiRequestsWritePointer.value >= len(webApiRequests):
                        webApiRequestsWritePointer.value = 0
            return "ok"
        else:
            return "Deg should be a number", 400
    else:
        return "You should specify the angle in a variable called deg", 400

@app.route('/output', methods = ['get'])
def getSerialOutput():
    return "not implemented yet", 501
    # return arduino.api(method="read")


def flask_loop(webApiRequests, webApiRequestsReadPointer):
    global keyMap
    global videoMap
    global video
    global player

    arduino = ArduinoApi.ArduinoApi()
    if arduino is None:
        print("No arduino has been found")
    lastEpoch = time.time()
    while True:
        # every second, it reads and processes the web api requests and the serial requests
        if time.time() - lastEpoch > 0.1:
            lastEpoch = time.time()
            tick(arduino, webApiRequests, webApiRequestsReadPointer)
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


def tick(arduino, webApiRequests, webApiRequestsReadPointer):
    value = arduino.api(method="read")
    print(value)
    handleWebApiRequests(arduino, webApiRequests, webApiRequestsReadPointer)


def handleWebApiRequests(arduino, webApiRequests, webApiRequestsReadPointer):
    while webApiRequests[webApiRequestsReadPointer.value] != b'\x00':
        request = b''
        startPoint = webApiRequestsReadPointer.value
        while webApiRequests[webApiRequestsReadPointer.value] != b'\n':
            request += webApiRequests[webApiRequestsReadPointer.value]
            webApiRequestsReadPointer.value += 1
            if webApiRequestsReadPointer.value >= len(webApiRequests):
                webApiRequestsReadPointer.value = 0
        endPoint = webApiRequestsReadPointer.value
        webApiRequestsReadPointer.value += 1
        if webApiRequestsReadPointer.value >= len(webApiRequests):
                webApiRequestsReadPointer.value = 0
        request = request.decode("utf-8").split(":")
        while startPoint != endPoint:
            webApiRequests[startPoint] = b'\x00'
            startPoint += 1
            if startPoint >= len(webApiRequests):
                startPoint = 0
        arduino.api(method="write", value=request[1], target=request[0])


if __name__=='__main__': #calling  main 

    cv2.namedWindow("900 jaar Kuurne", cv2.WND_PROP_FULLSCREEN)
    cv2.resizeWindow("900 jaar Kuurne",(800,600)); 

    webApiRequests = Array('c', 20)
    webApiRequestsWritePointer = Value('i', 0)
    webApiRequestsReadPointer = Value('i', 0)

    app.debug=True #setting the debugging option for the application instance
    p = Process(target=flask_loop, args=(webApiRequests,webApiRequestsReadPointer,))
    p.start()
    app.run(port="5001",use_reloader=False) #launching the flask's integrated development webserver
    p.join()

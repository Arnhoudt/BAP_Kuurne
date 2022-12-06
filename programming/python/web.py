from multiprocessing import Process, Array, Value
from flask import Flask, render_template, request #importing the module

import time
# importing libraries
import cv2
from ffpyplayer.player import MediaPlayer
import re
from lib import ArduinoApi
from tinydb import TinyDB, Query
from icecream import ic

IS_NUMBER_REGEX = '^[0-9]+$'

app=Flask(__name__) #instantiating flask object

video = None
player = None


keyMap = {
    ord("a"): 1810,
    ord("s"): 1815,
    ord("d"): 1847,
    ord("f"): 1888,
    ord("g"): 1950,
}

cardDB = TinyDB('./databases/cards.json')
videoDB = TinyDB('./databases/video.json')

@app.route('/') #defining a route in the application
def func(): #writing a function to be executed 
    videos = videoDB.all()
    flessen = cardDB.all()
    return render_template("index.html", videos=videos, flessen=flessen)

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

@app.route('/video', methods = ['post'])
def setVideo():
    if 'file' not in request.files:
        return "No file has been found", 400
    if 'year' not in request.form:
        return "No year has been found", 400
    year = request.form['year']
    ic(year)
    f = request.files['file']
    f.save('./videos/' + year + '.mp4')
    return "OK", 200

def openDoor(apiScheduler):
    currentTime = round(time.time())
    apiScheduler.append({"time": currentTime, "target": "servo", "value": 10})
    apiScheduler.append({"time": currentTime+10, "target": "servo", "value": 80})
    apiScheduler.sort(key=lambda x: x["time"])

def flask_loop(webApiRequests, webApiRequestsReadPointer, messagingRegister):
    global keyMap
    global video
    global player
    global cardDB
    global videoDB

    arduino = ArduinoApi.ArduinoApi()
    apiScheduler = []

    if arduino is None:
        print("No arduino has been found")
    lastEpoch = time.time()
    apiScheduler.append({"time": time.time() + 2, "target": "servo", "value": 80})
    while True:
        # every second, it reads and processes the web api requests and the serial requests
        if time.time() - lastEpoch > 0.1:
            lastEpoch = time.time()
            output = tick(arduino, webApiRequests, webApiRequestsReadPointer, messagingRegister)
            card = Query()
            if "error" in output:
                messagingRegister[0] = b'i'
            if "rfid" in output:
                rfidCard = cardDB.search(card.Id == output["rfid"])
                if len(rfidCard) > 0:
                    videoLink = videoDB.search(card.year == rfidCard[0]["year"])
                    if len(videoLink) == 0:
                        print("No video found for this card")
                        video = cv2.VideoCapture("videos/404.mp4")
                        player = MediaPlayer("videos/404.mp4")
                    else:
                        video = cv2.VideoCapture(videoLink[0]["url"])
                        player = MediaPlayer(videoLink[0]["url"])
                    openDoor(apiScheduler)
                elif output["rfid"] != '0':
                    print("Unknown carddddddd")
                    ic(output["rfid"])

                    openDoor(apiScheduler)
                output["rfid"] = None


        if apiScheduler != [] and apiScheduler[0]["time"] < round(time.time()):
            arduino.api(method="write", value=apiScheduler[0]["value"], target=apiScheduler[0]["target"])
            apiScheduler.pop(0)
    

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


def tick(arduino, webApiRequests, webApiRequestsReadPointer, messagingRegister):
    output = {}
    value = arduino.api(method="read")
    if value[1] != 200:
        output["error"] = value
        return output
    value = value[0].split(":")
    handleWebApiRequests(arduino, webApiRequests, webApiRequestsReadPointer)
    if len(value) > 1 and value[0] == "rfid":
        output["rfid"] = value[1].strip()
    return output


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
    # cardDB.insert({'Id': '53d17233', 'year': 1810})
    # videoDB.insert({'year': 1810, 'url': './videos/1810.mp4'})
    cv2.namedWindow("900 jaar Kuurne", cv2.WND_PROP_FULLSCREEN)
    cv2.resizeWindow("900 jaar Kuurne",(800,600)); 

    webApiRequests = Array('c', 20)
    webApiRequestsWritePointer = Value('i', 0)
    webApiRequestsReadPointer = Value('i', 0)
    messagingRegister = Array('c', 1)
    # messaging register is used to communicate between the flask thread and the main thread
    # it is used to tell the main thread that the flask thread has been started
    # bit 0 is used to tell the status of the arduino (active 'a' or inactive 'i')
    messagingRegister[0] = b'i'
    # 


    app.debug=True #setting the debugging option for the application instance
    p = Process(target=flask_loop, args=(webApiRequests,webApiRequestsReadPointer,messagingRegister))
    p.start()
    app.run(port="5001",use_reloader=False) #launching the flask's integrated development webserver
    p.join()

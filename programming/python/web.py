from multiprocessing import Process, Array, Value
from flask import Flask, render_template, request, send_file #importing the module

import time
# importing libraries
import cv2
from ffpyplayer.player import MediaPlayer
import re
from mylib import ArduinoApi
from tinydb import TinyDB, Query
from icecream import ic

IS_NUMBER_REGEX = '^[0-9]+$'

app=Flask(__name__) #instantiating flask object

video = None
defaultVideo = cv2.VideoCapture("videos/default.mp4")
defaultVideo.set(cv2.CAP_PROP_FPS, int(60))
player = None


keyMap = {
    ord("a"): 1810,
    ord("s"): 1815,
    ord("d"): 1847,
    ord("f"): 1888,
    ord("g"): 1950,
}
frameCounter = 0
fps = 0
startTime = time.time()

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
    videoDB.insert({'year': year, 'url': './videos/' + year + '.mp4'})
    return "OK", 200

@app.route('/play', methods = ['get'])
def playVideo():
    year = request.args.get('year')
    videoQuerry = Query()
    videoLink = videoDB.search(videoQuerry.year == year)
    if len(videoLink) == 0:
        return "No video found for this year", 404
    else:
        return send_file(videoLink[0]["url"], mimetype='video/mp4')

@app.route('/reqeustForUnregisteredCard', methods = ['post'])
def reqeustForUnregisteredCard():
    global messagingRegister
    messagingRegister[1] = b'1'
    return "Waiting for a card"


@app.route('/unregisteredPoll', methods = ['post'])
def unregisteredPoll():
    global messagingRegister
    if messagingRegister[1] == b'1':
        return "Card has not yet been presented", 204
    if messagingRegister[1] == b'0' and messagingRegister[2] != b'\x00':
        return str(messagingRegister[2:10].decode('utf-8')) 
    return "something went wrong"

@app.route('/registerCard', methods = ['post'])
def registerCard():
    global messagingRegister
    global cardDB
    for i in range(2, 10): # this is not needed, but it's here to make sure that the card is not registered twice if a bad programmer (aka I) messes up the code
        messagingRegister[i] = b'\x00'
    id = request.form['id'] # since the api will not be used by malicious people, the user may be trusted to send the correct data
    year = request.form['year']
    cardDB.insert({'Id': id, 'year': year})
    return "something went wrong"

def openDoor(apiScheduler):
    currentTime = round(time.time())
    apiScheduler.append({"time": currentTime, "target": "servo", "value": 10})
    apiScheduler.append({"time": currentTime+5, "target": "servo", "value": 80})
    apiScheduler.sort(key=lambda x: x["time"])

def flask_loop(webApiRequests, webApiRequestsReadPointer, messagingRegister):
    global keyMap
    global video
    global defaultVideo
    global fps
    global frameCounter
    global startTime
    global player
    global cardDB
    global videoDB
    

    arduino = ArduinoApi.ArduinoApi()
    apiScheduler = []

    if arduino is None:
        print("No arduino has been found")
    lastEpoch = time.time()
    apiScheduler.append({"time": time.time() + 2, "target": "servo", "value": 80})
    delay = 1000/36
    while True:
        cycleTime = time.time();
        # every second, it reads and processes the web api requests and the serial requests
        if time.time() - lastEpoch > 10000.1:
            lastEpoch = time.time()
            output = tick(arduino, webApiRequests, webApiRequestsReadPointer, messagingRegister)
            card = Query()
            if "error" in output:
                messagingRegister[0] = b'i'
            if "rfid" in output:
                # print all
                rfidCard = [card for card in cardDB.all() if (card["Id"] == output["rfid"][0:8])]
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
                    if messagingRegister[1] == b'1':
                        print("Card has been presented")
                        for i in range(8):
                            messagingRegister[2+i] = output["rfid"][i].encode('utf-8')
                        messagingRegister[1] = b'0'
                    else:
                        print("no request for this card")
                    ic(output["rfid"])

                    openDoor(apiScheduler)
                output["rfid"] = None


        if apiScheduler != [] and apiScheduler[0]["time"] < round(time.time()):
            arduino.api(method="write", value=apiScheduler[0]["value"], target=apiScheduler[0]["target"])
            apiScheduler.pop(0)
    

        
        # if key in keyMap:
        #     url = videoMap[keyMap[key]]
        #     video=cv2.VideoCapture(url)
        #     player = MediaPlayer(url)

        if video:
            grabbed, frame=video.read()
            audio_frame, val = player.get_frame()
        
        if video is not None and not grabbed:
            video.release()
            video = None
            player = None      
        
        if video is None:
            grabbed, frame=defaultVideo.read()
            if not grabbed:
                defaultVideo=cv2.VideoCapture("videos/default.mp4")
                grabbed, frame=defaultVideo.read()
        cv2.putText(frame, "FPS: " + str(fps), (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 1, cv2.LINE_AA)
        frameCounter += 1

        if time.time() - startTime >= 1:
            fps = frameCounter
            frameCounter = 0
            startTime = time.time()
        cv2.imshow("900 jaar Kuurne", frame)
        if player is not None and val != 'eof' and audio_frame is not None:
            #audio
            img, t = audio_frame
        key = None
        while time.time() - cycleTime < (delay/1000):
            newKey = cv2.waitKey( 1 ) & 0xFF
            if newKey != 255:
                key = newKey
        if key == ord("q"):
                break
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

    webApiRequests = Array('c', 20)
    webApiRequestsWritePointer = Value('i', 0)
    webApiRequestsReadPointer = Value('i', 0)
    messagingRegister = Array('c', 10)
    # messaging register is used to communicate between the flask thread and the main thread
    # it is used to tell the main thread that the flask thread has been started
    # bit 0 is used to tell the status of the arduino (active 'a' or inactive 'i')
    messagingRegister[0] = b'i'
    # bit 1 is used to tell if the app requests a card to be read 1 if requested, 0 when read
    messagingRegister[1] = b'0'
    for i in range(2, 10):
        messagingRegister[i] = b'\x00'
    # 


    app.debug=True #setting the debugging option for the application instance
    p = Process(target=flask_loop, args=(webApiRequests,webApiRequestsReadPointer,messagingRegister))
    p.start()
    app.run(port="5001",use_reloader=False) #launching the flask's integrated development webserver
    p.join()

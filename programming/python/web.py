# The arduino is controlled by the web api
# The web api is controlled by the flask server
# The flask server is controlled by the main process
# The main process is controlled by the arduino
# The arduino is controlled by the servo
# The servo is controlled by the user
# The user is controlled by the government
# The government is controlled by the aliens
# copilot 2022

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
import os

IS_NUMBER_REGEX = '^[0-9]+$' # regex to check if a string is a number

dirname = os.path.dirname(__file__)
app=Flask(__name__) #instantiating flask object

cardDB = TinyDB(dirname +'/databases/cards.json') # This will be used to store tuples of the form (cardId, year)
videoDB = TinyDB(dirname + '/databases/video.json') # This will be used to store tuples of the form (year, path)

@app.route('/') #This is the route to the dashboard
def func(): 
    # All the videos and cards are loaded from the databases and passed to the template
    videos = videoDB.all()
    flessen = cardDB.all()
    return render_template("index.html", videos=videos, flessen=flessen)

@app.route('/video', methods = ['post'])
# This is the route to upload a video
def setVideo():
    # The year and the video are extracted from the request
    if 'file' not in request.files:
        return "No file has been found", 400
    if 'year' not in request.form:
        return "No year has been found", 400
    year = request.form['year']
    f = request.files['file']
    f.save(dirname+'/videos/' + year + '.mp4') # The video has not to be saved securely, since the mayor of Kuurne is not an evil person
    videoDB.insert({'year': year, 'url': dirname +'/videos/' + year + '.mp4'}) # The video reference is saved in the database
    return "OK", 200

@app.route('/play', methods = ['get'])
# This is the route to play a video in the dashboard
def playVideo():
    # The year is extracted from the request and the video is searched in the database
    year = request.args.get('year')
    videoQuerry = Query()
    videoLink = videoDB.search(videoQuerry.year == year)
    if len(videoLink) == 0:
        return "No video found for this year", 404
    else:
        return send_file(videoLink[0]["url"], mimetype='video/mp4')

# How the 3 way register works:
# The user requests a card to be presented by setting char 1 to 1
# When an unregistered card is presented, the arduino sets char 1 to 0 and sets chars 2 to 10 to the card id
# When the dashboard checks if a card has been presented, the server checks if char 1 is 0, if it is, it returns the card id at chars 2 to 10

@app.route('/reqeustForUnregisteredCard', methods = ['post'])
# This is the route to request a card to be presented
def reqeustForUnregisteredCard():
    global messagingRegister
    messagingRegister[1] = b'1'
    return "Waiting for a card"


@app.route('/unregisteredPoll', methods = ['post'])
# This is the route to check if a card has been presented
def unregisteredPoll():
    global messagingRegister
    if messagingRegister[1] == b'1':
        return "Card has not yet been presented", 204
    if messagingRegister[1] == b'0' and messagingRegister[2] != b'\x00':
        return str(messagingRegister[2:10].decode('utf-8')) 
    return "something went wrong"

@app.route('/registerCard', methods = ['post'])
# This is the route to register a card, you can register a card without presenting it, but it's not recommended to do so
def registerCard():
    global messagingRegister
    global cardDB
    if 'id' not in request.form:
        return "No id has been found", 400
    if 'year' not in request.form:
        return "No year has been found", 400
    for i in range(2, 10): # this is not needed, but it's here to make sure that the card is not registered twice if a bad programmer (aka I) messes up the code
        messagingRegister[i] = b'\x00'
    id = request.form['id'] # since the api will not be used by malicious people, the user may be trusted to send the correct data
    year = request.form['year']
    cardDB.insert({'Id': id, 'year': year}) # the card is saved in the database
    return "OK", 200

def openDoor(apiScheduler): # this function is used to open the door for 5 seconds
    currentTime = round(time.time())
    apiScheduler.append({"time": currentTime, "target": "decoration", "value": 0})
    apiScheduler.append({"time": currentTime+1, "target": "servo", "value": 10})
    apiScheduler.append({"time": currentTime+4, "target": "servo", "value": 80})
    apiScheduler.append({"time": currentTime + 10, "target": "decoration", "value": 1})
    apiScheduler.sort(key=lambda x: x["time"])

def flask_loop(webApiRequests, webApiRequestsReadPointer, messagingRegister):
    global cardDB
    global videoDB
    videoMap = {}
    for video in videoDB.all():
        videoMap[video["year"]] = cv2.VideoCapture(video["url"])
    cv2.namedWindow("900 jaar Kuurne", cv2.WND_PROP_FULLSCREEN)
    cv2.setWindowProperty("900 jaar Kuurne", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN);

    frameCounter = 0
    startTime = time.time()

    arduino = ArduinoApi.ArduinoApi()
    apiScheduler = []
    CT3874 = round(time.time())
    apiScheduler.append({"time": CT3874 + 15, "target": "decoration", "value": 0})
    apiScheduler.append({"time": CT3874 + 18, "target": "decoration", "value": 1})

    if arduino is None:
        print("No arduino has been found")
    lastEpoch = time.time()
    apiScheduler.append({"time": time.time() + 2, "target": "servo", "value": 80})
    delay = 1000/36
    defaultVideo = cv2.VideoCapture(dirname + "/videos/default.mp4")
    unknownVideo = cv2.VideoCapture(dirname + "/videos/404.mp4")
    video = None
    player = None
    fps = 0
    testEpoch = time.time()
    while True:
        cycleTime = time.time();
        # every second, it reads and processes the web api requests and the serial requests
        if time.time() - lastEpoch > 0.1:
            lastEpoch = time.time()
            output = tick(arduino, webApiRequests, webApiRequestsReadPointer, messagingRegister)
            # if time.time() - testEpoch > 5: # this is used to test the arduino without the arduino
            #     output = {"rfid": "4af4f6a5", "error": "0"}
            #     testEpoch = time.time()
            card = Query()
            if "error" in output:
                messagingRegister[0] = b'i'
            if "rfid" in output:
                # print all
                rfidCard = [card for card in cardDB.all() if (card["Id"] == output["rfid"][0:8])]
                print(rfidCard)
                if len(rfidCard) > 0:
                    videoLink = videoDB.search(card.year == rfidCard[0]["year"])
                    if len(videoLink) == 0:
                        print("No video found for this card")
                        video = unknownVideo
                        video.set(cv2.CAP_PROP_POS_FRAMES, 0)
                        player = MediaPlayer(dirname + "/videos/404.mp4")
                    else:
                        if videoLink[0]["year"] not in videoMap:
                            videoMap[videoLink[0]["year"]] = cv2.VideoCapture(videoLink[0]["url"])
                        video = videoMap[videoLink[0]["year"]]
                        print(videoLink[0]["year"])
                        video.set(cv2.CAP_PROP_POS_FRAMES, 0)
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
                        video = unknownVideo
                        video.set(cv2.CAP_PROP_POS_FRAMES, 0)
                        player = MediaPlayer(dirname + "/videos/404.mp4")
                    ic(output["rfid"])

                    openDoor(apiScheduler)
                output["rfid"] = None


        if apiScheduler != [] and apiScheduler[0]["time"] < round(time.time()):
            arduino.api(method="write", value=apiScheduler[0]["value"], target=apiScheduler[0]["target"])
            apiScheduler.pop(0)

        if video:
            grabbed, frame=video.read()
            audio_frame, val = player.get_frame()
        
        if video is not None and not grabbed:
            # video.release() # you may not release the video, because it will be reused
            video = None
            player = None      
        
        if video is None:
            grabbed, frame=defaultVideo.read()
            if not grabbed:
                defaultVideo.set(cv2.CAP_PROP_POS_FRAMES, 0)
                grabbed, frame=defaultVideo.read()
        cv2.putText(frame, "FPS: " + str(fps), (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 1, cv2.LINE_AA)
        frameCounter += 1

        if time.time() - startTime >= 1:
            fps = frameCounter
            frameCounter = 0
            startTime = time.time()

        cv2.imshow("900 jaar Kuurne", frame)
        # if player is not None and val != 'eof' and audio_frame is not None:
        #     #audio
        #     img, t = audio_frame
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
    app.run(host= "0.0.0.0", port="5001",use_reloader=False) #launching the flask's integrated development webserver
    p.join()

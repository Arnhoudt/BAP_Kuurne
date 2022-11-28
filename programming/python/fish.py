# importing libraries
import cv2
import math
import random
import numpy as np

cv2.namedWindow("900 jaar Kuurne", cv2.WND_PROP_FULLSCREEN)
cv2.resizeWindow("900 jaar Kuurne",(1500,2000)); 
# cv2.setWindowProperty("900 jaar Kuurne",cv2.WND_PROP_FULLSCREEN,cv2.WINDOW_FULLSCREEN)

def rotate_image(image, angle):
  image_center = tuple(np.array(image.shape[1::-1]) / 2)
  rot_mat = cv2.getRotationMatrix2D(image_center, angle, 0.7)
  result = cv2.warpAffine(image, rot_mat, image.shape[1::-1], flags=cv2.INTER_LINEAR)
  return result

def shortestAngle(a, b):
    """Return the shortest angle between two angles in degrees."""
    return (a - b + 180) % 360 - 180


def createNewGoal(fish):
    fish["goal"] = [random.randint(0, frame.shape[1] - fish["size"]), random.randint(0, frame.shape[0] - fish["size"])]

def createSafeGoal(fish):
    clearPath = False
    while not clearPath:
        createNewGoal(fish)
        fish["direction"] = math.atan2(fish["goal"][1] - fish["pos"][1], fish["goal"][0] - fish["pos"][0]) * 180 / math.pi
        x = fish["pos"][0]
        y = fish["pos"][1]
        while x < fish["goal"][0] and y < fish["goal"][1]:
            clearPath = True
            x += int(fish["speed"] * math.cos(math.radians(fish["direction"])))
            y += int(fish["speed"] * math.sin(math.radians(fish["direction"])))
            for scareObject in scareObjects:
                if scareObject[0] < x < scareObject[0] + scareObject["width"] and scareObject[1] < y < scareObject[1] + scareObject["height"]:
                    clearPath = False
                    break

GOAL_MARGIN = 100
fishList = []
frame = cv2.imread('./screens/default.png')
for i  in range(0, 0):
    fishList.append({
        "pos": [random.randint(0, frame.shape[1]), random.randint(0, frame.shape[0])],
        "speed": random.randint(2, 10),
        "direction": -10,
        "goal": [500, 200],
        "size": random.randint(50, 200),
        "image": cv2.imread('./assets/fish.png', cv2.IMREAD_UNCHANGED),
        "imageRotation": -40,
        "scared": False
    })
    fishList[i]["image"] = cv2.resize(fishList[i]["image"], (fishList[i]["size"], fishList[i]["size"]))

scareObjects = []
for i  in range(0, 1):
    scareObjects.append({
        0: 200,
        1: 200,
        "width": 200,
        "height": 200,
        "border": 100,
    })


fish = {
    "pos": [random.randint(0, frame.shape[1]), random.randint(0, frame.shape[0])],
    "speed": random.randint(2, 10),
    "direction": -10,
    "goal": [500, 200],
    "size": random.randint(50, 200),
    "image": cv2.imread('./assets/fish.png', cv2.IMREAD_UNCHANGED),
    "imageRotation": -40,
    "scared": False
}

createSafeGoal(fish)

print(fish["goal"])
exit()
while True:
    frame = cv2.imread('./screens/default.png')
    for scareObject in scareObjects:
        cv2.rectangle(frame, (scareObject[0], scareObject[1]), (scareObject[0] + scareObject["width"], scareObject[1] + scareObject["height"]), (255, 0, 0), 2)
    key = cv2.waitKey(28) & 0xFF
    if key == ord("q"):
        break

    for fish in fishList:
        target = math.atan2(fish["goal"][1] - fish["pos"][1], fish["goal"][0] - fish["pos"][0]) * 180 / math.pi
        if target != fish["direction"]:
            angle = shortestAngle(target, fish["direction"])
            if angle > 0:
                fish["direction"] += 3
            else:
                fish["direction"] -= 3
        fish["direction"] = (fish["direction"] + 180) % 360 - 180
        if target - 5 < fish["direction"] < target + 5:
            fish["direction"] = target

        fish["pos"][0] += int((fish["speed"] if not fish["scared"] else 10) * math.cos(math.radians(fish["direction"])))
        fish["pos"][1] += int((fish["speed"] if not fish["scared"] else 10) * math.sin(math.radians(fish["direction"])))
        if not fish["scared"]:
            goalSafe = True
            for scareObject in scareObjects:
                if scareObject[0] < fish["pos"][0] + fish["size"] and fish["pos"][0] < scareObject[0] + scareObject["width"] and scareObject[1] < fish["pos"][1] + fish["size"] and fish["pos"][1] < scareObject[1] + scareObject["height"]:
                    goalSafe = False
                    break
            if not goalSafe:
                print(
                    fish["pos"],
                    fish["speed"],
                    fish["direction"],
                    fish["goal"],
                    fish["size"],
                )
                print("goal not safe")
                createSafeGoal(fish)
                fish["scared"] = True

        if fish["goal"][0] - GOAL_MARGIN < fish["pos"][0] < fish["goal"][0] + GOAL_MARGIN \
            and fish["goal"][1] - GOAL_MARGIN < fish["pos"][1] < fish["goal"][1] + GOAL_MARGIN:
            createNewGoal(fish)
            fish["scared"] = False
                # if(fish["goal"] == [0,250]):
                #     fish["goal"] = [500, 250]
                # else:
                #     fish["goal"] = [0, 250]
        # print(
        #         fish["pos"],
        #         fish["speed"],
        #         fish["direction"],
        #         fish["goal"],
        #         fish["size"],
        # )

        fishImage = rotate_image(fish["image"], fish["direction"]+fish["imageRotation"])

        if fish["pos"][0] + fish["size"] > frame.shape[1]:
            fish["pos"][0] = frame.shape[1] - fish["size"]
        if fish["pos"][1] + fish["size"] > frame.shape[0]:
            fish["pos"][1] = frame.shape[0] - fish["size"]
        if fish["pos"][0] < 0:
            fish["pos"][0] = 0
        if fish["pos"][1] < 0:
            fish["pos"][1] = 0
        alpha_s = fishImage[:, :, 3] / 255.0
        alpha_l = 1.0 - alpha_s
        y1, y2 = fish["pos"][1], fish["pos"][1] + fishImage.shape[0]
        x1, x2 = fish["pos"][0], fish["pos"][0] + fishImage.shape[1]
        for c in range(0, 3):
            frame[y1:y2, x1:x2, c] = (alpha_s * fishImage[:, :, c] + alpha_l * frame[y1:y2, x1:x2, c])

    cv2.imshow("900 jaar Kuurne", frame)

cv2.destroyAllWindows()


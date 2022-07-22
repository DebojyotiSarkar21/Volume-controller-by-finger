import cv2
import time
import numpy as np
import HandTrackingModule as htm
import math
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume


wCam, hCam = 640, 480


cap = cv2.VideoCapture(0)
cap.set(3, wCam)
cap.set(4, hCam)
pTime = 0

detector = htm.handDetector()


devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(
    IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))
# volume.GetMute()
# volume.GetMasterVolumeLevel()
volrange = volume.GetVolumeRange()

minvol = volrange[0]
maxvol = volrange[1]
vol = 0
volBar = 400
volPercentage = 0



while True:
    success, img = cap.read()
    img = detector.findhands(img)
    lmList = detector.findPosition(img, draw=False)
    if len(lmList) != 0:
        #print(lmList[4], lmList[8])

        x1,y1 = lmList[4][1], lmList[4][2]
        x2, y2 = lmList[8][1], lmList[8][2]
        cx, cy = (x1+x2) // 2, (y1+y2) // 2

        cv2.circle(img, (x1, y1), 15, (255,0,0),cv2.FILLED)
        cv2.circle(img, (x2, y2), 15, (255, 0, 0), cv2.FILLED)
        cv2.line(img, (x1, y1), (x2,y2),(255,0,0), 3)
        cv2.circle(img, (cx, cy), 15, (255, 0, 0), cv2.FILLED)

        length = math.hypot(x2-x1, y2-y1)
        #print(length)

        # Hand Range 50 - 300
        # Volume Range -64 - 0

        vol = np.interp(length, [55, 300], [minvol, maxvol])
        volBar = np.interp(length, [55, 300], [400, 150])
        volPercentage = np.interp(length, [55, 250], [0, 100])
        print(int(vol))
        volume.SetMasterVolumeLevel(vol, None)

        if length<50:
            cv2.circle(img, (cx, cy), 15, (255, 0, 255), cv2.FILLED)



    cv2.rectangle(img, (50, 150), (85, 400), (0,255,0), 3)
    cv2.rectangle(img, (50, int(volBar)), (85, 400), (0, 255, 0), cv2.FILLED)
    cv2.putText(img, f'VOLUME: {int(volPercentage)} %', (40, 450), cv2.FONT_HERSHEY_PLAIN,
                1, (0,255, 0), 2)

    cTime = time.time()
    fps = 1/(cTime - pTime)
    pTime = cTime

    cv2.putText(img, f'FPS: {int(fps)}',(10,30), cv2.FONT_HERSHEY_PLAIN,
                1,(255,0,255), 2)

    cv2.imshow("Image", img)
    cv2.waitKey(1)
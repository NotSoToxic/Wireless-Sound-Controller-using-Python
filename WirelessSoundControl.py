
#IMPORT STATEMENTS -
import cv2 as cv
import mediapipe as mp
import time as t
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
import math
import numpy as np


#initialisation of variables -
cam = cv.VideoCapture(0)
mpHands = mp.solutions.hands
hands = mpHands.Hands(False)
mpDraw = mp.solutions.drawing_utils
ct=0
pt=0


#Windows Volume Initialisation 
devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(
    IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))
#volume.GetMasterVolumeLevel()
vol_range = volume.GetVolumeRange()

volmin = vol_range[0]
volmax = vol_range[1]

#cannot detect cam -
if not cam.isOpened():
    print ("Error Camera Not Found ")


#Output procedure -
while cam.isOpened() :
    #Capturing Frame By Frame
    ret , frame = cam.read()


    #BGR TO RGB
    imgRGB = cv.cvtColor(frame , cv.COLOR_BGR2RGB)
    results = hands.process(imgRGB)


    lmList = []


    #landmarks
    if results.multi_hand_landmarks:
        for handLms in results.multi_hand_landmarks:
            for  id, lm  in enumerate(handLms.landmark):
                h,w,_ = frame.shape
                cx,cy = int(lm.x*w),int(lm.y*h)
                lmList.append([id,cx,cy])
        mpDraw.draw_landmarks(frame , handLms , mpHands.HAND_CONNECTIONS)

    #Landmark and Line Modification 
    if lmList != []:
        x1,y1 = lmList[4][1],lmList[4][2]
        x2,y2 = lmList[8][1],lmList[8][2]
 
        cv.circle(frame,(x1,y1),10,(0,0,255),cv.FILLED)
        cv.circle(frame,(x2,y2),10,(0,0,255),cv.FILLED)
        cv.line(frame,(x1,y1),(x2,y2),(255,255,255),3)
        

        #Vol Line Length
        lnlen = math.hypot(x2-x1,y2-y1)
        
        
        #Volume lvl conversion using numpy
        vol = np.interp(lnlen, [30,130],[volmin, volmax] )
        volBar = np.interp(lnlen, [30,130],[400,60] )
        volpercent = np.interp(lnlen, [30,130],[0,100] )
        volume.SetMasterVolumeLevel(vol, None)

        #Volume Bar On the Display Window
        cv.rectangle(frame , (25,60) , (45 ,400), (0,0,255), 2)
        cv.rectangle(frame , (25,int(volBar)) , (45 ,400), (0,0,255), cv.FILLED)
        cv.putText(frame, f'{int(volpercent)}%' , (15,50), cv.FONT_HERSHEY_PLAIN , 2 , (255,0,0) , 1)


        #Fps Display -
        ct = t.time()
        fps = 1/(ct-pt )
        cv.putText(frame, f'FPS : {str(int(fps))}' , (450,25), cv.FONT_HERSHEY_PLAIN , 2 , (0,0,255) , 2)
        pt = ct



      
    #Displaying Frames
    cv.imshow(" Web Cam " , frame)
    if cv.waitKey(1) == ord('q'):
        break


# Release the capture
cam.release()
cv.destroyAllWindows()



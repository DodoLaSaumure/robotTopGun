#!/usr/bin/python3
import cv2
import numpy as np
import time
import os
import sys
from urllib.request import urlopen
from copy import deepcopy
import serial



# All the 6 methods for comparison in a list
methods = ['cv.TM_CCOEFF', 'cv.TM_CCOEFF_NORMED', 'cv.TM_CCORR',
            'cv.TM_CCORR_NORMED', 'cv.TM_SQDIFF', 'cv.TM_SQDIFF_NORMED']

camnum = 2
W,H = 100,100
mouseX,mouseY = W+1,H+1
mouseClicked = False
img = None
scale =0.3
class FakeSerial():
    def __init__(self):
        print ("> Fake Ser >init done")
    def close(self):
        print ("> Fake Ser >serial Closed")
    def poweron(self):
        print ("Power on")
    def go(self,xOrZ,dir):#dir = + - off # xorZ = x , z
        print("> Fake Ser >"+xOrZ+dir)
    def move(self,x,z):
        print( "> Fake Ser >Moving to x %d - z %d"%(x,z))
    def poweroff(self):
        print ("> Fake Ser >Powering Off")
    def write(self,dummy):
        return
    def readline(self):
        return ("> Fake Ser >DUMMU")
class Robot():
    def __init__(self):
        print( "Opening serial")
        try :
            self.ser = serial.Serial('/dev/ttyACM0',115200,timeout=1)
        except :
            self.ser = FakeSerial()
        time.sleep(1)
    def close(self):
        self.ser.close()

    def poweron(self):
        print("> powering on")
        time.sleep(0.2)
        self.ser.write(b"\n")
        time.sleep(0.2)
        res =self.ser.readline()
        if not res == b'unknown Command :\r\n':
            print ("-----> Erreur powering on <--------", str(res))
        time.sleep(0.2)
        self.ser.write(b"poweron\n")
        time.sleep(0.2)
        res =self.ser.readline()
        if not res == b'Power is On\r\n':
            print ("-----> Erreur powering on <--------", str(res))
        else :
            print("< Power is On")

    def go(self,xOrZ,dir):#dir = + - off # xorZ = x , z
        print("> "+xOrZ+dir)
        cmd = bytes("%s%s\n"%(xOrZ,dir), 'utf-8')
        self.ser.write(cmd)
        res =self.ser.readline()
        print ("< " +str(res))
    def move(self,x,z):
        print( "> Moving to x %d - z %d"%(x,z))
        time.sleep(0.2)
        cmd = bytes("move x%d z%d\n"%(x,z),'utf-8')
        self.ser.write(cmd)
        time.sleep(2)
        res = self.ser.readline()
        if not res == bytes('XMove %d\r\n'%x,"utf-8"):
            print ("-----> Erreur moving on x <--------", str(res))
        res = self.ser.readline()
        if not res == bytes('ZMove %d\r\n'%z,"utf-8"):
            print ("-----> Erreur moving on z<--------", str(res))
        else :
            print ("< Move done")
    def poweroff(self):
        print ("> Powering Off")
        time.sleep(0.2)
        self.ser.write(b"poweroff\n")
        time.sleep(0.2)
        res =self.ser.readline()
        if not res == b'Power is Off\r\n':
            print ("-----> Erreur powering oof <--------", str(res))
        else : 
            print ("< Power is off")


def getMouse(event,x,y,flags,param):
    global mouseX,mouseY
    global img
    global mouseClicked
    global Follow
#     if event == cv2.EVENT_LBUTTONDBLCLK:
    if event == cv2.EVENT_LBUTTONDOWN:
        mouseX,mouseY = x,y
        mouseClicked = True
        Follow = not Follow
template = None


if __name__ == "__main__":
    print("start Program")
    Follow = False
    cap = cv2.VideoCapture(2)
    ret, imgSrc = cap.read()
    print("CapREads")
    myrobot = Robot()
    myrobot.poweron()
    print("Robot is ok")
    cv2.namedWindow('Image')
    cv2.setMouseCallback('Image',getMouse)
    while True :
        ret, imgSrc = cap.read()
#         imgSrc = url_to_image(camnum)
        img = cv2.resize(imgSrc, (0, 0), fx=scale, fy=scale)
        dimensions = img.shape
        dimx =dimensions[1]
        dimy = dimensions[0]
#         print(dimensions)
        cpimg = deepcopy(img)
        if template is None :
#             miny = max(0,mouseY-H)
#             maxy = min(mouseY+H,dimensions[0])
#             minx = max(mouseX-W,0)
#             maxx = min(mouseX+W,dimensions[1])
            minx = int(dimx/2-H/2)
            miny  = int(dimy/2-H/2)
            maxx = minx+H 
            maxy =miny + H
#             template = cpimg[mouseY-H:mouseY+H, mouseX-W:mouseX+W]
            template = cpimg[miny:maxy, minx:maxx]
            savedtemplate = deepcopy(template)
        w, h = W,H
        if mouseClicked :
            minyt = int(max(0,mouseY-H/2))
#             maxyt = min(mouseY+H,dimensions[0])
            maxyt = min(minyt+H,dimensions[0])
            minxt = int(max(mouseX-W/2,0))
#             maxxt = min(mouseX+W,dimensions[1])
            maxxt = min(minxt+W,dimensions[1])
#             template = cpimg[mouseY-H:mouseY+H, mouseX-W:mouseX+W]
            template = cpimg[minyt:maxyt, minxt:maxxt]
            savedtemplate = deepcopy(template)
            mouseClicked = False
        res = cv2.matchTemplate(cpimg,template,cv2.TM_SQDIFF_NORMED)
#         res = cv2.matchTemplate(img,template,cv2.TM_SQDIFF)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
        top_left = min_loc
        bottom_right = (top_left[0] + w, top_left[1] + h)
        miny = max(0,min_loc[1])
        maxy = miny+h
        minx = max(min_loc[0],0)
        maxx = minx+w
        x00 = minx + w
        y00 = miny +h 
        centerx =dimx/2
        centery = dimy/2
        deltax = centerx-x00
        deltay = centery -y00
        print("deltax",deltax)
        print("deltay",deltay)
        if Follow :
            if abs(deltax)<15 :
                myrobot.go("x", "off")
            elif deltax> 0 :
                myrobot.go("x", "+")
            elif deltax < 0 :
                myrobot.go("x", "-")
            if abs(deltay)<15 :
                myrobot.go("z", "off")
            elif deltay> 0 :
                myrobot.go("z", "+")
            elif deltay< 0 :
                myrobot.go("z", "-")
        else :
            myrobot.go("z", "off")
            myrobot.go("x", "off")
#         print (x,y)
        cpSrc = deepcopy(img)
        cropped = cpSrc[miny:maxy,minx:maxx]
        cv2.imshow("crop",cropped)
        cv2.imshow("template",template)
#         if min_val<0.07:
        if Follow:
            cv2.rectangle(img,(minx,miny),(maxx,maxy),(0,255,0),2)
        cv2.imshow('Image',img)
       
#         w, h = template.shape[::-1]
        k = cv2.waitKey(20) & 0xFF
        if k == 27:
            break
        elif k == ord('a'): 
            print (mouseX,mouseY)
        
        k = cv2.waitKey(20) & 0xFF
        if k == 27:
            break
        elif k == ord('a'):
            print (mouseX,mouseY)

    cv2.destroyAllWindows()  
    myrobot.move(0,0)
    myrobot.poweroff()
    myrobot.close()
#         time.sleep(2)
#         if cv2.waitKey(2000) & 0xff == 27: quit()


import cv2
import mediapipe as mp
import os

wCam , hCam = 640 , 480 #hight and width of the camra

cap = cv2.VideoCapture('fingers.mp4') #for opening cam vedio capture (number of device)
cap.set(3,wCam)
cap.set(4,hCam) #definiting hegight and width

mpHands=mp.solutions.hands #to analize hand image 
hands = mpHands.Hands()#extracting hand from vedio
mpDraw = mp.solutions.drawing_utils #for drawing hand on vedio for better reffrence

while True:
    success , img=cap.read()#reading img from fingers.mp4 and returing it 9in sucess var
    imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB) #converting img
    

    cv2.Inshow('finger counter', img)#showing finger count
    cv2.waitKey(5)
    imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB) #converting img
    results = hands.process(imgRGB) #processing img to get hand 
    results.multi_hand_landmarks #processes img landmarks
    multiLandmarks=results.multi_hand_landmarks #saving land marks to var 
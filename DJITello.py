#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from turtle import goto
from PyQt5.uic import loadUi
from PyQt5.QtWidgets import QMainWindow, QApplication
from PyQt5 import QtGui, QtCore
import cv2
import numpy as np
import time
from djitellopy import Tello
from FaceDetectionModule import faceDetector
from manuelControl import manuelControl
from keyboard_info import KeyboardInfo
from datetime import datetime



mode = 0 # 0: Webcam - 1: TelloCam (Default: 1)
isNewFile = 1 # 0: For Keep Going Current File - 1: For Create New File (Default: 0)
isDraw = 1 # 0: Don't draw face area and center of camera 1: Draw face area and center of camera (Default: 1)  

class djiTello(QMainWindow):
    def __init__(self):
        global mode, isNewFile, isDraw
        super().__init__()
        loadUi("opencv.ui",self)
        self.variables() # Init Variables
        self.key_info = KeyboardInfo() # Set up keyboard info window
        self.manuel = manuelControl() # Set up manuelControl widget
        self.face_detector = faceDetector() # Set Up Face Detector
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.checkmode()
        self.statusBar().showMessage('INFO: ')
        
        if(isNewFile):
            with open("PID.txt", "w") as f:
                pass
        
        
        if not mode: # Webcam Mode
            self.cap = cv2.VideoCapture(0)
            _, self.img = self.cap.read()
        else: # Drone Mode
            self.me = Tello()
            self.me.connect() # Connect To Drone
            self.me.streamoff()
            self.me.streamon()
            time.sleep(5)
            
            self.img = self.me.get_frame_read().frame

        # Check Buttons
        self.save_button.clicked.connect(self.saveValues)
        self.close_button.clicked.connect(self.closeEverything)
        self.takeOff_button.clicked.connect(self.takeOffDrone)
        self.land_button.clicked.connect(self.landDrone)

        self.manuel_button.clicked.connect(self.openManuelPage)
        self.manuel.closeM_button.clicked.connect(self.closeManuelPage)

        self.fbRadio.toggled.connect(self.updateFB)
        self.lrRadio.toggled.connect(self.updateLR)
        self.udRadio.toggled.connect(self.updateUD)
        
        


    # --------------------- CODE LOOP ---------------------
    def runCode(self):
        self.show() # Open The Gui
        cTime = 0
        pTime = 0
        while True:
            self.time1 = time.time()
            if(self.keyboard_control.isChecked()):
                self.key_info.show() # If Keyboard Control activated, open keyboard info window
            else:
                self.key_info.close() #  If Keyboard Control activated, close keyboard info window
            if not mode:
                _, self.img = self.cap.read() # Read Image From Webcam
            else:
                try:

                    self.img = self.me.get_frame_read().frame # Read Image From Drone
                    self.battery_label.setText("%" + str(self.me.get_battery())) # Setting battery label to see drone charge.
                except: # If can't get img, give an error.
                    print("Cant Get İmage.")
                    self.statusBar().showMessage("ERROR: Can't Get Image.")
                    continue
            
                
            

            self.img = cv2.resize(self.img, (640, 480))  # Resizing Image
            self.img, self.bboxs = self.findFace(img = self.img) # Finding Face
                   
            
                
            imgGui = self.img.copy() # Copying the img to set in gui
            self.imgHeight, self.imgWidth, _ = imgGui.shape # Getting img shape
            
            
            
            self.getPIDValues() # Set PID Values to Control Speeds of Drone
          
            

            if(isDraw):
                imgGui = self.drawFace(img = imgGui, rt = 4) # Drawing Face Area
                cv2.line(imgGui, (self.imgWidth // 2, 0), (self.imgWidth // 2 , self.imgHeight), (255,0,0), 4) # Draw Center Point
                cv2.line(imgGui, (0, self.imgHeight // 2), (self.imgWidth, self.imgHeight // 2), (255,0,0), 4) #
            

            if self.pageNum == 0:  # If in main page
                self.findPositions()                # Finding Cx, Cy, Area of Face
                if(not self.keyboard_control.isChecked()):
                    self.findErrors()                   # Finding PID Errors To Set Speed Of Drone
                try:
                    if(not self.keyboard_control.isChecked()):
                        if(mode):
                            self.me.send_rc_control(0, self.fbSpeed, -self.udSpeed, self.yawSpeed)
                    
                except: # If not connected the drone give an error
                    print("Moving Drone Failed.----------------")
                    self.statusBar().showMessage('ERROR: Moving Drone Failed.')
            elif self.pageNum == 1: # If in manual control page
                try:
                    self.manuel.getSpeeds(self.me) # Getting manual speeds from gui to remote control drone
                except:
                    print("Not Drone Connected")
                    
                    
                    
           # FPS Calculating...         
            cTime = time.time()  
            fps = 1 / (cTime - pTime)
            pTime = cTime
            
            cv2.putText(imgGui, f'FPS: {int(fps)}', (20, 70), cv2.FONT_HERSHEY_PLAIN, 3, (0, 255, 0), 2) # Write FPS Top Corner
            
            
            

            
            
            
            imgGui = cv2.cvtColor(imgGui,cv2.COLOR_RGB2BGR)                                                 # Convert Img to QPixmap
            imgGui = QtGui.QImage(imgGui.data,imgGui.shape[1],imgGui.shape[0],QtGui.QImage.Format_RGB888)   #
            
            if self.pageNum == 0:    
                self.label.setPixmap(QtGui.QPixmap.fromImage(imgGui))   # Setting img in gui
            elif self.pageNum == 1:
                self.manuel.camImg.setPixmap(QtGui.QPixmap.fromImage(imgGui))                                         

            self.time2 = time.time()
            self.delta_time = round(self.time2 - self.time1, 4)
            print("Time: {}".format(self.delta_time))
            QtCore.QCoreApplication.processEvents() # Updade Gui

        

    # --------------------- HELPFUL FUNCTIONS ------------------------

    def findErrors(self): # Finding Face Positioning Errors
        try:
            if len(self.bboxs[1]) and int(self.bboxs[2] * 100) > 85: # If any face found and face percentage is higher than 85 find errors.
                
                
  
                self.errors[0] = self.fb_Range[0] - self.area             # Finding Forw-Backw Error
                self.errors[1] = self.centerXY[0] - (self.imgWidth // 2)  # Finding Yaw Error
                self.errors[2] = self.centerXY[1] - (self.imgHeight // 2) # Finding Up-Down Error


                '''print("Cx: ", self.centerXY[0], "Cy: ", self.centerXY[1])
                
                print("ECx: ", self.errors[1], "ECy: ", self.errors[2])'''
                self.proposal_values[0] = self.errors[0]
                self.proposal_values[1] = self.errors[1]
                self.proposal_values[2] = self.errors[2]

                self.derivative_values[0] = (self.errors[0] - self.pErrors[0]) / self.delta_time
                self.derivative_values[1] = (self.errors[1] - self.pErrors[1]) / self.delta_time
                self.derivative_values[2] = (self.errors[2] - self.pErrors[2]) / self.delta_time

                self.integral_values[0] += self.errors[0] * self.delta_time
                self.integral_values[1] += self.errors[1] * self.delta_time 
                self.integral_values[2] += self.errors[2] * self.delta_time  

                self.fbSpeed = self.errors[0] * self.fbPID[0] + self.derivative_values[0] * self.fbPID[1] + self.integral_values[0] * self.fbPID[2] # Find Forward Backward Error Speed of Drone

                self.yawSpeed = self.errors[1] * self.lrPID[0] + self.derivative_values[1] * self.lrPID[1] + self.integral_values[1] * self.lrPID[2] # Find Yaw Speed Error Of Drone

                self.udSpeed = self.errors[2] * self.udPID[0] + self.derivative_values[2] * self.udPID[1] + self.integral_values[2] * self.udPID[2] # Find Up Down Speed Error Of Drone

                self.fbSpeed = int(np.clip(self.fbSpeed, -100, 100))
                self.yawSpeed = int(np.clip(self.yawSpeed,-100,100)) 
                self.udSpeed = int(np.clip(self.udSpeed,-100,100))


                print("Forward Speed: ", self.fbSpeed)
                print("Yaw Speed: ", self.yawSpeed)
                print("UpDown Speed: ", self.udSpeed)
                
                print(f"Der Err: {self.derivative_values}")
                
                
                
                self.integral_prior = self.integral_values
                self.pErrors[0] = self.errors[0]
                self.pErrors[1] = self.errors[1]
                self.pErrors[2] = self.errors[2]
                

        except: # If there is no face give an error
            print("Error Finding PID Errors")



    def findPositions(self): # Finding Face Positions
        try:
            if len(self.bboxs[1]) and int(self.bboxs[2] * 100) > 85: # If any face found and face percentage is higher than 85, find face area, and positions

                x, y, w, h = self.bboxs[1]

                self.centerXY[0] = x + (w // 2) # Center X of Face
                self.centerXY[1] = y + (h // 2) # Center Y of Face

                self.area = ((w) * (h)) ** 0.5  # Root Of Face Area

                print("Area: ", self.area)
                print("CX: ", self.centerXY[0], "CY: ", self.centerXY[1])
            else:
                self.area = 0
                self.centerXY[0] = 0
                self.centerXY[1] = 0
        except: # If there is no face give an error
            print("Cant Calculate The Speeds.")
            self.area = 0
            self.centerXY[0] = 0
            self.centerXY[1] = 0
            self.corners = [0, 0, 0, 0]
            self.fbSpeed = 0
            self.yawSpeed = 0
            self.udSpeed = 0
            self.fSpeed = 0
            self.bSpeed = 0
   
    

    def findFace(self, img): # Using Mediapipe Finding Any Face
        img, self.bboxs = self.face_detector.findFaces(img, draw=isDraw) #Finding face using mediapipe
        
        return img, self.bboxs
        

    def drawFace(self, img, l=30, t=5, rt= 1): # Drawing Face Area 
            try: 
                    x, y, w, h = self.bboxs[1] 
                    x1, y1 = x + w, y + h

                    #cv2.circle(img, (self.centerXY[0], self.centerXY[1]), 5, (0,255,0), -1, cv2.FILLED)
                    cv2.rectangle(img, (x, y), (x+w, y+h), (255,0,0), rt)
                    #cv2.rectangle(img, (x, x+w), (y, y + h), (255, 0, 255), rt)
                    # Top Left  x,y
                    #cv2.putText(img, str(int(self.bboxs[0][2] * 100)), (10, 70), cv2.FONT_HERSHEY_PLAIN, 5, (255,255,255), 3)
            except:
                print("Can't Draw")
                #print(self.bboxs)

            return img

          

    def variables(self): # Setting the variables
        self.img = 0
        self.mode = 0
        self.info = []
        self.bboxs = []
        self.fb_Range = [170, 190] # Root Of Face Area
        self.errors = [0, 0, 0]  # fbError, lrError, udError
        self.pErrors = [0, 0, 0] # fbError, lrError, udError

        self.fbSpeed = 0
        self.yawSpeed = 0
        self.udSpeed = 0
        self.fSpeed = 0
        self.bSpeed = 0

        self.centerXY = [0, 0]      # X, Y
        self.area = 0               # Root Of Face
        self.corners = [0, 0, 0, 0] # x, y, w, h

        self.fbPID = [0.0, 0.0, 0.0] # P, D, I
        self.lrPID = [0.0, 0.0, 0.0] # P, D, I
        self.udPID = [0.0, 0.0, 0.0] # P, D, I

        self.imgWidth = 0
        self.imgHeight = 0
        self.stopThread = False
        self.pageNum = 0

        self.pTime = 0
        self.cTime = 0
        self.integral_values = [0.0, 0.0, 0.0]
        self.integral_prior = [0.0, 0.0, 0.0]

        self.derivative_values = [0.0, 0.0, 0.0]
        self.proposal_values = [0.0, 0.0, 0.0]
        
        self.keyboard_speed = 0
        self.delta_time = 0.1
            
    def getPIDValues(self): # Getting PID Values From Sliders
        if self.mode == 0:
            self.fbPID[0] = int(self.kp_value.text()) / 100.0
            self.fbPID[1] = int(self.kd_value.text()) / 100.0
            self.fbPID[2] = int(self.ki_value.text()) / 100.0
        elif self.mode == 1:
            self.lrPID[0] = int(self.kp_value.text()) / 100.0
            self.lrPID[1] = int(self.kd_value.text()) / 100.0
            self.lrPID[2] = int(self.ki_value.text()) / 100.0
        elif self.mode == 2:
            self.udPID[0] = int(self.kp_value.text()) / 100.0
            self.udPID[1] = int(self.kd_value.text()) / 100.0
            self.udPID[2] = int(self.ki_value.text()) / 100.0

    def saveValues(self): # Saving PID Values To File
        
        valueList = []
        valueList.append(self.fbPID[0])
        valueList.append(self.lrPID[0])
        valueList.append(self.udPID[0])

        valueList.append(self.fbPID[2])
        valueList.append(self.lrPID[2])
        valueList.append(self.udPID[2])

        valueList.append(self.fbPID[1])
        valueList.append(self.lrPID[1])
        valueList.append(self.udPID[1])
        

        with open("PID.txt","a") as f:
            fb = "Forward-Backward"
            lr = "Left-Right"
            ud = "Up-Down"
            temp = ["P", "I", "D"]
            temp_num = 0
            
            f.write(f"{datetime.now()}\n")
            f.write(f"{fb:20}{lr:20}{ud:20}\n")
            f.write(f"{temp[temp_num]}:")
            for num, element in enumerate(valueList):
                print("Num:", element)
               
                f.write(f"{str(element):20}")
                if (num + 1) % 3 == 0:
                    temp_num += 1
                    f.write("\n")
                    if(num < 8):
                        f.write(f"{temp[temp_num%3]}:")
            f.write("---------------------------------------------------\n")
        self.statusBar().showMessage('INFO: Values Saved.')
                    
            

    def updateFB(self, selected): # Forward-Backward PID Slider Update
        if selected:
            self.mode = 0
            self.kp_slider.setValue(int(self.fbPID[0] * 100))
            self.kd_slider.setValue(int(self.fbPID[1] * 100))
            self.ki_slider.setValue(int(self.fbPID[2] * 100))

            self.kp_value.setText(str(int(self.fbPID[0] * 100)))
            self.kd_value.setText(str(int(self.fbPID[1] * 100)))
            self.ki_value.setText(str(int(self.fbPID[2] * 100)))
    
    def updateLR(self, selected): # Yaw Left-Right PID Slider Update
        if selected:
            self.mode = 1
            self.kp_slider.setValue(int(self.lrPID[0] * 100))
            self.kd_slider.setValue(int(self.lrPID[1] * 100))
            self.ki_slider.setValue(int(self.lrPID[2] * 100))

            self.kp_value.setText(str(int(self.lrPID[0] * 100)))
            self.kd_value.setText(str(int(self.lrPID[1] * 100)))
            self.ki_value.setText(str(int(self.lrPID[2] * 100)))
    
    def updateUD(self, selected): # Up-Down PID Slider Update
        if selected:
            self.mode = 2
            self.kp_slider.setValue(int(self.udPID[0] * 100))
            self.kd_slider.setValue(int(self.udPID[1] * 100))
            self.ki_slider.setValue(int(self.udPID[2] * 100))

            self.kp_value.setText(str(int(self.udPID[0] * 100)))
            self.kd_value.setText(str(int(self.udPID[1] * 100)))
            self.ki_value.setText(str(int(self.udPID[2] * 100)))
    
    def takeOffDrone(self): # Take Off The Drone
        try:
            self.me.takeoff()
        except:
            print("Take Off Failed")
            self.statusBar().showMessage('ERROR: Take Off Failed.')
    def landDrone(self): # Land The Drone
        try:
            self.me.land()
        except:
            print("Land Failed.")
            self.statusBar().showMessage('ERROR: Land Failed.')


    def openManuelPage(self): # Opening Manual Page
        self.pageNum = 1
        self.manuel.show()
        self.hide()
    
    def closeManuelPage(self): # Closingf Manual Page
        self.pageNum = 0
        self.show()
        self.manuel.close()

     
    def closeEverything(self): # Closing Every Window
        if mode:
            self.me.streamoff()
        else:
            self.cap.release()

        self.close()
        self.key_info.close()
        self.isStopped = True
    
    
    def keyPressEvent(self, event): # Controlling Drone With Keyboard
        key = event.text()
        udspeed = 0
        yawspeed = 0
        fbspeed = 0
        lrspeed = 0
        if(key.lower() == "w"): # Moving Drone Up
            udspeed = self.keyboard_speed
        elif(key.lower() == "s"): # Moving Drone Down
            udspeed = -self.keyboard_speed
        elif(key.lower() == "a"): # Moving Drone Yaw Left
            yawspeed = -self.keyboard_speed
        elif(key.lower() == "d"): # Moving Drone Yaw Right
            yawspeed =  self.keyboard_speed 
        elif(key.lower() == "o"): # Moving Drone Forward
            fbspeed = self.keyboard_speed
        elif(key.lower() == "l"): # Moving Drone Backward
            fbspeed = -self.keyboard_speed
        elif(key.lower() == "k"): # Moving Drone Left
            lrspeed = -self.keyboard_speed
        elif(key.lower() == "ş"): # Moving Drone Right
            lrspeed = self.keyboard_speed
        elif(key.lower() == "e"): # Increasing Drone Speed
            self.keyboard_speed += 10
            if(self.keyboard_speed >= 100):
                self.keyboard_speed = 100
            self.speed_label.setText(str(self.keyboard_speed) + " cm/s")
        elif(key.lower() == "c"): # Decreasing Drone Speed
            self.keyboard_speed -= 10
            if(self.keyboard_speed <= 0):
                self.keyboard_speed = 0
            self.speed_label.setText(str(self.keyboard_speed) + " cm/s")
        else: # Any Key Pressed Without Up Keys, Drone Stop
            print("************************************Not Pressed.************************************")
            udspeed = 0
            yawspeed = 0
            fbspeed = 0
            lrspeed = 0
        
        if(self.keyboard_control.isChecked()): # If keyboard control checked send speeds to drone
            try:
                self.me.send_rc_control(lrspeed, fbspeed, udspeed, yawspeed)
            except: # If not connected the drone, give an error.
                print("Moving Drone Failed.")
                self.statusBar().showMessage('ERROR: Moving Drone Failed.')
                
    def checkmode(self):
        if(not mode):
            self.takeOff_button.setEnabled(False)
            self.land_button.setEnabled(False)
            self.manuel_button.setEnabled(False)
            self.keyboard_control.setEnabled(False)
        
       


    

if __name__ == "__main__":
    app = QApplication([])
    window = djiTello()
    window.runCode()

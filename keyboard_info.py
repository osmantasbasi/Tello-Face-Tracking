from PyQt5.uic import loadUi
from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import Qt

class KeyboardInfo(QWidget):
        def __init__(self):
                super().__init__()
                loadUi("keyboard_information.ui", self)
                self.ismanuel = False
                self.setWindowFlags(Qt.WindowStaysOnTopHint)
                
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
                elif(key.lower() == "c"):# Decreasing Drone Speed
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
                
                if(self.ismanuel):# If keyboard control checked send speeds to drone
                        try:
                                self.me.send_rc_control(lrspeed, fbspeed, udspeed, yawspeed)
                        except: # If not connected the drone, give an error.
                                print("Moving Drone Failed.")
                                self.statusBar().showMessage('ERROR: Moving Drone Failed.')
        def setManuel(self, v):
                self.ismanuel = v
                
              
              
              

                
                

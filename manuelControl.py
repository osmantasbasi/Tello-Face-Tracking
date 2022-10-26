from PyQt5.uic import loadUi
from PyQt5.QtWidgets import QWidget




class manuelControl(QWidget):
        def __init__(self):
                super().__init__()
                loadUi("manuel.ui",self)
                self.speeds = [0, 0, 0, 0] # F-B : L-R : U-D : YAW
                self.speed = 0
                self.drone = 0
                self.checkButtons()
                
        
        def checkButtons(self):

                self.fw_button.clicked.connect(lambda: self.updateVariables(self.fw_button))
                self.bw_button.clicked.connect(lambda: self.updateVariables(self.bw_button))
                self.left_button.clicked.connect(lambda: self.updateVariables(self.left_button))
                self.right_button.clicked.connect(lambda: self.updateVariables(self.right_button))
                self.up_button.clicked.connect(lambda: self.updateVariables(self.up_button))
                self.down_button.clicked.connect(lambda: self.updateVariables(self.down_button))
                self.yawL_button.clicked.connect(lambda: self.updateVariables(self.yawL_button))
                self.yawR_button.clicked.connect(lambda: self.updateVariables(self.yawR_button))
                self.speed_slider.valueChanged.connect(lambda: self.updateVariables(self.empty))
                self.stop_button.clicked.connect(lambda: self.updateVariables(self.stop_button))
                self.takeoff_button.clicked.connect(self.takeoff)
                self.land_button.clicked.connect(self.land)
                self.empty.hide()

        def takeoff(self):
                try:
                        self.drone.takeoff()
                except:
                        pass

        def land(self):
                try:
                        self.me.land()
                except:
                        pass
                
        def getSpeeds(self, me):
                self.drone = me
                me.send_rc_control(self.speeds[1], self.speeds[0], self.speeds[2], self.speeds[3])
                self.btry_label.setText("%" + str(me.get_battery()))

        
        def updateVariables(self, button):
                print(button.text())
                if button.text() == "Forward":
                        self.speeds[0] = self.speed

                elif button.text() == "Backward":
                        self.speeds[0] = -self.speed

                elif button.text() == "Left":
                        self.speeds[1] = -self.speed

                elif button.text() == "Right":
                        self.speeds[1] = self.speed
                        
                elif button.text() == "Up":
                        self.speeds[2] = self.speed

                elif button.text() == "Down":
                        self.speeds[2] = -self.speed

                elif button.text() == "YawLeft":
                        self.speeds[3] = -self.speed

                elif button.text() == "YawRight":
                        self.speeds[3] = self.speed

                elif button.text() == "Speed":
                        self.speed = int(self.spd_label.text())

                elif button.text() == "Stop":
                        self.speeds = [0, 0, 0, 0]

                print(self.speeds)

        
                        
        





'''app = QApplication([])
window = manuelControl()
window.show()
sys.exit(app.exec_())'''
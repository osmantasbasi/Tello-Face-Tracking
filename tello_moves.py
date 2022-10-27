from djitellopy import Tello
import time
import cv2

me = Tello()
me.connect()


ssid = "TurkTelekom_ZTU3FU_2.4GHz"
pass_ = "xsHhsA7DPFCt"


print("Battery: {}".format(me.get_battery()))
me.takeoff()
time.sleep(4)
me.enable_mission_pads()
time.sleep(4)
me.go_xyz_speed(30, 30, -50, 50)

time.sleep(10)
print("Landing")
me.land()
while True:
    
    #print(me.curve_xyz_speed())
    print("Roll: {} Pitch: {} Yaw: {}".format(me.get_roll(), me.get_pitch(), me.get_yaw()))
    

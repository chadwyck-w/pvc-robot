#robot.py

#rsync -avz ~/Desktop/pi_robot pi@robot.local:

#ssh pi@robot.local 'cd ~/pi_robot; python robot.py saved_model.pmdl'

import sys
import serial
import os
from time import sleep
from robot_body import robot_body

from demo_opts import get_device
from robot_face import robot_face
from robot_eye import robot_eye

def main():
    #os.system("espeak 'Hello!' --stdout | aplay")
    body = robot_body(serial.Serial('/dev/ttyACM0',9600, timeout=0))
    body.get_feedback()

    device = get_device()
    face = robot_face(device, body)
    eye = robot_eye(None)

    try:
        while True:
            body.distance()
            result = eye.detect_face()
            face.set_gaze(result)
            face.set_dist(body.get_last_distance())

    except KeyboardInterrupt:
        print "Exiting Program"

    except BaseException as e:
        print "Error Occurs, Exiting Program " + str(e)

    finally:
        body.shutdown()
        face.shutdown()
        pass

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass
import math
import time
import datetime
from luma.core.render import canvas
from time import sleep
import threading
import random

RANDOM_LOOK = 6
EYE_SIZE = 10
EYE_HEIGHT = 6
PUPIL_SIZE = 4
SMILE_HEIGHT = 8
SMILE_WIDTH = 20

def posn(angle, arm_length):
    dx = int(math.cos(math.radians(angle)) * arm_length)
    dy = int(math.sin(math.radians(angle)) * arm_length)
    return (dx, dy)

def scale(width, height, rectangle):
    x,y,w,h = rectangle
    x = int(float(x) * (float(width) / 720.0))
    y = int(float(y) * (float(height) / 480.0))
    w = int(float(w) * (float(width) / 720.0))
    h = int(float(h) * (float(height) / 480.0))
    return (x,y,w,h)

def rect_to_gaze(width, height, rectangle):
    #center of rect and size of rect / dimensions
    x,y,w,h = rectangle
    horizontal_gaze = x + (w/2)
    vertical_gaze = y + (y/2)
    gaze_depth = w
    return (horizontal_gaze,vertical_gaze,gaze_depth)

def reduce_distance(cur, dst):
    return cur + ((dst-cur)/2)

class robot_face(object):

    def __init__(self, device, bodyOfRobot):
        self.device = device
        self.dist = 0
        self.gaze = (self.device.width / 2, self.device.height / 2, 1)
        self.last_gaze = (self.device.width / 2, self.device.height / 2, 1)
        self.head_angle = 90
        self.eye_size = 15
        self.expression = 'neutral'
        self.expressions = ['fear', 'anger', 'sadness', 'joy', 'disgust', 'surprise', 'trust', 'anticipation', 'neutral']
        self.grades = [i for i in range(10)]
        self.grade = 0
        self.update = True
        self.bodyOfRobot = bodyOfRobot
        self.face_on = True
        self.gaze_updated = True
        self.face_detected = False

        self.thread = threading.Thread(target=self.run_update_face)
        self.thread.start()

    def run_update_face(self):
        while self.update:
            if self.face_on:
                self.update_expression()
                self.update_gaze()
                self.draw_eyes()
                if self.bodyOfRobot and self.gaze_updated:
                    self.gaze_updated = False
                    self.bodyOfRobot.look(self.head_angle)
            elif not self.face_on:
                self.device.clear()

            sleep(0.125)

    def set_expression(self, expression, grade):
        if hasattr(self, expression):
            self.expression = expression
            method_to_call = getattr(self, expression)
            method_to_call(grade)

    def update_expression(self):
        expression = self.expression
        if self.grade > 0:
            self.grade -= 1

    def update_gaze(self):
        x,y,s = self.gaze
        sx, sy, ss = self.last_gaze
        self.last_gaze = (reduce_distance(sx,x), reduce_distance(sy,y), reduce_distance(ss,s))
        new_angle = self.get_gaze_angle(self.last_gaze[0]) - self.head_angle
        self.head_angle = min(self.head_angle + new_angle, 180) # min(new_angle, 180)
        if self.head_angle < 1:
            self.head_angle = 1

    def neutral(self, grade):
        print 'neutral ' + str(grade)

    def fear(self, grade):
        print 'fear ' + str(grade)

    def anger(self, grade):
        print 'anger ' + str(grade)

    def joy(self, grade):
        print 'joy ' + str(grade)

    def disgust(self, grade):
        print 'disgust ' + str(grade)

    def fear(self, grade):
        print 'fear ' + str(grade)

    def surprise(self, grade):
        print 'surprise ' + str(grade)

    def trust(self, grade):
        print 'trust ' + str(grade)

    def anticipation(self, grade):
        print 'anticipation ' + str(grade)

    def draw_eyes(self):
        if self.face_detected:
            eye_height = EYE_HEIGHT
            eye_width = EYE_SIZE
            pupil_size = PUPIL_SIZE
        else:
            eye_height = EYE_HEIGHT - 2
            eye_width = EYE_SIZE - 2
            pupil_size = PUPIL_SIZE - 2

        with canvas(self.device) as draw:
            gaze_x = self.last_gaze[0]
            gaze_y = self.last_gaze[1]
            pupil_x = (self.device.width/2 - gaze_x)/20
            pupil_y = (self.device.height/2 - gaze_y)/20
            scale = min(self.last_gaze[2] / 4, 10)
            cx,cy = (gaze_x, gaze_y)
 
            #left eye
            draw.ellipse((cx - eye_width - 15, cy - eye_height, cx + eye_width - 15, cy + eye_height), fill="blue", outline="white")
            draw.ellipse((cx - pupil_size - 15 - pupil_x, cy - pupil_size - pupil_y, cx + pupil_size - 15 - pupil_x, cy + pupil_size - pupil_y), fill="black")

            #right eye
            draw.ellipse((cx - eye_width + 15, cy - eye_height, cx + eye_width + 15, cy + eye_height), fill="blue", outline="white")
            draw.ellipse((cx - pupil_size + 15 - pupil_x, cy - pupil_size - pupil_y, cx + pupil_size + 15 - pupil_x, cy + pupil_size - pupil_y), fill="black")

            self.smile(draw, cx, cy)

    def set_home_gaze(self):
        self.gaze = (self.device.width / 2, self.device.height / 2, 1)

    def set_gaze(self, rectangle):
        if rectangle is not None:
            self.face_detected = True
            self.gaze = rect_to_gaze(self.device.width / 2, self.device.height / 2,scale(min(self.device.width, 96), min(self.device.height, 64), rectangle))
            self.gaze_updated = True
        else:
            self.face_detected = False
            self.set_home_gaze()
            self.gaze = (self.gaze[0]+random.randint(-RANDOM_LOOK, RANDOM_LOOK), self.gaze[1]+random.randint(-RANDOM_LOOK/2, RANDOM_LOOK/2), self.gaze[2])
        #print self.gaze

    def get_gaze_angle(self, gaze):
        #convert gaze to angle to give to the body to control the servo
        return (180 - int((float(gaze) / float(self.device.width)) * 180.0)) + 4

    def clear(self):
        self.device.clear()

    def draw_rect(self,rectangle):
        with canvas(self.device) as draw:
            rect = scale(min(self.device.width, 96), min(self.device.height, 64), rectangle)
            x,y,w,h = rect
            draw.rectangle((x,y,x+w,y+h), outline="white")

    def smile(self, draw, x, y):
        if self.face_detected:
            smile_h = 0
        else:
            smile_h = SMILE_HEIGHT - 2

        draw.arc((x-SMILE_WIDTH, y+SMILE_HEIGHT+smile_h, x+SMILE_WIDTH, y+(SMILE_HEIGHT*2)), 0, 180, fill="white")

    def set_dist(self, dist):
        self.dist = dist

    def set_face_display(self, on):
        self.face_on = on

    def shutdown(self):
        self.update = False
        if self.thread.is_alive():
            self.thread.join()

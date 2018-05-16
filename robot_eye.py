import cv2

import config
import face

class robot_eye(object):

    def __init__(self, eye):
        self.eye = eye
        self.camera = config.get_camera()
        
    def detect_face(self):
        # Check for the positive face and unlock if found.
        image = self.camera.read()
        # Convert image to grayscale.
        image = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        # Get coordinates of single face in captured image.
        result = face.detect_single(image)
 
        #x, y, w, h = result
        #print(result)
        return result
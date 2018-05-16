#robot.py

#rsync -avz ~/Desktop/pi_robot pi@robot.local:

#ssh pi@robot.local 'cd ~/pi_robot; python robot.py saved_model.pmdl'

#python robot_with_ears.py saved_model.pmdl --config ssd1331Invert.conf

import sys
import serial
import os
from time import sleep

import speech_recognition as sr
import snowboythreaded

from robot_body import robot_body
from demo_opts import get_device
from robot_face import robot_face
from robot_eye import robot_eye

from parse_command import parseCommand #convert speech to do something

body = None

def audioRecorderCallback(fname):
    print "converting audio to text"
    r = sr.Recognizer()
    with sr.AudioFile(fname) as source:
        audio = r.record(source)  # read the entire audio file
    # recognize speech using Google Speech Recognition
    try:
        # for testing purposes, we're just using the default API key
        # to use another API key, use `r.recognize_google(audio, key="GOOGLE_SPEECH_RECOGNITION_API_KEY")`
        # instead of `r.recognize_google(audio)`
        result = r.recognize_google(audio)
        global body
        parseCommand(body, result)
        #print(result)
        #os.system("espeak \'" + result + "\' --stdout | aplay")
    except sr.UnknownValueError:
        print "Google Speech Recognition could not understand audio"
    except sr.RequestError as e:
        print "Could not request results from Google Speech Recognition service; {0}".format(e)

    os.remove(fname)

def main():

    model = 'saved_model.pmdl'

    #os.system("espeak 'Hello!' --stdout | aplay")
    global body
    body = robot_body(serial.Serial('/dev/ttyACM0',9600, timeout=0))
    body.get_feedback()

    device = get_device()
    face = robot_face(device, body)
    eye = robot_eye(None)

    # Set up the ears kitt.ai
    # Initialize ThreadedDetector object and start the detection thread
    threaded_detector = snowboythreaded.ThreadedDetector(model, sensitivity=0.5)
    threaded_detector.start()

    print('Listening... Press Ctrl+C to exit')

    # main loop
    threaded_detector.start_recog(audio_recorder_callback=audioRecorderCallback,
                                  sleep_time=0.03)

    # Let audio initialization happen before requesting input
    sleep(1)

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
        threaded_detector.terminate()
        pass

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass
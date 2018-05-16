import os
import sys
import signal
import time
import speech_recognition as sr
import snowboythreaded

#for my robot
import serial
from parse_command import parseCommand
from robot_body import robot_body

stop_program = False

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
        parseCommand(body, result)
        #print(result)
        #os.system("espeak \'" + result + "\' --stdout | aplay")
    except sr.UnknownValueError:
        print "Google Speech Recognition could not understand audio"
    except sr.RequestError as e:
        print "Could not request results from Google Speech Recognition service; {0}".format(e)

    os.remove(fname)

def signal_handler(signal, frame):
    global stop_program
    stop_program = True


def interrupt_callback():
    global interrupted
    return interrupted

if len(sys.argv) == 1:
    print "Error: need to specify model name"
    print "Usage: python demo.py your.model"
    sys.exit(-1)

model = sys.argv[1]
body = robot_body(serial.Serial('/dev/ttyACM0',9600, timeout=0))

# capture SIGINT signal, e.g., Ctrl+C
signal.signal(signal.SIGINT, signal_handler)

# Initialize ThreadedDetector object and start the detection thread
threaded_detector = snowboythreaded.ThreadedDetector(model, sensitivity=0.5)
threaded_detector.start()

print('Listening... Press Ctrl+C to exit')

# main loop
threaded_detector.start_recog(audio_recorder_callback=audioRecorderCallback,
                              sleep_time=0.03)

# Let audio initialization happen before requesting input
time.sleep(1)

# Do a simple task separate from the detection - addition of numbers
while not stop_program:
    try:
        num1 = int(raw_input("Enter the first number to add: "))
        num2 = int(raw_input("Enter the second number to add: "))
        print "Sum of number: {}".format(num1 + num2)
    except ValueError:
        print "You did not enter a number."

threaded_detector.terminate()





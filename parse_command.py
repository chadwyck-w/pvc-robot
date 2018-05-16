import os
from time import strftime
from parse import parse

MOVE_AMOUNT = 50

def parseCommand(robotbody, command):
    result_double = parse("{} {}", command)
    result_single = parse("{}", command)
    result = result_double
    if result is None and result_single is not None:
    	result = result_single
    print result
    if result is not None and command is not None:
        result = [i.lower() for i in result]
        print result

        if result[0] == 'move':
            if result[1] is not None and result[1] == 'forward':
                robotbody.move(MOVE_AMOUNT,MOVE_AMOUNT)
            if result[1] is not None and result[1] == 'back':
                robotbody.move(-MOVE_AMOUNT,-MOVE_AMOUNT)
            os.system("espeak \'ok\' --stdout | aplay")
            return

        if result[0] == 'turn':
            if result[1] is not None and result[1] == 'left':
                robotbody.move(-MOVE_AMOUNT,MOVE_AMOUNT)
            if result[1] is not None and result[1] == 'right':
                robotbody.move(MOVE_AMOUNT,-MOVE_AMOUNT)
            os.system("espeak \'ok\' --stdout | aplay")
            return

        if result[0] == 'look':
            if result[1] is not None and result[1] == 'left':
                robotbody.look(10)
            if result[1] is not None and result[1] == 'right':
                robotbody.look(165)
            if result[1] is not None and result[1] == 'center':
                robotbody.look(90)
            os.system("espeak \'ok\' --stdout | aplay")
            return

        if result[0] == 'stop':
            robotbody.move(0,0)
            os.system("espeak \'stopping\' --stdout | aplay")
            return

        if result is not None and result[0] == 'what':
            if result[1] is not None:
                time_question = result[1].find('time')
                print(time_question)
                if time_question is not None:
                    time_hour = strftime('%I').lstrip('0')
                    time_minute = strftime('%M %p').lstrip('0')
                    os.system("espeak \'The time is " + time_hour + ' ' + time_minute + "\' --stdout | aplay")
                    return

    os.system("espeak \'I did not understand the command " + command + "?\' --stdout | aplay")
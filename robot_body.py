import threading
import serial
from parse import parse

class robot_body(object):

    def __init__(self, serial_port):
        self.serial_port = serial_port
        self.listen = False
        self.thread = threading.Thread(target=self.read_from_port, args=(self.serial_port,))
        self.commands = [0] * 40
        self.responses = [0] * 40

    def get_last_distance(self):
        return self.responses[-1]

    def conform_response(self, result):
        if result[0] == 'd':
            self.responses.append(int(result[1]))
            self.responses.pop(0)
        return

    def is_complete_command(self, data):
        command = str(data)
        if command.find('<') < command.find('>'):
            result = parse("<{},{}>\r\n", command)
            if result:
                self.conform_response(result)
                return ''
        return data

    def handle_data(self, data):
        result = self.is_complete_command(data)
        return result

    def read_from_port(self, ser):
        tdata = ''
        while self.listen:
            while ser.inWaiting():
                tdata += ser.read(ser.inWaiting())
                if len(tdata) > 0:
                    tdata = self.handle_data(tdata)

    def get_feedback(self):
        self.listen = True
        if not self.thread.is_alive():
            self.thread = threading.Thread(target=self.read_from_port, args=(self.serial_port,))
            self.thread.start()
        return

    def move(self, left_motor, right_motor):
        if self.serial_port.isOpen():
            self.serial_port.write('<m,'+str(left_motor)+','+str(right_motor)+'>')
            self.commands.append('<m,'+str(left_motor)+','+str(right_motor)+'>')
            self.commands.pop(0)
        return

    def look(self, angle):
        if self.serial_port.isOpen():
            self.serial_port.write('<l,'+str(angle)+',0>')
            self.commands.append('<l,'+str(angle)+',0>')
            self.commands.pop(0)
        return
        
    def distance(self):
        if self.serial_port.isOpen():
            self.serial_port.write('<d>') #distance
            self.commands.append('<d>')
            self.commands.pop(0)
        return

    def shutdown(self):
        self.listen = False
        if self.thread.is_alive():
            self.thread.join()
        self.serial_port.close()
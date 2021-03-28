import csv
import os
import threading
import time
import random
import tkinter as Tk

values = []

class Camera():
    print("")

    def capture(self):
        print("")


class TwoWayGate(threading.Thread):
    to_exit = False
    activated = 0
    '''
    KEY: 0 = OFF, 1 = MODE A, 2 = MODE B
    '''

    def __init__(self, threadID):
        threading.Thread.__init__(self)
        self.threadID = threadID

    def switch(self, direction: int):
        self.activated = direction
        print("Two Way Gate Turn " + str(self.activated))
        if (self.activated == 0):
            # DO ACTION
            pass
        if (self.activated == 1):
            # DO ACTION
            pass
        if (self.activated == 2):
            # DO ACTION
            pass

class PressureSensor(threading.Thread):
    timer = 0
    id = 0
    to_exit = False

    def __init__(self, threadID, number, frequency):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.id = number
        self.timer = frequency

    def run(self):
        while (self.to_exit == False):
            time.sleep(0.5 + (0.5 * int(self.id)))
            self.read_sensor()

    def read_sensor(self):
        x = random.uniform(0, 50)
        values[self.id] = x
        print("Sensor " + str(self.id) + "reads: " + str(x))
        return x

    def getID(self):
        return self.threadID

    def get_value(self):
        return values[self.id]

    def terminate(self):
        self.to_exit = True


class Actuator(threading.Thread):
    id = 0
    is_depressurizer = False
    activated = False

    def __init__(self, threadID, id, is_depressurizer):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.id = id
        self.is_depressurizer = is_depressurizer

    def run(self):
        print()

    def switch(self, direction):
        self.activated = not self.activated
        print("Actuator " + str(self.id) + " Move " + str(self.activated))
        if (self.is_depressurizer):
            # DO ACTION
            if (self.activated == False):
                # DO ACTION
                pass
            if (self.activated == True):
                # DO ACTION
                pass
            pass
        else:
            # DO ACTION
            if (self.activated == False):
                # DO ACTION
                pass
            if (self.activated == True):
                # DO ACTION
                pass
            pass

    def getID(self):
        return self.threadID

    def get_is_depressurizer(self):
        return self.is_depressurizer

    def get_state(self):
        return self.activated

class WaterRobot(threading.Thread):
    frequency = 0
    pressure_sensors = []
    actuators = []
    two_way_gate = TwoWayGate(0)
    to_exit = False
    sensors_have_started = False
    '''
    Part 1: Robot
    '''

    def __init__(self, timerHz, numSensors, numActuators):
        super().__init__()
        threading.Thread.__init__(self)
        self.threadID = "ROBOTMAIN"
        print("Robot Init.")

        current_directory = os.getcwd()
        final_directory = os.path.join(current_directory, r'data')
        if not os.path.exists(final_directory):
            os.makedirs(final_directory)

        for i in range(0, numSensors):
            sensor = PressureSensor(i, i, 1000)
            self.pressure_sensors.append(sensor)
            values.append(0)
        for j in range(0, numActuators):
            is_dep = False
            if (j >= 4):
                is_dep = True
            self.actuators.append(Actuator(j, j, is_dep))

        with open('data/dataset.csv', 'w', newline='') as file:
            fieldnames = ['sensors', 'actuators']
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()

    def getListOfParts(self):
        for i in self.pressure_sensors:
            print("Pressure Sensor " + str(i.getID))
        for j in self.actuators:
            print("Actuator " + str(j.getID))

    def start(self):
        print("Sensor Start")
        self.sensors_have_started = True
        for i in self.pressure_sensors:
            i.start()

    def stop(self):
        print("Sensor Terminate")
        self.sensors_have_started = False
        for i in self.pressure_sensors:
            i.terminate()

    def run(self):
        print("A")
        '''
        while (self.to_exit == False):
            time.sleep(0.5)
            for i in self.pressure_sensors:
                i.read_sensor()
            self.saveState()
        '''

    def saveState(self):
        with open('data/dataset.csv', 'a', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=['sensors', 'actuators'])
            actuatorvalues = []
            for i in self.actuators:
                actuatorvalues.append(i.activated)

            writer.writerow({'sensors': values, 'actuators': actuatorvalues})

    def printOut(self, text):
        print(text)

def main():
    print()


if __name__ == "__main__":
    main()

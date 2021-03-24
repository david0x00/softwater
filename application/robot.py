import csv
import os
import threading
import time
import random
import tkinter as Tk

''' WEEK 1'''
# find an alternate way insteaad of sleep to "fire the methods or functions at a certain time"

# collect data and get pressure.
# either control the robot or give the robot procedures to execute.
# while the robot moves the data for pressure is being taken.

# TODO: add a function add another function that takes the photos of the robot as it changes position; this way we can see where the position of the robot is .
# TODO: every round we take a photo and save its positions and pressure, and the state of solenoid valves into a csv

# Priority 1: get data at a reliable frequency like 5 HZ. we have a variable Sampling frequency and changes how frequent we snap data
# Priority 2: Build a Soft Robot Class.
# Priority 3: How are we going to get input? allow manual control for robot actuating solenoids for now

'''WEEK 2'''
# In the GUI, Take data from pressure sensors -> actuate each solenoid.
# Setup and finish the Gui. Turn on solenoids, start experiment button, stop, such.

'''WEEK 3'''
# 4 Pressure Sensors, 8 Solenoid Actuators, 4 will pressurize a solenoid and 4 will depressurize. We have solenoid gate valve which is represented with on/off. we also have a water pump
# Write to CSV every sensor read. In the csv we need to write actuator states (Actuator is 1/0, solenoid is 1/0, Pump is 1/0, 1 = open, 0 = closed)

'''WEEK 4'''
# Add a 2 way pump switch
# Add a Gate solenoid valve
# finish the UI photo implementation
# add a text field that allows us to set frequency
# save dataset to a folder. browse
# I will create a start recording button for a set frequency

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


class WaterRobot:
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
        self.run()

    def stop(self):
        print("Sensor Terminate")
        self.sensors_have_started = False
        for i in self.pressure_sensors:
            i.terminate()

    def run(self):
        if (self.to_exit == False):
            time.sleep(0.5)
            for i in self.pressure_sensors:
                i.read_sensor()
            self.saveState()

    def updateSensors(self):
        return 0

    def updateActuators(self):
        return 0

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

import csv
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
# Setup and finish the Gui. Turn on solenoids, start expirement button, stop, such.

'''GOAL LIST'''

values = []


class Camera():
    print("")

    def capture(self):
        print("")


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
            time.sleep(0.5+(0.5*int(self.id)))
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
    def __init__(self, threadID, id):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.id = id
    def run(self):
        print("")

    def actuate_solenoid(self, direction):
        print("Actuator " + str(self.id) + " Move " + direction)

    def getID(self):
        return self.threadID

class WaterRobot:
    # add variables pressure sensors, solenoids, timestamp,
    # like sensor1;
    # take the state of the robot write to csv.
    # update function
    timer = 0
    pressure_sensors = []
    actuators = []
    to_exit = False
    sensors_have_started = False
    '''
    Part 1: Robot
    '''

    def __init__(self, timerHz, numSensors, numActuators):
        print("Robot Init.")
        for i in range(0, numSensors):
            sensor = PressureSensor(i, i, 1000)
            self.pressure_sensors.append(sensor)
            values.append(0)
        for j in range(0, numActuators):
            self.actuators.append(Actuator(j,j))

        with open('dataset.csv', 'w', newline='') as file:
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
        counter = 0

    def updateSensors(self):
        return 0

    def updateActuators(self):
        return 0

    def saveState(self):
        with open('dataset.csv', 'a', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=['sensors', 'actuators'])
            writer.writerow({'sensors': values, 'actuators': 0})


def main():
    print()


if __name__ == "__main__":
    main()

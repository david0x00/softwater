import csv
import os
import threading
import time
import random
import numpy as np

try:
    import board
    import busio

    i2c = busio.I2C(board.SCL, board.SDA)
    import adafruit_ads1x15.ads1115 as ADS
    from adafruit_ads1x15.analog_in import AnalogIn
    ads_0 = ADS.ADS1115(i2c)
    ads_1 = ADS.ADS1115(i2c, address=0x49)

    from adafruit_mcp230xx.mcp23008 import MCP23008
    mcp_0 = MCP23008(i2c)
    mcp_1 = MCP23008(i2c, address=0x21)
    robot_detected = True
except NotImplementedError:
    print("Robot not Connected")
    ads_0 = -1
    ads_1 = -1
    mcp_0 = -1
    mcp_1 = -1
    robot_detected = False

class Camera():
    print("")

    def capture(self):
        print("")

class TwoWayGate(threading.Thread):
    to_exit = False
    activatedA = False
    activatedB = False

    def __init__(self, threadID):
        threading.Thread.__init__(self)
        self.threadID = threadID

    def switch(self, gate: int):
        if (gate == 0):
            self.activatedA = not self.activatedA
        else:
            self.activatedB = not self.activatedB
        print("Switch " + str(gate))


class PressureSensor(threading.Thread):
    timer = 0
    id = 0
    to_exit = False

    def __init__(self, threadID, number, frequency, hardware_mapper=None):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.id = number
        self.timer = frequency
        self.hardware_mapper = hardware_mapper

    def run(self):
        pass
    

    def read_sensor(self):
        if self.hardware_mapper is not None:
            return self.hardware_mapper.readSensor(self.id)

        if (self.id == 0):
            # DO ACTION
            pass
        elif (self.id == 1):
            # DO ACTION
            pass
        elif (self.id == 2):
            # DO ACTION
            pass
        elif (self.id == 3):
            # DO ACTION
            pass

        x = random.uniform(0, 10)
        print("Sensor " + str(self.id) + "reads: " + str(x))
        return x

    def getID(self):
        return self.threadID

    def terminate(self):
        self.to_exit = True
    

class HardwareMapping:

    def __init__(self):
        self.actuator_pin_order = [1,0,3,2]
        self.actuator_boards = [mcp_0, mcp_1]
        self.sensor_pairs = [(ads_0, ADS.P0),(ads_0, ADS.P1),(ads_1, ADS.P0),(ads_1, ADS.P1)]
        self.setupPins()

    def setupPins(self):
        self.pins = []
        for module in self.actuator_boards:
            for pin_num in self.actuator_pin_order:
                temp_pin = module.get_pin(pin_num)
                temp_pin.switch_to_output(value=False)
                self.pins.append(temp_pin)
    
    def actuateSolenoid(self, id, new_state):
        self.pins[id].value = new_state
    
    def readSensor(self, id):
        sensor_pair = self.sensor_pairs[id]
        chan = AnalogIn(sensor_pair[0], sensor_pair[1])
        Va = chan.voltage
        P = ((Va / 5.0) + 0.040) / 0.004
        return P
    
class Actuator(threading.Thread):
    id = 0
    is_depressurizer = False
    activated = False

    def __init__(self, threadID, id, is_depressurizer, hardware_mapper=None):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.id = id
        self.is_depressurizer = is_depressurizer
        self.hardware_mapper = hardware_mapper

    def run(self):
        print()

    def switch(self):
        self.activated = not self.activated
        if self.hardware_mapper is not None:
            self.hardware_mapper.actuate(self.id, self.activated)
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
    frequency = 1
    pressure_sensors = []
    actuators = []
    two_way_gate = TwoWayGate(0)
    to_exit = False
    sensors_have_started = False
    data_filepath = ''
    values = []
    '''
    Part 1: Robot
    '''

    def __init__(self, timerHz, numSensors, numActuators):
        threading.Thread.__init__(self)
        self.threadID = "ROBOTMAIN"
        print("Robot Init.")

        current_directory = os.getcwd()
        final_directory = os.path.join(current_directory, r'data')
        if not os.path.exists(final_directory):
            os.makedirs(final_directory)

        if robot_detected:
            self.hardware_mapper = HardwareMapping()
        else:
            self.hardware_mapper = None

        for i in range(0, numSensors):
            sensor = PressureSensor(i, i, 1000, hardware_mapper=self.hardware_mapper)
            self.pressure_sensors.append(sensor)
            self.values.append(0)
        for j in range(0, numActuators):
            is_dep = False
            if (j % 2):
                is_dep = True
            self.actuators.append(Actuator(j, j, is_dep, hardware_mapper=self.hardware_mapper))

    def getListOfParts(self):
        for i in self.pressure_sensors:
            print("Pressure Sensor " + str(i.getID))
        for j in self.actuators:
            print("Actuator " + str(j.getID))

    def pause(self):
        pass

    def stop(self):
        print("Sensor Shutdown")
        self.to_exit = True

    def read_sensor(self, id : int):
        if(id < len(self.pressure_sensors) and id >= 0):
            self.values[id] = round(self.pressure_sensors[id].read_sensor(), 3)

    def actuate_solenoid(self, id : int):
        if(id < len(self.actuators) and id >= 0):
            self.actuators[id].switch()

    def run(self):
        while (self.to_exit == False):
            time.sleep(1 / self.frequency)
            for i in range(0, len(self.values)):
                self.values[i] = round(self.pressure_sensors[i].read_sensor(), 3)
            self.saveState()

    def saveState(self):
        with open(self.data_filepath, 'a', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=['sensors', 'actuators'])
            actuatorvalues = []
            for i in self.actuators:
                actuatorvalues.append(i.activated)

            writer.writerow({'sensors': self.values, 'actuators': actuatorvalues})

    def printOut(self, text):
        print(text)


def main():
    print()


if __name__ == "__main__":
    main()

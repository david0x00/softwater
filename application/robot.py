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
except NotImplementedError:
    print("Robot not Connected")
    ads_0 = -1
    ads_1 = -1
    mcp_0 = -1
    mcp_1 = -1

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

    def __init__(self, threadID, number, frequency):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.id = number
        self.timer = frequency

    def run(self):
        pass
    
    def getValue(self):
        chan = AnalogIn(ads_0, ADS.P1) #or can be ADS.P0
        Va = chan.voltage
        P = ((Va / 5.0) + 0.040) / 0.004

    def read_sensor(self):
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

        x = random.uniform(0, 50)
        print("Sensor " + str(self.id) + "reads: " + str(x))
        return x

    def getID(self):
        return self.threadID

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

    def switch(self):
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
        
    def open(self):
        pin = mcp_0.get_pin(1)
        pin.switch_to_output(value=True)
        pin.value = True

    def close(self):
        pin = mcp_0.get_pin(1)
        pin.switch_to_output(value=True)
        pin.value = False

    def getID(self):
        return self.threadID

    def get_is_depressurizer(self):
        return self.is_depressurizer

    def get_state(self):
        return self.activated

class Actuations:
    open_valve = True
    close_valve = False

class ModuleState:
    left_in_valve = Actuations.close_valve
    left_out_valve = Actuations.close_valve
    right_in_valve = Actuations.close_valve
    right_out_valve = Actuations.close_valve
    left_pressure = 0
    right_pressure = 0

class RobotModule:

    def __init__(self, pressure_reader, valve_driver):
        self.pressure_reader = pressure_reader
        self.valve_driver = valve_driver
        self.state = ModuleState()
    
    def execute(self):
        self.valve_driver.execute(self.state)
    
    def updateLeftPressureReading(self):
        self.state.left_pressure = self.pressure_reader.left()
    
    def updateRightPressureReading(self):
        self.state.right_pressure = self.pressure_reader.right()
    
    def openLeftInValve(self):
        self.state.left_in_valve = Actuations.open_valve

    def closeLeftInValve(self):
        self.state.left_in_valve = Actuations.close_valve

    def openLeftOutValve(self):
        self.state.left_out_valve = Actuations.open_valve

    def closeLeftOutValve(self):
        self.state.left_out_valve = Actuations.close_valve

    def openRightInValve(self):
        self.state.right_in_valve = Actuations.open_valve

    def closeRightInValve(self):
        self.state.right_in_valve = Actuations.close_valve

    def openRightOutValve(self):
        self.state.right_out_valve = Actuations.open_valve

    def closeRightOutValve(self):
        self.state.right_out_valve = Actuations.close_valve

class SoftWaterRobot(threading.Thread):
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

    def __init__(self, timerHz, num_modules):
        threading.Thread.__init__(self)
        self.threadID = "ROBOTMAIN"
        print("Robot Init.")

        current_directory = os.getcwd()
        final_directory = os.path.join(current_directory, r'data')
        if not os.path.exists(final_directory):
            os.makedirs(final_directory)
        
        self.num_modules = num_modules
        modules = []
        modules.append(RobotModule(ads_0, mcp_0))
        modules.append(RobotModule(ads_1, mcp_1))

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

    def __init__(self, timerHz, numSensors, numActuators, numberOfModules):
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
            self.values.append(0)
        for j in range(0, numActuators):
            is_dep = False
            if (j >= 4):
                is_dep = True
            self.actuators.append(Actuator(j, j, is_dep))

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

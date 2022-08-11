import threading
import random
import queue
from rate import Rate

import board
import busio

i2c = busio.I2C(board.SCL, board.SDA)
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn

ads_0 = ADS.ADS1115(i2c, address=0x48)
ads_1 = ADS.ADS1115(i2c, address=0x49)

from adafruit_mcp230xx.mcp23008 import MCP23008

mcp_0 = MCP23008(i2c, address=0x20)
mcp_1 = MCP23008(i2c, address=0x21)

from hat.Raspi_MotorHAT import Raspi_MotorHAT, Raspi_DCMotor

mh = Raspi_MotorHAT(addr=0x6f)
pump = mh.getMotor(1)
gate_valve = mh.getMotor(2)


class PumpAndGate(threading.Thread):
    to_exit = False
    pump_activated = False
    gate_valve_activated = False

    def __init__(self, threadID, hardware_mapper=None):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.hardware_mapper = hardware_mapper
    
    def set_pump(self, val):
        if val == False:
            if self.pump_activated:
                self.hardware_mapper.turnOffPump()
        else:
            if not self.pump_activated:
                self.hardware_mapper.turnOnPump()
        self.pump_activated = val
    
    def set_gate(self, val):
        if val == False:
            if self.gate_valve_activated:
                self.hardware_mapper.closeGateValve()
        else:
            if not self.gate_valve_activated:
                self.hardware_mapper.openGateValve()
        self.gate_valve_activated = val

    def switchPump(self):
        self.pump_activated = not self.pump_activated
        if self.hardware_mapper is not None:
            if self.pump_activated:
                self.hardware_mapper.turnOnPump()
            else:
                self.hardware_mapper.turnOffPump()
        print("Switch Pump " + str(self.pump_activated))

    def switchGateValve(self):
        self.gate_valve_activated = not self.gate_valve_activated
        if self.hardware_mapper is not None:
            if self.gate_valve_activated:
                self.hardware_mapper.openGateValve()
            else:
                self.hardware_mapper.closeGateValve()
        print("Switch Gate Valve " + str(self.gate_valve_activated))


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
        self.num_of_tries = 5

    def run(self):
        pass

    def read_sensor(self):
        if self.hardware_mapper is not None:
            for i in range(self.num_of_tries):
                try:
                    return self.hardware_mapper.readSensor(self.id)
                except OSError:
                    print("try: " + str(i))
            return -1
        else:
            randomnum = random.uniform(0, 10)
            return randomnum

    def getID(self):
        return self.threadID

    def terminate(self):
        self.to_exit = True


class HardwareMapping:
    def __init__(self):
        self.actuator_pin_order = [2, 3, 1, 0]
        self.actuator_boards = [mcp_0, mcp_1]
        self.setupPins()

        self.sensor_pairs = [(ads_0, ADS.P1), (ads_0, ADS.P0), (ads_1, ADS.P1), (ads_1, ADS.P0)]

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
        P = ((Va / 5.0) + 0.040) / 0.004  # kilopascels
        return P

    def turnOnPump(self):
        pump.run(Raspi_MotorHAT.BACKWARD)
        pump.setSpeed(100)

    def turnOffPump(self):
        pump.run(Raspi_MotorHAT.RELEASE)
        pump.setSpeed(0)

    def openGateValve(self):
        gate_valve.run(Raspi_MotorHAT.FORWARD)
        gate_valve.setSpeed(100)

    def closeGateValve(self):
        gate_valve.run(Raspi_MotorHAT.RELEASE)
        gate_valve.setSpeed(0)


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
    
    def set_val(self, val):
        if val == False:
            if self.activated:
                self.hardware_mapper.actuateSolenoid(self.id, val)
        else:
            if not self.activated:
                self.hardware_mapper.actuateSolenoid(self.id, val)
        self.activated = val

    def switch(self):
        self.activated = not self.activated
        if self.hardware_mapper is not None:
            self.hardware_mapper.actuateSolenoid(self.id, self.activated)
        print("Actuator " + str(self.id) + " Move " + str(self.activated))

    def getID(self):
        return self.threadID

    def get_is_depressurizer(self):
        return self.is_depressurizer

    def get_state(self):
        return self.activated


class WaterRobot(threading.Thread):
    frequency = 2
    pressure_sensors = []
    actuators = []
    to_exit = False
    values = []
    actuator_command_queue = queue.Queue()

    def __init__(self, numSensors, numActuators):
        threading.Thread.__init__(self)
        self.threadID = "ROBOTMAIN"
        print("Robot Init.")

        self.hardware_mapper = HardwareMapping()

        for i in range(0, numSensors):
            sensor = PressureSensor(i, i, 1000, hardware_mapper=self.hardware_mapper)
            self.pressure_sensors.append(sensor)
            self.values.append(0)
        for j in range(0, numActuators):
            is_dep = False
            if (j % 2):
                is_dep = True
            self.actuators.append(Actuator(j, j, is_dep, hardware_mapper=self.hardware_mapper))

        self.pump_and_gate = PumpAndGate(0, self.hardware_mapper)

    def turn_off_robot(self):
        self.set_pump(False)
        self.set_gate_valve(False)
        for i in range(8):
            self.set_solenoid(i, False)
        
    def return_to_home(self):
        self.set_pump(False)
        self.set_gate_valve(False)
        for i in range(8):
            if i % 2 == 0:
                self.set_solenoid(i, False)
            else:
                self.set_solenoid(i, True)

    def print_list_of_parts(self):
        for i in self.pressure_sensors:
            print("Pressure Sensor " + str(i.getID))
        for j in self.actuators:
            print("Actuator " + str(j.getID))

    def stop(self):
        print("Sensor Shutdown")
        for sensor in self.pressure_sensors:
            sensor.terminate()
        self.to_exit = True
    
    def switchPump(self):
        self.pump_and_gate.switchPump()
    
    def switchGateValve(self):
        self.pump_and_gate.switchGateValve()

    def __read_sensor(self, id):
        self.values[id] = round(self.pressure_sensors[id].read_sensor(), 3)

    def read_sensor(self, id: int):
        if (id < len(self.pressure_sensors) and id >= 0):
            self.__read_sensor(id)
    
    def read_sensors(self):
        for i in range(len(self.pressure_sensors)):
            self.read_sensor(i)

    def __actuate_solenoid(self, id):
        for i in range(5):
            try:
                self.actuators[id].switch()
            except OSError:
                print("try actuator: " + str(i))
    
    def set_solenoid(self, id, val):
        self.actuators[id].set_val(val)
    
    def set_gate_valve(self, val):
        self.pump_and_gate.set_gate(val)
    
    def set_pump(self, val):
        self.pump_and_gate.set_pump(val)

    def actuate_solenoid(self, id: int):
        if (id < len(self.actuators) and id >= 0):
            self.__actuate_solenoid(id)
    
    def runActuatorCommands(self):
        while not self.actuator_command_queue.empty():
            self.actuator_command_queue.get()()

    def run(self):
        while (self.to_exit == False):
            self.runActuatorCommands()
        
        self.actuator_command_queue = queue.Queue()
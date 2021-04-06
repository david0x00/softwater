import csv
import os
import threading
import time
import random
import datetime

try:
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

    from picamera import PiCamera

    robot_detected = True
    print("Robot Connected!")

except NotImplementedError:
    print("Robot not Connected: Not Implemented Error")
    ads_0 = -1
    ads_1 = -1
    mcp_0 = -1
    mcp_1 = -1
    robot_detected = False

except ValueError:
    print("Robot not Connected: Value Error")
    ads_0 = -1
    ads_1 = -1
    mcp_0 = -1
    mcp_1 = -1
    robot_detected = False


class Camera:

    def __init__(self,directory):
        self.camera = PiCamera()
        self.directory = directory

    def capture(self, count):
        file_name = self.directory + "/" + str(count) + ".jpg"
        self.camera.capture(file_name)
        print("Captured")


class PumpAndGate(threading.Thread):
    to_exit = False
    pump_activated = False
    gate_valve_activated = False

    def __init__(self, threadID, hardware_mapper=None):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.hardware_mapper = hardware_mapper

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

    def run(self):
        pass

    def read_sensor(self):
        if self.hardware_mapper is not None:
            print("Sensor " + str(self.id) + "reads: " + str(self.hardware_mapper.readSensor(self.id)))
            return self.hardware_mapper.readSensor(self.id)
        else:
            randomnum = random.uniform(0, 10)
            print("Sensor " + str(self.id) + "reads: " + str(randomnum))
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
    frequency = 1
    pressure_sensors = []
    actuators = []
    to_exit = False
    sensors_have_started = False
    data_filepath = ''
    detected_status = robot_detected
    values = []
    csv_headers = ["TIME", "M1-PL", "M1-PR", "M2-PL", "M2-PR", "M1-AL-IN", "M1-AL-OUT", "M1-AR-IN", "M1-AR-OUT", "M2-AL-IN", "M2-AL-OUT", "M2-AR-IN", "M2-AR-OUT"]

    def __init__(self, numSensors, numActuators):
        threading.Thread.__init__(self)
        self.threadID = "ROBOTMAIN"
        print("Robot Init.")

        current_directory = os.getcwd()
        print(current_directory)
        final_directory = os.path.join(current_directory, r'data')
        print(final_directory)
        if not os.path.exists(final_directory):
            os.makedirs(final_directory)

        if robot_detected:
            self.hardware_mapper = HardwareMapping()
            self.camera = Camera("/")
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

        self.pump_and_gate = PumpAndGate(0, self.hardware_mapper)

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

    def read_sensor(self, id: int):
        if (id < len(self.pressure_sensors) and id >= 0):
            self.values[id] = round(self.pressure_sensors[id].read_sensor(), 3)

    def actuate_solenoid(self, id: int):
        if (id < len(self.actuators) and id >= 0):
            self.actuators[id].switch()

    def run(self):
        with open(self.data_filepath, 'a', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=self.csv_headers)
            writer.writeheader()
        
        self.sample_count = 0
        self.start_time = datetime.datetime.now()

        while (self.to_exit == False):
            time.sleep(1 / self.frequency)
            for i in range(0, len(self.values)):
                self.values[i] = round(self.pressure_sensors[i].read_sensor(), 3)
            self.saveState()

    def saveState(self):
        with open(self.data_filepath, 'a', newline='') as file:
            #writer = csv.DictWriter(file, fieldnames=['sensors', 'actuators'])
            writer = csv.DictWriter(file, fieldnames=self.csv_headers)

            current_time = datetime.datetime.now()
            elapsed_time = round((current_time - self.start_time).total_seconds(),3)

            actuatorvalues = []
            for i in self.actuators:
                actuatorvalues.append(i.activated * 1)
            
            row_dict = {}
            for idx, h in enumerate(self.csv_headers):
                if idx == 0:
                    row_dict[h] = elapsed_time
                elif idx > 0 and idx < 5:
                    row_dict[h] = self.values[idx - 1]
                else:
                    row_dict[h] = actuatorvalues[idx - 5]

            #writer.writerow({'sensors': self.values, 'actuators': actuatorvalues})
            writer.writerow(row_dict)

    def printOut(self, text):
        print(text)


def main():
    print()


if __name__ == "__main__":
    main()

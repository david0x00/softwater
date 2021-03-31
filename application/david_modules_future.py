
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
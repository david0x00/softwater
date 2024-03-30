from usbcom import USBMessageBroker
from robot import *
from rate import Rate

import time
import os
import csv

# m0: out
# m1: in
# s0: a-in
# s1: a-out
# s2: c-out
# s3: b-out
# s4: c-in
# s5: b-in

class PressureController:
    def __init__(self, tolerance=0.5):
        self._pressure = None
        self._setPoint = -1
        self._tolerance = tolerance
        
        self._last = time.perf_counter()
    
    def setTargetPressure(self, value, adj=False):
        if adj:
            if self._setPoint < 0:
                return
            self._setPoint += value
        else:
            self._setPoint = value
        if self._setPoint < 70:
            self._setPoint = 70
        elif self._setPoint > 125:
            self._setPoint = 125
    
    def setPoint(self):
        return self._setPoint
    
    def update(self, currentPressure):
        dt = time.perf_counter() - self._last

        if self._pressure is None:
            self._pressure = currentPressure
        else:
            self._pressure = self._pressure * 0.8 + currentPressure *  0.2

        if self._setPoint == -1:
            self._setPoint = self._pressure
            return 0
        
        if self._pressure > self._setPoint + self._tolerance:
            return -1
        elif self._pressure < self._setPoint - self._tolerance:
            return 1
        return 0

class StageController:
    def __init__(self):
        self._last = time.perf_counter()
        self._pcons = [PressureController() for _ in range(3)]
    
    def setATarget(self, value, adj=False):
        self._pcons[0].setTargetPressure(value, adj)
    
    def setBTarget(self, value, adj=False):
        self._pcons[1].setTargetPressure(value, adj)
    
    def setCTarget(self, value, adj=False):
        self._pcons[2].setTargetPressure(value, adj)
    
    def getTargets(self):
        return [pcon.setPoint() for pcon in self._pcons]
    
    def update(self, stageState, stageStateNextInChain=None):
        dt = time.perf_counter() - self._last
        sd = SetDriver(stageState['stage'])

        for pcon in self._pcons:
            if pcon.setPoint() < 0:
                pcon.setTargetPressure(stageState['p1'])

        actions = []
        actions.append(self._pcons[0].update(stageState['p0']))
        actions.append(self._pcons[1].update(stageState['p3']))
        actions.append(self._pcons[2].update(stageState['p2']))
        
        #if 1 in actions:
        sd.modifyBit(BIT_M1, True)
        #if -1 in actions:
        sd.modifyBit(BIT_M0, True)
        
        if actions[0] == 1:
            sd.modifyBit(BIT_S0, True)
        elif actions[0] == -1:
            sd.modifyBit(BIT_S1, True)
        
        if actions[1] == 1:
            sd.modifyBit(BIT_S5, True)
        elif actions[1] == -1:
            sd.modifyBit(BIT_S3, True)

        if actions[2] == 1:
            sd.modifyBit(BIT_S4, True)
        elif actions[2] == -1:
            sd.modifyBit(BIT_S2, True)
        
        return sd

class Controller:
    stageData: dict = {}
    lightsData: dict = {}
    driverData: dict = {}

    _usb: USBMessageBroker
    _logFile: str = ""
    _logData: list = []

    _sendRate = Rate(25)
    _on = False

    def __init__(self, usb, console) -> None:
        self._usb = usb
        self._console = console

    def beginLog(self, file):
        self._logFile = file
        self.logging_on = True
    
    def endLog(self):
        self.logging_on = False
        if not self._logFile:
            return
        with open(self._logFile, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(StageState._ssTUP._fields)
            for ss in self._logData:
                row = []
                for field in StageState._ssTUP._fields:
                    row.append(ss[field])
                writer.writerow(row)
        self._console.print(f"Saved log file to {os.path.abspath(self._logFile)}", style="green", end="")
        self._logFile = None
    
    def update(self):
        self._usb.update()
        if not self._usb.connected():
            return False
        
        for msg in self._usb.messages:
            if msg.type == 1:
                ss = StageState(msg.data)
                
                if self._logFile:
                    self._logData.append(ss)
                
                if not ss['stage'] in self.stageData.keys():
                    self.lightsData[ss['stage']] = [[0, 0, 0] for _ in range(4)]
                    self.driverData[ss['stage']] = SetDriver(ss['stage'])
                self.stageData[ss['stage']] = ss
        self._usb.messages.clear()

        if self._sendRate.ready():
            for stage in self.lightsData:
                self._usb.send(5, packLEDS(stage, self.lightsData[stage]))
            for stage in self.driverData:
                self._usb.send(0, self.driverData[stage].pack())
        self._usb.update()
        return True

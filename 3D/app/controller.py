from usbcom import USBMessageBroker
from robot import *
from rate import Rate

import time
import os
import csv
import math
import numpy as np

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
        self._tp = 0
        self._tr = 0
        self._cp = 0
        self._cr = 0
        self._cy = 0
        self._pavg = -1
        self._y = 0
        self._p = 0
        self._r = 0

    def setATarget(self, value, adj=False):
        self._pcons[0].setTargetPressure(value, adj)
    
    def setBTarget(self, value, adj=False):
        self._pcons[1].setTargetPressure(value, adj)
    
    def setCTarget(self, value, adj=False):
        self._pcons[2].setTargetPressure(value, adj)
    
    def calibrateIMU(self, stageState, stageStateNextInChain):
        if stageStateNextInChain is None:
            return
        self._cp = stageStateNextInChain['pitch'] - stageState['pitch']
        self._cr = stageStateNextInChain['roll'] - stageState['roll']
        self._cy = stageStateNextInChain['yaw'] - stageState['yaw']
    
    def setPitchTarget(self, pitch, adj=False):
        if adj:
            self._tp = math.fmod(self._tp + pitch, 90)
        else:
            self._tp = math.fmod(pitch, 90)
    
    def setRollTarget(self, roll, adj=False):
        if adj:
            self._tr = math.fmod(self._tr + roll, 180)
        else:
            self._tr = math.fmod(roll, 180)
    
    def setIMUPressureAverage(self, value, adj=False):
        if adj:
            self._pavg += value
        else:
            self._pavg = value
        if self._pavg < 70:
            self._pavg = 70
        elif self._pavg > 125:
            self._pavg = 125
        
    def getPressureTargets(self):
        return [pcon.setPoint() for pcon in self._pcons]

    def getYPR(self):
        return self._y, self._p, self._r
    
    def getIMUTargets(self):
        return self._ty, self._tp, self._tr
    
    def update(self, stageState, stageStateNextInChain=None, imuControlled=False):
        dt = time.perf_counter() - self._last
        sd = SetDriver(stageState['stage'])

        if imuControlled:
            if stageStateNextInChain is None:
                return sd

            alpha = math.radians(stageStateNextInChain['yaw']-stageState['yaw'] - self._cy)
            beta = math.radians(stageStateNextInChain['pitch']-stageState['pitch'])
            gamma = math.radians(stageStateNextInChain['roll']-stageState['roll'])
            
            rz = np.array([
                [math.cos(alpha), -math.sin(alpha), 0],
                [math.sin(alpha), math.cos(alpha), 0],
                [0, 0, 1]
            ])

            ry = np.array([
                [math.cos(beta), 0, math.sin(beta)],
                [0, 1, 0],
                [-math.sin(beta), 0, math.cos(beta)]
            ])

            rx = np.array([
                [1, 0, 0],
                [0, math.cos(gamma), -math.sin(gamma)],
                [0, math.sin(gamma), math.cos(gamma)]
            ])

            r = rz.dot(ry).dot(rx)

            self._y = math.degrees(math.atan2(r[1][0], r[0][0]))
            self._p = math.degrees(-math.asin(r[2][0]))
            self._r = math.degrees(math.atan2(r[2][1], r[2][2]))

            aVec = np.array([0, -1])
            bVec = np.array([1 / math.sqrt(2), 1 / math.sqrt(2)])
            cVec = np.array([-1 / math.sqrt(2), 1 / math.sqrt(2)])
            pVec = (self._tp - self._p) * np.array([0, 1])
            rVec = (self._tr - self._r) * np.array([1, 0])

            self._y = aVal = pVec.dot(aVec.T) + rVec.dot(aVec.T)
            self._p = bVal = pVec.dot(bVec.T) + rVec.dot(bVec.T)
            self._r = cVal = pVec.dot(cVec.T) + rVec.dot(cVec.T)

            sd.modifyBit(BIT_M1, True)
            sd.modifyBit(BIT_M0, True)

            if aVal > 0:
                sd.modifyBit(BIT_S0, True)
            else:
                sd.modifyBit(BIT_S1, True)
            
            if bVal > 0:
                sd.modifyBit(BIT_S5, True)
            else:
                sd.modifyBit(BIT_S3, True)
            
            if cVal > 0:
                sd.modifyBit(BIT_S4, True)
            else:
                sd.modifyBit(BIT_S2, True)

        else:
            for pcon in self._pcons:
                if pcon.setPoint() < 0:
                    pcon.setTargetPressure(stageState['p1'])

            actions = []
            actions.append(self._pcons[0].update(stageState['p0']))
            actions.append(self._pcons[1].update(stageState['p3']))
            actions.append(self._pcons[2].update(stageState['p2']))
            
            sd.modifyBit(BIT_M1, True)
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

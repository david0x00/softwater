from usbcom import USBMessageBroker
from collections import namedtuple
import struct
import csv
from rate import Rate
import numpy as np

BIT_S0 = 0
BIT_S1 = 1
BIT_S2 = 2
BIT_S3 = 3
BIT_S4 = 4
BIT_S5 = 5
BIT_M0 = 6
BIT_M1 = 7

counts = [0 for _ in range(8)]

class StageState:
    _ssTUP = namedtuple("StageStatePacked", "stage id ping mem memExt timestamp init drivers p0 p1 p2 p3 yaw pitch roll")
    _ssFMT = "<BHIffQBBfffffff"
    data = None

    def __init__(self, data) -> None:
        packed = self._ssTUP._make(struct.unpack(self._ssFMT, data))
        self.data = packed._asdict()

    def initialized(self) -> bool:
        return self.data['init'] == 255
    
    def driver(self, bit) -> bool:
        return self.data['drivers'] & (1 << bit)

class SetDriver:
    _driverFMT = "<BB"
    _stage: int
    _state: int

    def __init__(self, stage, initialState=0) -> None:
        self._stage = stage
        self._state = initialState
    
    def modify(self, arr):
        for i in range(min(len(arr), 8)):
            self.modifyBit(i, arr[i])
    
    def modifyBit(self, bit, set) -> None:
        if set:
            self._state = self._state | (1 << bit)
        else:
            self._state = self._state & ~(1 << bit)
    
    def pack(self):
        return struct.pack(self._driverFMT, self._stage, self._state)

class Controller:
    stageData: dict

    _usb: USBMessageBroker
    _logFile: str = ""
    _logData: list = []

    _rate = Rate(10)
    _on = False

    def __init__(self, usb) -> None:
        self._usb = usb

    def beginLog(self, file):
        self._logFile = file
    
    def endLog(self):
        if not self._logFile:
            return
        with open(self._logFile, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(StageState._ssTUP._fields)
            for ss in self._logData:
                row = []
                for field in StageState._ssTUP._fields:
                    row.append(ss.data[field])
                writer.writerow(row)
        self._logFile = None
    
    def compute(self):
        pass
    
    def update(self):
        self._usb.update()
        if not self._usb.connected():
            return False
        
        for msg in self._usb.messages:
            if msg.type == 1:
                ss = StageState(msg.data)
                counts[ss.data["stage"]] += 1
                if self._logFile:
                    self._logData.append(ss)
                print(ss.data)
        self._usb.messages.clear()
        self._usb.update()
            
if __name__ == "__main__":
    usb = USBMessageBroker("COM5", baudrate=1e6)
    controller = Controller(usb)

    controller.beginLog("./log.csv")

    rate = Rate(100)
    
    
    try:
        for i in range(8):
            sd = SetDriver(i)
            usb.send(0, sd.pack())

        while True:
            if rate.ready():
                for i in range(8):
                    sd = SetDriver(i)
                    sd.modifyBit(BIT_S0, True)
                    sd.modifyBit(BIT_S1, True)
                    sd.modifyBit(BIT_S2, True)
                    sd.modifyBit(BIT_S3, True)
                    sd.modifyBit(BIT_S4, True)
                    sd.modifyBit(BIT_S5, True)
                    sd.modifyBit(BIT_M0, False)
                    sd.modifyBit(BIT_M1, False)
                    usb.send(0, sd.pack())

            controller.update()
    except KeyboardInterrupt:
        controller.endLog()

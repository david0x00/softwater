from collections import namedtuple
import struct

BIT_S0 = 0
BIT_S1 = 1
BIT_S2 = 2
BIT_S3 = 3
BIT_S4 = 4
BIT_S5 = 5
BIT_M0 = 6
BIT_M1 = 7

class StageState:
    _ssTUP = namedtuple("StageStatePacked", "stage id ping mem memExt timestamp init drivers p0 p1 p2 p3 yaw pitch roll")
    _ssFMT = "<BHIffQBBfffffff"
    _data = None

    def __init__(self, data) -> None:
        packed = self._ssTUP._make(struct.unpack(self._ssFMT, data))
        self._data = packed._asdict()

    def initialized(self) -> bool:
        return self._data['init'] == 255
    
    def driver(self, bit) -> bool:
        return self._data['drivers'] & (1 << bit)

    def __getitem__(self, key):
        return self._data[key]

    def keys(self):
        return self._data.keys()

class SetDriver:
    _driverFMT: str = "<BB"
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
    
def packLEDS(stage, arr):
    return struct.pack("<B" + "B" * 12, stage, *arr[0], *arr[1], *arr[2], *arr[3])
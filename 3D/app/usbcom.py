import serial
import serial.serialutil
import serial.tools.list_ports
import struct
from collections import namedtuple
import numpy as np
from rate import Rate
import time
from typing import List

FNVOB = np.uint32(0x811c9dc5)
FNVP = np.uint32(0x01000193)

np.seterr(over='ignore')

def hash32(arr: List) -> None:
    val = np.array([FNVOB])
    for byte in arr:
        val *= FNVP
        valarr = bytearray(val.tobytes())
        valarr[0] ^= byte
        val = np.frombuffer(valarr, dtype=np.uint32)
    return val

class USBRecvMessage:
    def __init__(self, type: int, data: bytearray) -> None:
        self.type = type
        self.data = data

class PriorityQueue:
    _data: dict = dict()
    _cnt: int = 0

    def __init__(self) -> None:
        pass

    def put(self, priority: int, data) -> None:
        priority = abs(priority)
        if priority in self._data.keys():
            self._data[priority].append(data)
        else:
            self._data[priority] = [data]
        self._cnt += 1
    
    def get(self):
        if len(self._data.keys()) == 0:
            return None
        key = min(self._data.keys())
        data = self._data[key].pop()
        if len(self._data[key]) == 0:
            self._data.pop(key)
        self._cnt -= 1
        return key, data

    def empty(self) -> bool:
        return len(self._data.keys()) == 0

    def __len__(self) -> int:
        return self._cnt

class USBMessageBroker:
    _Header = namedtuple('header', 'type priority len dhash hhash')
    _header_format: str = "<BBHII"
    _header_size: int = struct.calcsize(_header_format)
    _header_data_size: int = struct.calcsize("<BBHI")

    _send_msgs = PriorityQueue()
    _buf: List[bytes] = []
    _header: _Header = None
    _msgdarr: List[bytes] = []
    _missed: int = 0
    _received: int = 0
    _transfered: int = 0

    _PING: int = 0
    _REPING: int = 1
    _reserved_types: int = 4

    _ping_timeout: int = 0.5
    _last_ping_send: int = 0
    _ping_time: float = float('inf')
    _ping_id: int = 0
    _ping_rate: Rate = Rate(1 / _ping_timeout)

    messages: List[USBRecvMessage] = []

    _msgs = 0

    def __init__(self, device: str, baudrate: int=500000) -> None:
        self._device_name = device
        self._baudrate = baudrate
        self._device = serial.Serial(port=device, baudrate=baudrate)

    def send(self, type: int, data: bytearray=bytearray(), priority: int=2) -> None:
        self._send(type + self._reserved_types, priority + 1, data)
    
    def _send(self, type: int, priority: int, data: bytearray) -> None:
        msg = struct.pack("<BBHI", type, priority, len(data), hash32(data)[0])
        msg += struct.pack("<I", hash32(msg)[0])
        msg += data
        self._send_msgs.put(priority, msg)

    def connected(self) -> bool:
        return self._device.is_open and self._ping_time < self._ping_timeout

    def ping(self) -> float:
        return self._ping_time
    
    def bytes_transfered(self) -> int:
        return self._transfered

    def bytes_received(self) -> int:
        return self._received
    
    def bytes_missed(self) -> int:
        return self._missed
    
    def update(self) -> None:
        problem = False

        if self._device.is_open:
            try:
                serial_data = self._device.read_all()
                self._received += len(serial_data)
                self._buf.extend(list(serial_data))
            except serial.serialutil.SerialException:
                problem = True
                       
            while len(self._buf) >= self._header_size:
                if not self._header and len(self._buf) >= self._header_size:
                    self._header = self._Header._make(struct.unpack(self._header_format, bytes(self._buf[0:self._header_size])))
                    if self._header.hhash == hash32(self._buf[0:self._header_data_size]):
                        del self._buf[0:self._header_size]
                    else:
                        self._missed += 1
                        self._header = None
                        del self._buf[0]
                if self._header:
                    extend_len = min(len(self._buf), self._header.len - len(self._msgdarr))
                    self._msgdarr.extend(self._buf[0:extend_len])
                    del self._buf[0:extend_len]

                    if len(self._msgdarr) == self._header.len:
                        if self._header.dhash == hash32(self._msgdarr):
                            self._msgs += 1
                            if self._header.type == self._PING:
                                self._send(self._REPING, 0, bytes(self._msgdarr))
                            elif self._header.type == self._REPING:
                                if (int.from_bytes(bytes(self._msgdarr), 'little') == self._ping_id):
                                    self._ping_time = time.perf_counter() - self._last_ping_send
                            else:
                                self.messages.append(USBRecvMessage(self._header.type - self._reserved_types, bytes(self._msgdarr)))
                        self._header = None
                        self._msgdarr = []                
                
            if self._ping_rate.ready():
                self._ping_id += 1
                self._send(self._PING, 0, self._ping_id.to_bytes(4, 'little'))
                self._last_ping_send = time.perf_counter()
            
            while not self._send_msgs.empty():
                priority, msg = self._send_msgs.get()
                try:
                    self._device.write(msg)
                    self._transfered += len(msg)
                except serial.serialutil.SerialException:
                    problem = True
                    self._send_msgs.put(priority, msg)
                    break

        if (problem):
            self._ping_time = float('inf')
            try:
                self._device = serial.Serial(port=self._device_name, baudrate=self._baudrate)
            except serial.serialutil.SerialException:
                pass
    
if __name__ == "__main__":
    ports = serial.tools.list_ports.comports()
    if len(ports) == 0:
        print("not connected")
        quit()
    
    broker = USBMessageBroker("COM4", baudrate=2000000)

    debug_rate = Rate(2)
    last_ping = 0

    while True:
        if broker.connected():
            # if (debug_rate.ready()):
            #     print(f'{broker.ping() * 1000} ms', len(broker.messages), broker.bytes_missed(), broker.bytes_transfered(), broker.bytes_received(), len(broker._send_msgs))
            for msg in broker.messages:
                if msg.type == 1:
                    ssTUP = namedtuple('StageStatePacked', 'stage timestamp ping init drivers p0 p1 p2 p3 yaw pitch roll')
                    ssFMT = "<BQIBBfffffff"
                    ssTUP = ssTUP._make(struct.unpack(ssFMT, msg.data))
                    print(ssTUP)
            broker.messages.clear()
        else:
            first = True
        broker.update()

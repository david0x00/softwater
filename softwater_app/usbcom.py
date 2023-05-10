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
    
class USBSendMessage:
    def __init__(self, type: int, data: bytearray) -> None:
        header = np.zeros(4, dtype=np.uint32)
        header[0] = type
        header[1] = len(data)
        header[2] = hash32(data)
        header[3] = hash32(header[0:3].tobytes())
        self.type = type
        self.data = bytearray(header.tobytes())
        self.data.extend(data)

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
    _Header = namedtuple('header', 'type datalen dhash hhash')
    _header_format: str = '<IIII'
    _header_size: int = struct.calcsize(_header_format)
    _header_data_size: int = struct.calcsize('<III')

    _send_msgs = PriorityQueue()
    _buf: List[bytes] = []
    _header: _Header = None
    _msgdarr: List[bytes] = []
    _missed: int = 0
    _received: int = 0
    _transfered: int = 0

    _PING: int = 0
    _REPING: int = 1
    _RAM: int = 2
    _reserved_types: int = 10

    _ping_timeout: int = 1
    _last_ping_send: int = 0
    _ping_time: float = float('inf')
    _ping_id: int = 0
    _ping_rate: Rate = Rate(1 / _ping_timeout)

    _allowed_bytes: int = 1000

    messages: List[USBRecvMessage] = []

    _msgs = 0

    def __init__(self, device: str, baudrate: int=115200) -> None:
        self._device_name = device
        self._baudrate = baudrate
        self._device = serial.Serial(port=device, baudrate=baudrate)

    def send(self, type: int, data: bytearray=bytearray(), priority: int=2) -> None:
        self._send(type + self._reserved_types, data, priority + 1)
    
    def _send(self, type: int, data: bytearray, priority: int) -> None:
        self._send_msgs.put(priority, USBSendMessage(type, data))

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
                    extend_len = min(len(self._buf), self._header.datalen - len(self._msgdarr))
                    self._msgdarr.extend(self._buf[0:extend_len])
                    del self._buf[0:extend_len]

                    if len(self._msgdarr) == self._header.datalen:
                        if self._header.dhash == hash32(self._msgdarr):
                            self._msgs += 1
                            if self._header.type == self._PING:
                                self._send(self._REPING, self._msgdarr, 0)
                            elif self._header.type == self._REPING:
                                if (int.from_bytes(bytes(self._msgdarr), 'little') == self._ping_id):
                                    self._ping_time = time.perf_counter() - self._last_ping_send
                            elif self._header.type == self._RAM:
                                [heap_size, free_heap_size] = struct.unpack('<II', bytes(self._msgdarr))
                                self._allowed_bytes = (heap_size + free_heap_size) * 0.7 - heap_size
                            else:
                                self.messages.append(USBRecvMessage(self._header.type - self._reserved_types, bytes(self._msgdarr)))
                        self._header = None
                        self._msgdarr = []                
                
            if self._ping_rate.ready():
                self._ping_id += 1
                self._send(self._PING, self._ping_id.to_bytes(4, 'little'), 0)
                self._last_ping_send = time.perf_counter()
            
            while not self._send_msgs.empty():
                priority, msg = self._send_msgs.get()
                if self._allowed_bytes - len(msg.data) > 0:
                    try:
                        self._device.write(msg.data)
                        self._transfered += len(msg.data)
                        self._allowed_bytes -= len(msg.data)
                    except serial.serialutil.SerialException:
                        problem = True
                        self._send_msgs.put(priority, msg)
                        break
                else:
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
    
    broker = USBMessageBroker("COM7", baudrate=500000)

    debug_rate = Rate(1)
    last_ping = 0

    first = True

    while True:
        if broker.connected():
            if (debug_rate.ready()):
                print(f'{broker.ping() * 1000} ms', len(broker.messages), broker.bytes_missed(), broker.bytes_transfered(), broker.bytes_received(), len(broker._send_msgs))
            broker.messages.clear()
        else:
            first = True
        broker.update()

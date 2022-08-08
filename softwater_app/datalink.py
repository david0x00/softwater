import pickle
import zmq
from rate import Rate
import time

PRIORITY_LOW    = 0
PRIORITY_MEDIUM = 1
PRIORITY_HIGH   = 2

MSGTYPE_PING    = 0
MSGTYPE_REPING  = 1
MSGTYPE_USER    = 2

class DataLink():
    def __init__(self, name, server, host="localhost", port=5005):
        self.name = name

        self._context = zmq.Context()
        self._socket = self._context.socket(zmq.PAIR)
        if server:
            self._socket.bind(f"tcp://*:{str(port)}")
        else:
            self._socket.connect(f"tcp://{host}:{str(port)}")

        self.ping_time = 0.5
        self.ping_timeout = 3

        self._pinging = False
        self._ping_start = 0

        self._msg_id_count = 0
        self._latency = None

        self._send_msgs = []
        self._receive_msgs = []

    def latency(self, string=False):
        if string:
            if self._latency is None:
                return "??? ms"
            return "{:.2f} ms".format(self._latency * 1000)
        return self._latency

    def send(self, data, priority=PRIORITY_LOW):
        self._send(data, MSGTYPE_USER, priority)
        
    def _send(self, data, msg_type, priority):
        self._send_msgs.append({
            'sender': self.name,
            'type': msg_type,
            'priority': priority,
            'data': data
        })

    def data_available(self):
        return len(self._receive_msgs) != 0

    def get(self):
        if len(self._receive_msgs) != 0:
            msg = self._receive_msgs[0]
            self._receive_msgs.pop(0)
            return msg
        return None

    def update(self):
        t = time.perf_counter()

        # RECEIVING
        try:
            msg = pickle.loads(self._socket.recv(flags=zmq.NOBLOCK))
            id = msg['type']
            if id == MSGTYPE_PING:
                self._send(None, MSGTYPE_REPING, PRIORITY_HIGH)
            elif id == MSGTYPE_REPING:
                self._latency = t - self._ping_start
                self._pinging = False
            else:
                self._receive_msgs.append(msg)
        except zmq.error.Again:
            pass

        # SENDING
        if self._pinging:
            if t - self._ping_start > self.ping_timeout:
                self._pinging = False
                self._latency = None
        elif t - self._ping_start > self.ping_time:
            self._pinging = True
            self._ping_start = t
            self._send(None, MSGTYPE_PING, PRIORITY_HIGH)

        while len(self._send_msgs) != 0:
            priority = PRIORITY_LOW
            for i in range(len(self._send_msgs)):
                m = self._send_msgs[i]
                if m['priority'] >= priority:
                    priority = m['priority']
                    msg = self._send_msgs[i]

            msg = pickle.dumps(msg, protocol=4)
            try:
                self._socket.send(msg, flags=zmq.NOBLOCK)
                self._send_msgs.pop(i)
            except zmq.error.Again:
                break


if __name__ == "__main__":
    d1 = DataLink("Link1", False, host="169.254.11.63")
    r = Rate(5)

    while True:
        if r.ready():
            print(d1.latency(string=True))
        d1.update()

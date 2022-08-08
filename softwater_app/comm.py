import socket
import pickle
import struct


class Link:
    def __init__(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def start_server(self, port):
        self.socket.bind("", port)
        self.socket.listen()
    
    def connect(self, tcp_ip, port):
        try:
            self.socket.connect((tcp_ip, port))
            return True
        except ConnectionRefusedError:
            return False
    
    def send_msg(self, msg):
        byte_msg = pickle.dumps(msg, protocol=5)
        out_msg = struct.pack('>I', len(byte_msg)) + byte_msg
        self.socket.sendall(out_msg)

    def recv_msg(self):
        raw_msglen = self._recvall(4)
        if not raw_msglen:
            return None
        msglen = struct.unpack('>I', raw_msglen)[0]
        return self._recvall(msglen)

    def _recvall(self, n):
        data = bytearray()
        while len(data) < n:
            packet = self.socket.recv(n - len(data))
            if not packet:
                return None
            data.extend(packet)
        return data
    
if __name__=="__main__":
    import time

    link = Link()

    while not link.connect("169.254.11.63", 5005):
        time.sleep(1)

    while True:
        link.send_msg("Hello!!")
        time.sleep(1)

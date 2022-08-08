import socket
import pickle
import struct
import threading


class Link:
    def __init__(self):
        self._is_server = False
        self._conn = None
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def start_server(self, port):
        self.socket.bind(("", port))
        self.socket.listen()
        self._is_server = True
    
    def accept(self):
        if self._is_server:
            self._conn, addr = self.socket.accept()
    
    def connect(self, tcp_ip, port):
        try:
            self.socket.connect((tcp_ip, port))
            return True
        except ConnectionRefusedError:
            return False
    
    def send_msg(self, msg):
        byte_msg = pickle.dumps(msg, protocol=5)
        out_msg = struct.pack('>I', len(byte_msg)) + byte_msg
        if self._is_server:
            if not self._conn:
                return self._conn.sendall(out_msg)
            return False
        else:
            return self.socket.sendall(out_msg)

    def recv_msg(self):
        raw_msglen = self._recvall(4)
        if not raw_msglen:
            return None
        msglen = struct.unpack('>I', raw_msglen)[0]
        return pickle.loads(self._recvall(msglen))

    def _recvall(self, n):
        data = bytearray()
        s = self.socket
        if self._is_server:
            s = self._conn
            if not self._conn:
                return None
        while len(data) < n:
            packet = s.recv(n - len(data))
            if not packet:
                return None
            data.extend(packet)
        return data

def client_thread():
    link = Link()
    while not link.connect("localhost", 5005):
        time.sleep(1)
    
    while True:
        link.send_msg("Hello!!")
        time.sleep(1)
    
if __name__=="__main__":
    import time

    server = Link()
    server.start_server(5005)

    threading.Thread(target=client_thread, daemon=True).start()

    server.accept()

    while True:
        #start = time.time()
        msg = server.recv_msg()
        if not msg:
            print("E")
        #print(time.time() - start)
        print(msg)
        #time.sleep(1)


    

    

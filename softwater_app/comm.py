from serial import Serial

if __name__ == "__main__":
    dev = Serial(port="COM7", baudrate=115200)
    try:
        dev.open()
    except:
        pass
    
    msgs = []
    while dev.is_open:
        input = bytearray(dev.read_all())
        msgs.append(input.split(b'$'))
        print(msgs)
        
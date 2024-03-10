import os
# import keyboard
from pynput import keyboard
import serial.tools.list_ports
from colorama import Fore, Style
from collections import namedtuple
import struct
import curses
import math
import csv
import time

from usbcom import USBMessageBroker
from rate import Rate
import time

def connect():
    while True:    
        while True:
            print(f"{Fore.GREEN}Select Port:")
            ports = serial.tools.list_ports.comports()
            for (i, port) in enumerate(ports):
                print(f"{Fore.YELLOW}{i}: {port.device}")
            if len(ports) == 0:
                print(f"{Fore.RED}No USB devices found")
                time.sleep(2)
                print("")
                continue
            print("")
            
            print(f"{Fore.GREEN}Selection: {Fore.YELLOW}", end="")
            try:
                selection = input()
            except EOFError:
                continue
            
            try:
                selection = int(selection)
                if selection >= len(ports):
                    continue
                break
            except:
                continue
        
        while True:
            print(f"{Fore.GREEN}Baud Rate (default: 500000): {Fore.YELLOW}", end="")
            try:
                baudrate = input()
            except EOFError:
                continue
            
            try:
                if baudrate == "":
                    baudrate = 500000
                else:
                    baudrate = int(baudrate)
                if baudrate < 1:
                    continue
                break
            except:
                continue
        print(Style.RESET_ALL)
        
        return USBMessageBroker(ports[selection].device, baudrate)
    
class DynamicTextBox:
    def __init__(self, scr, text=None):
        self._scr = scr
        self.text = ""
        self._last_len = 0
        if text is not None:
            self.set_text(text)
            self._last_len = len(text)
    
    def set_text(self, text):
        self.text = text
    
    def put(self, y=None, x=None, pair=None):
        if self._last_len > len(self.text):
            text = self.text + " " * (self._last_len - len(self.text))
        else:
            text = self.text
                
        self._last_len = len(self.text)
        
        if y is None:
            if pair is not None:
                self._scr.addstr(text, pair)
            else:
                self._scr.addstr(text)
        elif x is None:
            if pair is not None:
                self._scr.addstr(y, text, pair)
            else:
                self._scr.addstr(y, text)
        else:
            if pair is not None:
                self._scr.addstr(y, x, text, pair)
            else:
                self._scr.addstr(y, x, text)

def is_set(x, bit):
    return x & 1 << bit != 0

logging = False
log_data = []
log_start = 0

def main(stdscr, comm):
    rate = Rate(1)
    refresh = False
    ss_names = namedtuple("StageState", 'timestamp init driver p0 p1 p2 p3 yaw pitch roll power')
    ss_format = "<QBBffffffff"
    ss = None

    def key_press_cb(event):
        # if event.name in "12345678" and ss:
        if hasattr(event, 'char'):
            name = event.char
        else:
            name = ""

        if name in "12345678" and ss:
            # idx = "12345678".index(event.name)
            idx = "12345678".index(name)
            comm.send(1, struct.pack("<BB", idx, not is_set(ss['driver'], idx)))
        # elif event.name == 'l':
        elif (name) == 'l':
            global logging, log_data, log_start
            if logging:
                if not os.path.exists("./logs"):
                    os.mkdir("./logs")
                max = None
                for filename in os.listdir("./logs"):
                    num = int(filename.split(".")[0])
                    if max is None or num > max:
                        max = num
                if max is None:
                    max = 0
                else:
                    max += 1
                with open(f"./logs/{max}.csv", "w", newline="") as f:
                    writer = csv.writer(f)
                    fields = ["timestamp", "init", "s0", "s1", "s2", "s3", "s4", "s5", "m0", "m1", "p0", "p1", "p2", "p3", "yaw", "pitch", "roll", "power"]
                    writer.writerow(fields)
                    for data in log_data:
                        writer.writerow([
                            data["timestamp"],
                            data["init"],
                            *[is_set(data["driver"], i) for i in range(8)],
                            *data["pressure"],
                            *data["ypr"],
                            data["power"]
                        ])
                logging = False
            else:
                log_data = []
                logging = True
                log_start = time.perf_counter()
    # keyboard.on_press(key_press_cb)

    # pynput
    listener = keyboard.Listener(
        on_press=key_press_cb)
    listener.start()


    curses.curs_set(0)
    curses.use_default_colors()
    green = 1
    yellow = 2
    red = 3
    magenta = 4
    blue = 5
    curses.init_pair(green, curses.COLOR_GREEN, -1)
    curses.init_pair(yellow, curses.COLOR_YELLOW, -1)
    curses.init_pair(red, curses.COLOR_RED, -1)
    curses.init_pair(magenta, curses.COLOR_MAGENTA, -1)
    curses.init_pair(blue, curses.COLOR_BLUE, -1)
    green = curses.color_pair(green)
    yellow = curses.color_pair(yellow)
    red = curses.color_pair(red)
    magenta = curses.color_pair(magenta)
    blue = curses.color_pair(blue)

    connection_text_box = DynamicTextBox(stdscr, "Not Connected")
    ping_text_box = DynamicTextBox(stdscr, "N/A")
    sent_text_box = DynamicTextBox(stdscr, "N/A")

    timestamp_value_box = DynamicTextBox(stdscr, "N/A")
    power_text_box = DynamicTextBox(stdscr, "N/A")
    recv_text_box = DynamicTextBox(stdscr, "N/A")

    valve_name_text_boxes = [DynamicTextBox(stdscr, f"S{i} ({i + 1})") for i in range(6)]
    valve_state_text_boxes = [DynamicTextBox(stdscr) for _ in range(6)]

    motor_name_text_boxes = [DynamicTextBox(stdscr, f"M{i} ({i + 7})") for i in range(2)]
    motor_state_text_boxes = [DynamicTextBox(stdscr) for _ in range(2)]

    log_file_text_box = DynamicTextBox(stdscr)

    pressure_name_text_boxes = [DynamicTextBox(stdscr, f"P{i} (kPa)") for i in range(4)]
    pressure_value_text_boxes = [DynamicTextBox(stdscr) for _ in range(4)]

    yaw_name_text_box = DynamicTextBox(stdscr, "Yaw (deg)")
    yaw_value_text_box = DynamicTextBox(stdscr)
    yaw_bar_text_box = DynamicTextBox(stdscr)

    pitch_name_text_box = DynamicTextBox(stdscr, "Pitch (deg)")
    pitch_value_text_box = DynamicTextBox(stdscr)
    pitch_bar_text_box = DynamicTextBox(stdscr)

    roll_name_text_box = DynamicTextBox(stdscr, "Roll (deg)")
    roll_value_text_box = DynamicTextBox(stdscr)
    roll_bar_text_box = DynamicTextBox(stdscr)

    while True:
        comm.update()

        for message in comm.messages:
            if message.type == 0:
                new_ss = ss_names._make(struct.unpack(ss_format, message.data))
                ss = {
                    "timestamp": new_ss.timestamp,
                    "init": new_ss.init,
                    "driver": new_ss.driver,
                    "pressure": [new_ss.p0, new_ss.p1, new_ss.p2, new_ss.p3],
                    "ypr": [new_ss.yaw, new_ss.pitch, new_ss.roll],
                    "power": new_ss.power}
                refresh = True

                if logging:
                    log_data.append(ss)
        comm.messages.clear()
    
        if not comm.connected():
            ss = None

        if refresh or rate.ready():
            row = 0
            col_start = 20
            spacer = 9
            bar_space = spacer * 4
            stdscr.addstr(row, 0, "Connection Status:", magenta)
            if ss:
                connection_text_box.set_text("Connected")
                connection_text_box.put(0, col_start, pair=green)
            else:
                connection_text_box.set_text("Not Connected")
                connection_text_box.put(0, col_start, pair=red)
            
            stdscr.addstr(row, col_start + spacer * 2, "Ping:", magenta)
            if ss:
                ping_text_box.set_text(f"{(comm.ping() * 1000):.3f} ms")
                ping_text_box.put(row, col_start + spacer * 3, pair=blue)
            else:
                ping_text_box.set_text("N/A")
                ping_text_box.put(row, col_start + spacer * 3, pair=red)
            
            stdscr.addstr(row, col_start + spacer * 5, "Sent:", magenta)
            sent_text_box.set_text(str(comm.bytes_transfered()))
            sent_text_box.put(row, col_start + spacer * 6, blue)

            row += 2
            stdscr.addstr(row, 0, "Timestamp:", magenta)
            if ss:
                timestamp_value_box.set_text(f"{ss['timestamp']} µs")
                timestamp_value_box.put(row, col_start, blue)
            else:
                timestamp_value_box.set_text("N/A")
                timestamp_value_box.put(row, col_start, red)
            
            stdscr.addstr(row, col_start + spacer * 2, "Power:", magenta)
            if ss:
                power_text_box.set_text(f"{ss['power']:.3f} W")
                power_text_box.put(row, col_start + spacer * 3, pair=blue)
            else:
                power_text_box.set_text("N/A")
                power_text_box.put(row, col_start + spacer * 3, pair=red)
            
            stdscr.addstr(row, col_start + spacer * 5, "Recv:", magenta)
            recv_text_box.set_text(str(comm.bytes_received()))
            recv_text_box.put(row, col_start + spacer * 6, blue)

            row += 2
            stdscr.addstr(row, 0, "Solenoid Valves:", magenta)
            for (i, textbox) in enumerate(valve_name_text_boxes):
                textbox.put(row, col_start + i * spacer, pair=yellow)
            row += 1
            for (i, textbox) in enumerate(valve_state_text_boxes):
                if ss:
                    if is_set(ss["driver"], i):
                        textbox.set_text("OPEN")
                        textbox.put(row, col_start + i * spacer, green)
                    else:
                        textbox.set_text("CLOSED")
                        textbox.put(row, col_start + i * spacer, red)
                        
                else:
                    textbox.set_text("N/A")
                    textbox.put(row, col_start + i * spacer, red)

            row += 2
            stdscr.addstr(row, 0, "Motors:", magenta)
            for (i, textbox) in enumerate(motor_name_text_boxes):
                textbox.put(row, col_start + i * spacer, pair=yellow)
            row += 1
            for (i, textbox) in enumerate(motor_state_text_boxes):
                if ss:
                    if is_set(ss["driver"], i + 6):
                        textbox.set_text("ON")
                        textbox.put(row, col_start + i * spacer, green)
                    else:
                        textbox.set_text("OFF")
                        textbox.put(row, col_start + i * spacer, red)
                else:
                    textbox.set_text("N/A")
                    textbox.put(row, col_start + i * spacer, red)
            
            row -= 1
            stdscr.addstr(row, col_start + spacer * 2, "Log (l):", magenta)
            if logging:
                log_file_text_box.text = f"In Progress ({time.perf_counter() - log_start:.3f})"
                log_file_text_box.put(row, col_start + spacer * 3, green)
            else:
                log_file_text_box.text = "Not Logging"
                log_file_text_box.put(row, col_start + spacer * 3, red)
            row += 1
            
            row += 2
            stdscr.addstr(row, 0, "Pressures:", magenta)
            for (i, textbox) in enumerate(pressure_name_text_boxes):
                textbox.put(row, col_start + i * spacer * 2, pair=yellow)
            row += 1
            for (i, textbox) in enumerate(pressure_value_text_boxes):
                if ss:
                    textbox.set_text(f"{ss['pressure'][i]:.3f}")
                    textbox.put(row, col_start + i * spacer * 2, blue)
                else:
                    textbox.set_text("N/A")
                    textbox.put(row, col_start + i * spacer * 2, red)
            
            row += 2
            stdscr.addstr(row, 0, "IMU:", magenta)
            yaw_name_text_box.put(row, col_start, yellow)
            row += 1
            if ss:
                yaw_value_text_box.set_text(f"{ss['ypr'][0]:.3f}")
                yaw_value_text_box.put(row, col_start, blue)
                tics = bar_space * (math.fmod(ss["ypr"][0] + 180, 360) - 180) / 360
                yaw_bar_text_box.set_text(f"-180 [{' ' * round(bar_space / 2 + tics)}|{' ' * round(bar_space / 2 - tics)}] 180")
                yaw_bar_text_box.put(row, col_start + spacer * 2, blue)
            else:
                yaw_value_text_box.set_text("N/A")
                yaw_value_text_box.put(row, col_start, red)
                yaw_bar_text_box.set_text(f"-180 [{' ' * (bar_space + 1)}] 180")
                yaw_bar_text_box.put(row, col_start + spacer * 2, red)

            row += 2
            pitch_name_text_box.put(row, col_start, yellow)
            row += 1
            if ss:
                pitch_value_text_box.set_text(f"{ss['ypr'][1]:.3f}")
                pitch_value_text_box.put(row, col_start, blue)
                tics = bar_space * (math.fmod(ss["ypr"][1] + 90, 180) - 90) / 180
                pitch_bar_text_box.set_text(f" -90 [{' ' * round(bar_space / 2 + tics)}|{' ' * round(bar_space / 2 - tics)}]  90")
                pitch_bar_text_box.put(row, col_start + spacer * 2, blue)
            else:
                pitch_value_text_box.set_text("N/A")
                pitch_value_text_box.put(row, col_start, red)
                pitch_bar_text_box.set_text(f" -90 [{' ' * (bar_space + 1)}]  90")
                pitch_bar_text_box.put(row, col_start + spacer * 2, red)

            row += 2
            roll_name_text_box.put(row, col_start, yellow)
            row += 1
            if ss:
                roll_value_text_box.set_text(f"{ss['ypr'][2]:.3f}")
                roll_value_text_box.put(row, col_start, blue)
                tics = bar_space * (math.fmod(ss["ypr"][2] + 180, 360) - 180) / 360
                roll_bar_text_box.set_text(f"-180 [{' ' * round(bar_space / 2 + tics)}|{' ' * round(bar_space / 2 - tics)}] 180")
                roll_bar_text_box.put(row, col_start + spacer * 2, blue)
            else:
                roll_value_text_box.set_text("N/A")
                roll_value_text_box.put(row, col_start, red)
                roll_bar_text_box.set_text(f"-180 [{' ' * (bar_space + 1)}] 180")
                roll_bar_text_box.put(row, col_start + spacer * 2, red)
            
            stdscr.addstr(os.get_terminal_size().lines - 1, 0, "")
            stdscr.refresh()
            refresh = False

logo = """


  /$$$$$$             /$$$$$$    /$$                               /$$                        
 /$$__  $$           /$$__  $$  | $$                              | $$                        
| $$  \__/  /$$$$$$ | $$  \__/ /$$$$$$   /$$  /$$  /$$  /$$$$$$  /$$$$$$    /$$$$$$   /$$$$$$ 
|  $$$$$$  /$$__  $$| $$$$    |_  $$_/  | $$ | $$ | $$ |____  $$|_  $$_/   /$$__  $$ /$$__  $$
 \____  $$| $$  \ $$| $$_/      | $$    | $$ | $$ | $$  /$$$$$$$  | $$    | $$$$$$$$| $$  \__/
 /$$  \ $$| $$  | $$| $$        | $$ /$$| $$ | $$ | $$ /$$__  $$  | $$ /$$| $$_____/| $$      
|  $$$$$$/|  $$$$$$/| $$        |  $$$$/|  $$$$$/$$$$/|  $$$$$$$  |  $$$$/|  $$$$$$$| $$      
 \______/  \______/ |__/         \___/   \_____/\___/  \_______/   \___/   \_______/|__/      

 
 """
  
if __name__ == '__main__':
    print(f"{Fore.MAGENTA}{logo}")
    while True:
        try:
            comm = connect()
            curses.wrapper(main, comm)
        except KeyboardInterrupt:
            print(Style.RESET_ALL)
            exit()
        # except Exception as e:
        #     if str(e) == "addwstr() returned ERR":
        #         print(f"{Fore.RED}Error: Screen dimensions are too small!")
        #     print(Style.RESET_ALL)
        #     exit()

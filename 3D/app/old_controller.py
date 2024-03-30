from usbcom import USBMessageBroker
from collections import namedtuple
import serial.tools.list_ports
import struct
import csv
from rate import Rate
from pynput import keyboard
from rich.console import Console
import time
import curses
import os
import math

console = Console()

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

class Controller:
    stageData: dict = {}
    lightsData: dict = {}
    driverData: dict = {}

    _usb: USBMessageBroker
    _logFile: str = ""
    _logData: list = []

    _sendRate = Rate(25)
    _on = False

    logging_on = False

    def __init__(self, usb) -> None:
        self._usb = usb

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
        console.print(f"Saved log file to {os.path.abspath(self._logFile)}", style="green", end="")
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

def connect():
    while True:    
        while True:
            console.print("Select Port:", style="green")
            ports = serial.tools.list_ports.comports()
            for (i, port) in enumerate(ports):
                console.print(f"{i}: {port.device}", style="yellow")
            if len(ports) == 0:
                console.print(f"No USB devices found", style="red")
                time.sleep(2)
                console.print("")
                continue
            console.print("")
            
            console.print(f"Selection: ", style="green", end="")
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
            console.print(f"Baud Rate (default: 2000000): ", style="green", end="")
            try:
                baudrate = input()
            except EOFError:
                continue
            
            try:
                if baudrate == "":
                    baudrate = 2000000
                else:
                    baudrate = int(baudrate)
                if baudrate < 1:
                    continue
                break
            except:
                continue
        
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
        self.text = str(text)
    
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

selectedStage = 0

def main(stdscr, usb):
    global selectedStage
    
    controller = Controller(usb)

    # controller.beginLog("./log.csv")

    keys = {}

    def key_press_cb(event):
        if hasattr(event, 'char'):
            key = event.char
        else:
            key = event.name
        keys[key] = True
    
    def key_release_cb(event):
        global selectedStage

        if hasattr(event, 'char'):
            key = event.char
        else:
            key = event.name
        keys[key] = False

        if key == 'w' and selectedStage + 1 in controller.stageData.keys():
            selectedStage += 1
        elif key == 's' and selectedStage - 1 in controller.stageData.keys():
            selectedStage -= 1

    listener = keyboard.Listener(
        on_press=key_press_cb,
        on_release=key_release_cb)
    listener.start()

    refresh = Rate(30)
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

    stage_name = DynamicTextBox(stdscr, "Stage:")
    timestamp_name = DynamicTextBox(stdscr, "Timestamp:")
    p0_name = DynamicTextBox(stdscr, "p0:")
    p1_name = DynamicTextBox(stdscr, "p1:")
    p2_name = DynamicTextBox(stdscr, "p2:")
    p3_name = DynamicTextBox(stdscr, "p3:")
    pitch_name = DynamicTextBox(stdscr, "Pitch (deg):")
    roll_name = DynamicTextBox(stdscr, "Roll (deg):")
    yaw_name = DynamicTextBox(stdscr, "Yaw (deg):")
    driver_name = DynamicTextBox(stdscr, "Drivers:")

    stageInfo = [{
            'selected': DynamicTextBox(stdscr, ">"),
            'timestamp_value': DynamicTextBox(stdscr),
            'p0_value': DynamicTextBox(stdscr),
            'p1_value': DynamicTextBox(stdscr),
            'p2_value': DynamicTextBox(stdscr),
            'p3_value': DynamicTextBox(stdscr),
            'yaw_value': DynamicTextBox(stdscr),
            'yaw_bar': DynamicTextBox(stdscr),
            'pitch_value': DynamicTextBox(stdscr),
            'pitch_bar': DynamicTextBox(stdscr),
            'roll_value': DynamicTextBox(stdscr),
            'roll_bar': DynamicTextBox(stdscr),
            'drivers': [DynamicTextBox(stdscr, "|") for _ in range(8)]
        } for _ in range(8)
    ]

    # m0: out
    # m1: in
    # s0: a-in
    # s1: a-out
    # s2: c-out
    # s3: b-out
    # s4: c-in
    # s5: b-in
    
    try:
        while True:
            if 'o' in keys and keys['o']:
                break

            if 'l' in keys and keys['l']:
                if controller.logging_on is False:
                    controller.beginLog("./log.csv")

            if 'q' in keys and keys['q']:
                for stage in controller.lightsData.keys():
                    controller.lightsData[stage] = [[255, 95, 5] for _ in range(4)]
            else:
                for stage in controller.lightsData.keys():
                    controller.lightsData[stage] = [[0, 0, 0] for _ in range(4)]
                if selectedStage in controller.lightsData.keys():
                    if controller.logging_on is True:
                        controller.lightsData[selectedStage] = [[0, 0, 255] for _ in range(4)]
                    else:
                        controller.lightsData[selectedStage] = [[0, 255, 0] for _ in range(4)]

            if 'a' in keys and keys['a']: # depressurize
                for stage in controller.lightsData.keys():
                    controller.driverData[stage].modify([False, True, True, True, False, False, True, False])
            elif 'd' in keys and keys['d']: # pressurize
                for stage in controller.lightsData.keys():
                    controller.driverData[stage].modify([True, False, False, False, True, True, False, True])
            else:
                for stage in controller.driverData.keys():
                    controller.driverData[stage] = SetDriver(stage)
                if selectedStage in controller.driverData.keys():
                    if 'x' in keys and keys['x']: # pressurize
                        if 'up' in keys and keys['up']:
                            controller.driverData[selectedStage].modifyBit(BIT_M1, True)
                            controller.driverData[selectedStage].modifyBit(BIT_S0, True)
                        if 'left' in keys and keys['left']:
                            controller.driverData[selectedStage].modifyBit(BIT_M1, True)
                            controller.driverData[selectedStage].modifyBit(BIT_S5, True)
                        if 'right' in keys and keys['right']:
                            controller.driverData[selectedStage].modifyBit(BIT_M1, True)
                            controller.driverData[selectedStage].modifyBit(BIT_S4, True)
                    if 'z' in keys and keys['z']: # depressurize
                        if 'up' in keys and keys['up']:
                            controller.driverData[selectedStage].modifyBit(BIT_M0, True)
                            controller.driverData[selectedStage].modifyBit(BIT_S1, True)
                        if 'left' in keys and keys['left']:
                            controller.driverData[selectedStage].modifyBit(BIT_M0, True)
                            controller.driverData[selectedStage].modifyBit(BIT_S3, True)
                        if 'right' in keys and keys['right']:
                            controller.driverData[selectedStage].modifyBit(BIT_M0, True)
                            controller.driverData[selectedStage].modifyBit(BIT_S2, True)

            controller.update()

            if refresh.ready():
                row = 0
                sspacer = 9
                lspacer = 13
                bar_space = 11
                col = 0
                stdscr.addstr(row, col, "Connection Status:", magenta)
                col += 20
                if usb.connected():
                    connection_text_box.set_text("Connected")
                    connection_text_box.put(row, col, pair=green)
                else:
                    connection_text_box.set_text("Not Connected")
                    connection_text_box.put(row, col, pair=red)
                row += 2
                
                col = 0
                stage_name.put(row, col, green)
                col += sspacer
                timestamp_name.put(row, col, green)
                col += lspacer
                p0_name.put(row, col, green)
                col += sspacer
                p1_name.put(row, col, green)
                col += sspacer
                p2_name.put(row, col, green)
                col += sspacer
                p3_name.put(row, col, green)
                col += sspacer
                pitch_name.put(row, col, green)
                col += sspacer + bar_space + lspacer
                roll_name.put(row, col, green)
                col += sspacer + bar_space + lspacer
                yaw_name.put(row, col, green)
                col += sspacer + bar_space + lspacer
                driver_name.put(row, col, green)
                row += 1

                for (i, info) in enumerate(stageInfo):
                    col = 0
                    if i == selectedStage:
                        info['selected'].set_text(">")
                    else:
                        info['selected'].set_text("")
                    info['selected'].put(row, col, magenta)
                        #stdscr.addstr(row, col, ">", magenta)
                    stdscr.addstr(row, col + 1, f"{i}", blue)
                    col += sspacer
                    if i in controller.stageData.keys():
                        sd = controller.stageData[i]
                        info['timestamp_value'].set_text(sd['timestamp'])
                        info['timestamp_value'].put(row, col, yellow)
                        col += lspacer
                        info['p0_value'].set_text("{:.3f}".format(sd['p0']))
                        info['p0_value'].put(row, col, yellow)
                        col += sspacer
                        info['p1_value'].set_text("{:.3f}".format(sd['p1']))
                        info['p1_value'].put(row, col, yellow)
                        col += sspacer
                        info['p2_value'].set_text("{:.3f}".format(sd['p2']))
                        info['p2_value'].put(row, col, yellow)
                        col += sspacer
                        info['p3_value'].set_text("{:.3f}".format(sd['p3']))
                        info['p3_value'].put(row, col, yellow)
                        col += sspacer
                        info['pitch_value'].set_text("{:.3f}".format(sd['pitch']))
                        info['pitch_value'].put(row, col, yellow)
                        col += sspacer
                        tics = bar_space * (math.fmod(sd['pitch'] + 90, 180) - 90) / 180
                        info['pitch_bar'].set_text(f" -90 [{' ' * round(bar_space / 2 + tics)}|{' ' * round(bar_space / 2 - tics)}]  90")
                        info['pitch_bar'].put(row, col, blue)
                        col += bar_space + lspacer
                        info['roll_value'].set_text("{:.3f}".format(sd['roll']))
                        info['roll_value'].put(row, col, yellow)
                        col += sspacer
                        tics = bar_space * (math.fmod(sd['roll'] + 180, 360) - 180) / 360
                        info['roll_bar'].set_text(f"-180 [{' ' * round(bar_space / 2 + tics)}|{' ' * round(bar_space / 2 - tics)}] 180")
                        info['roll_bar'].put(row, col, blue)
                        col += bar_space + lspacer
                        info['yaw_value'].set_text("{:.3f}".format(sd['yaw']))
                        info['yaw_value'].put(row, col, yellow)
                        col += sspacer
                        tics = bar_space * (math.fmod(sd['yaw'] + 180, 360) - 180) / 360
                        info['yaw_bar'].set_text(f"-180 [{' ' * round(bar_space / 2 + tics)}|{' ' * round(bar_space / 2 - tics)}] 180")
                        info['yaw_bar'].put(row, col, blue)
                        col += bar_space + lspacer
                        
                        for i in range(8):
                            if sd.driver(i):
                                info['drivers'][i].put(row, col, green)
                            else:
                                info['drivers'][i].put(row, col, red)
                            col += 1

                    row += 1

                stdscr.addstr(os.get_terminal_size().lines - 1, 0, "")
                stdscr.refresh()
    except KeyboardInterrupt:
        pass
    
    controller.endLog()

if __name__ == "__main__":
    console.print(logo, style="magenta")
    curses.wrapper(main, connect())
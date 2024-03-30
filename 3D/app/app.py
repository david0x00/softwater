from rate import Rate
from xbox import XboxController
from robot import *
from controller import *

from pynput import keyboard
import curses
import os
import math
import numpy as np

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

class App:    
    _selectedStage = 0
    _keys = {}
    _xcon = XboxController()

    _refresh = Rate(30)
    
    sspacer = 9
    lspacer = 13
    bar_space = 11

    def __init__(self, stdscr, usb, console):
        self._scr = stdscr
        self._usb = usb
        self._console = console
        self._controller = Controller(usb, console)

        self._listener = keyboard.Listener(
            on_press=self._key_press_cb,
            on_release=self._key_release_cb)
        self._listener.start()

        curses.curs_set(0)
        curses.use_default_colors()

        curses.init_pair(1, curses.COLOR_GREEN, -1)
        self._green = curses.color_pair(1)

        curses.init_pair(2, curses.COLOR_YELLOW, -1)
        self._yellow = curses.color_pair(2)

        curses.init_pair(3, curses.COLOR_RED, -1)
        self._red = curses.color_pair(3)

        curses.init_pair(4, curses.COLOR_MAGENTA, -1)
        self._magenta = curses.color_pair(4)

        curses.init_pair(5, curses.COLOR_BLUE, -1)
        self._blue = curses.color_pair(5)

        self._connection_text_box = DynamicTextBox(stdscr, "Not Connected")

        self._stage_name = DynamicTextBox(stdscr, "Stage:")
        self._timestamp_name = DynamicTextBox(stdscr, "Timestamp:")
        self._p0_name = DynamicTextBox(stdscr, "p0:")
        self._p1_name = DynamicTextBox(stdscr, "p1:")
        self._p2_name = DynamicTextBox(stdscr, "p2:")
        self._p3_name = DynamicTextBox(stdscr, "p3:")
        self._pitch_name = DynamicTextBox(stdscr, "Pitch (deg):")
        self._roll_name = DynamicTextBox(stdscr, "Roll (deg):")
        self._yaw_name = DynamicTextBox(stdscr, "Yaw (deg):")
        self._driver_name = DynamicTextBox(stdscr, "Drivers:")

        self._stageInfo = [{
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
            } for _ in range(8)]
    
        self._con_stage_name = DynamicTextBox(stdscr, "Stage:")
        self._con_a_name = DynamicTextBox(stdscr, "a:")
        self._con_b_name = DynamicTextBox(stdscr, "b:")
        self._con_c_name = DynamicTextBox(stdscr, "c:")
        self._conInfo = [{
            'a_value': DynamicTextBox(stdscr),
            'b_value': DynamicTextBox(stdscr),
            'c_value': DynamicTextBox(stdscr),
            'y_value': DynamicTextBox(stdscr),
            'p_value': DynamicTextBox(stdscr),
            'r_value':  DynamicTextBox(stdscr)
        } for _ in range(8)]

    def _key_press_cb(self, event):
        if hasattr(event, 'char'):
            key = event.char
        else:
            key = event.name
        self._keys[key] = True
    
    def _key_release_cb(self, event):
        if hasattr(event, 'char'):
            key = event.char
        else:
            key = event.name
        self._keys[key] = False

        if key == 'w' and self._selectedStage + 1 in self._controller.stageData.keys():
            self._selectedStage += 1
        elif key == 's' and self._selectedStage - 1 in self._controller.stageData.keys():
            self._selectedStage -= 1
    
    def _keyDown(self, key):
        return key in self._keys and self._keys[key]
    
    def run(self):
            stageControllers = [StageController() for _ in range(8)]
            cupdate = Rate(30)
            csend = Rate(3)
            multiMode = False

            try:
                while True:
                    isNew, value = self._xcon.Y()
                    if isNew and value:
                        multiMode = not multiMode
                    
                    _, value = self._xcon.Start()
                    if self._keyDown('q') or value:
                        for stage in self._controller.lightsData.keys():
                            self._controller.lightsData[stage] = [[255, 95, 5] for _ in range(4)]
                    else:
                        if multiMode:
                            for stage in self._controller.lightsData.keys():
                                self._controller.lightsData[stage] = [[0, 255, 0] for _ in range(4)]
                        else:
                            for stage in self._controller.lightsData.keys():
                                self._controller.lightsData[stage] = [[0, 0, 0] for _ in range(4)]
                            if self._selectedStage in self._controller.lightsData.keys():
                                self._controller.lightsData[self._selectedStage] = [[0, 255, 0] for _ in range(4)]

                    isNew, value = self._xcon.DPadUp()
                    if isNew and value and self._selectedStage + 1 in self._controller.stageData.keys():
                        self._selectedStage += 1

                    isNew, value = self._xcon.DPadDown()
                    if isNew and value and self._selectedStage - 1 in self._controller.stageData.keys():
                        self._selectedStage -= 1
                    
                    _, value = self._xcon.X()
                    if value:
                        for i in range(8):
                            if i in self._controller.stageData.keys():
                                sd = self._controller.stageData[i]
                                nsd = None
                                if i + 1 in self._controller.stageData.keys():
                                    nsd = self._controller.stageData[i + 1]
                                    stageControllers[i].calibrateIMU(sd, nsd)

                    _, lvalue = self._xcon.LeftBumper()
                    _, rvalue = self._xcon.RightBumper()
                    if self._keyDown('a') or lvalue:
                        for stage in self._controller.lightsData.keys():
                            self._controller.driverData[stage].modify([False, True, True, True, False, False, True, False])
                    elif self._keyDown('d') or rvalue:
                        for stage in self._controller.lightsData.keys():
                            self._controller.driverData[stage].modify([True, False, False, False, True, True, False, True])
                    else:
                        _, a = self._xcon.A()
                        _, b = self._xcon.B()
                        
                        if a:
                            _, lt = self._xcon.LeftTrigger()
                            _, rt = self._xcon.RightTrigger()
                            _, ljx = self._xcon.LeftJoystickX()
                            _, ljy = self._xcon.LeftJoystickY()
                            
                            dp = 0
                            if lt > 0:
                                dp += -lt
                            if rt > 0:
                                dp += rt

                            aVec = np.array([0, -1])
                            bVec = np.array([1 / math.sqrt(2), 1 / math.sqrt(2)])
                            cVec = np.array([-1 / math.sqrt(2), 1 / math.sqrt(2)])
                            jVec = np.array([ljx, ljy])

                            aVal = jVec.dot(aVec.T)
                            bVal = jVec.dot(bVec.T)
                            cVal = jVec.dot(cVec.T)

                            if cupdate.ready():
                                # stageControllers[self._selectedStage].setATarget((dp + aVal) * cupdate.get_inverse_rate(), True)
                                # stageControllers[self._selectedStage].setBTarget((dp + bVal) * cupdate.get_inverse_rate(), True)
                                # stageControllers[self._selectedStage].setCTarget((dp + cVal) * cupdate.get_inverse_rate(), True)

                                for i in range(8):
                                    if multiMode or self._selectedStage == i:
                                        stageControllers[i].setATarget((dp + aVal) * cupdate.get_inverse_rate() * 2, True)
                                        stageControllers[i].setBTarget((dp + bVal) * cupdate.get_inverse_rate() * 2, True)
                                        stageControllers[i].setCTarget((dp + cVal) * cupdate.get_inverse_rate() * 2, True)

                            if csend.ready():
                                for i in range(8):
                                    if i in self._controller.stageData.keys():
                                        sd = self._controller.stageData[i]
                                        nsd = None
                                        if i + 1 in self._controller.stageData.keys():
                                            nsd = self._controller.stageData[i + 1]
                                        if multiMode or self._selectedStage == i:
                                            self._controller.driverData[i] = stageControllers[i].update(sd, nsd)
                        elif b:
                            _, ljx = self._xcon.LeftJoystickX()
                            _, ljy = self._xcon.LeftJoystickY()

                            for i in range(8):
                                if i in self._controller.stageData.keys():
                                    sd = self._controller.stageData[i]
                                    nsd = None
                                    if i + 1 in self._controller.stageData.keys():
                                        nsd = self._controller.stageData[i + 1]
                                    elif multiMode or self._selectedStage == i:
                                        stageControllers[i].setPitchTarget(ljy * 80)
                                        stageControllers[i].setRollTarget(ljx * 80)
                                    if multiMode or self._selectedStage == i:
                                        self._controller.driverData[i] = stageControllers[i].update(sd, nsd, True)
                        else:
                            for stage in self._controller.driverData.keys():
                                self._controller.driverData[stage] = SetDriver(stage)
                        
                            if self._selectedStage in self._controller.driverData.keys():
                                if self._keyDown('x'):
                                    if self._keyDown('up'):
                                        self._controller.driverData[self._selectedStage].modifyBit(BIT_M1, True)
                                        self._controller.driverData[self._selectedStage].modifyBit(BIT_S0, True)
                                    if self._keyDown('left'):
                                        self._controller.driverData[self._selectedStage].modifyBit(BIT_M1, True)
                                        self._controller.driverData[self._selectedStage].modifyBit(BIT_S5, True)
                                    if self._keyDown('right'):
                                        self._controller.driverData[self._selectedStage].modifyBit(BIT_M1, True)
                                        self._controller.driverData[self._selectedStage].modifyBit(BIT_S4, True)
                                elif self._keyDown('z'):
                                    if self._keyDown('up'):
                                        self._controller.driverData[self._selectedStage].modifyBit(BIT_M0, True)
                                        self._controller.driverData[self._selectedStage].modifyBit(BIT_S1, True)
                                    if self._keyDown('left'):
                                        self._controller.driverData[self._selectedStage].modifyBit(BIT_M0, True)
                                        self._controller.driverData[self._selectedStage].modifyBit(BIT_S3, True)
                                    if self._keyDown('right'):
                                        self._controller.driverData[self._selectedStage].modifyBit(BIT_M0, True)
                                        self._controller.driverData[self._selectedStage].modifyBit(BIT_S2, True)

                    self._controller.update()

                    if self._refresh.ready():
                        row = 0
                        col = 0
                        self._scr.addstr(row, col, "Connection Status:", self._magenta)
                        col += 20
                        if self._usb.connected():
                            self._connection_text_box.set_text("Connected")
                            self._connection_text_box.put(row, col, pair=self._green)
                        else:
                            self._connection_text_box.set_text("Not Connected")
                            self._connection_text_box.put(row, col, pair=self._red)
                        row += 2
                        
                        col = 0
                        self._stage_name.put(row, col, self._green)
                        col += self.sspacer
                        self._timestamp_name.put(row, col, self._green)
                        col += self.lspacer
                        self._p0_name.put(row, col, self._green)
                        col += self.sspacer
                        self._p1_name.put(row, col, self._green)
                        col += self.sspacer
                        self._p2_name.put(row, col, self._green)
                        col += self.sspacer
                        self._p3_name.put(row, col, self._green)
                        col += self.sspacer
                        self._pitch_name.put(row, col, self._green)
                        col += self.sspacer + self.bar_space + self.lspacer
                        self._roll_name.put(row, col, self._green)
                        col += self.sspacer + self.bar_space + self.lspacer
                        self._yaw_name.put(row, col, self._green)
                        col += self.sspacer + self.bar_space + self.lspacer
                        self._driver_name.put(row, col, self._green)
                        row += 1

                        for (i, info) in enumerate(self._stageInfo):
                            col = 0
                            if i == self._selectedStage:
                                info['selected'].set_text(">")
                            else:
                                info['selected'].set_text("")
                            info['selected'].put(row, col, self._magenta)
                            self._scr.addstr(row, col + 1, f"{i}", self._blue)
                            col += self.sspacer
                            if i in self._controller.stageData.keys():
                                sd = self._controller.stageData[i]
                                info['timestamp_value'].set_text(sd['timestamp'])
                                info['timestamp_value'].put(row, col, self._yellow)
                                col += self.lspacer
                                info['p0_value'].set_text("{:.3f}".format(sd['p0']))
                                info['p0_value'].put(row, col, self._yellow)
                                col += self.sspacer
                                info['p1_value'].set_text("{:.3f}".format(sd['p1']))
                                info['p1_value'].put(row, col, self._yellow)
                                col += self.sspacer
                                info['p2_value'].set_text("{:.3f}".format(sd['p2']))
                                info['p2_value'].put(row, col, self._yellow)
                                col += self.sspacer
                                info['p3_value'].set_text("{:.3f}".format(sd['p3']))
                                info['p3_value'].put(row, col, self._yellow)
                                col += self.sspacer
                                info['pitch_value'].set_text("{:.3f}".format(sd['pitch']))
                                info['pitch_value'].put(row, col, self._yellow)
                                col += self.sspacer
                                tics = self.bar_space * (math.fmod(sd['pitch'] + 90, 180) - 90) / 180
                                info['pitch_bar'].set_text(f" -90 [{' ' * round(self.bar_space / 2 + tics)}|{' ' * round(self.bar_space / 2 - tics)}]  90")
                                info['pitch_bar'].put(row, col, self._blue)
                                col += self.bar_space + self.lspacer
                                info['roll_value'].set_text("{:.3f}".format(sd['roll']))
                                info['roll_value'].put(row, col, self._yellow)
                                col += self.sspacer
                                tics = self.bar_space * (math.fmod(sd['roll'] + 180, 360) - 180) / 360
                                info['roll_bar'].set_text(f"-180 [{' ' * round(self.bar_space / 2 + tics)}|{' ' * round(self.bar_space / 2 - tics)}] 180")
                                info['roll_bar'].put(row, col, self._blue)
                                col += self.bar_space + self.lspacer
                                info['yaw_value'].set_text("{:.3f}".format(sd['yaw']))
                                info['yaw_value'].put(row, col, self._yellow)
                                col += self.sspacer
                                tics = self.bar_space * (math.fmod(sd['yaw'] + 180, 360) - 180) / 360
                                info['yaw_bar'].set_text(f"-180 [{' ' * round(self.bar_space / 2 + tics)}|{' ' * round(self.bar_space / 2 - tics)}] 180")
                                info['yaw_bar'].put(row, col, self._blue)
                                col += self.bar_space + self.lspacer
                                
                                for i in range(8):
                                    if sd.driver(i):
                                        info['drivers'][i].put(row, col, self._green)
                                    else:
                                        info['drivers'][i].put(row, col, self._red)
                                    col += 1

                            row += 1
                    
                        row += 2
                        col = 0
                        self._con_stage_name.put(row, col, self._green)
                        col += self.sspacer
                        self._con_a_name.put(row, col, self._green)
                        col += self.sspacer
                        self._con_b_name.put(row, col, self._green)
                        col += self.sspacer
                        self._con_c_name.put(row, col, self._green)
                        row += 1
                        for (i, controller) in enumerate(stageControllers):
                            col = 0
                            self._scr.addstr(row, col, f"{i}", self._blue)
                            col += self.sspacer
                            targets = controller.getPressureTargets()
                            y, p, r = controller.getYPR()
                            
                            self._conInfo[i]['a_value'].set_text("{:.3f}".format(targets[0]))
                            self._conInfo[i]['a_value'].put(row, col, self._yellow)
                            col += self.sspacer

                            self._conInfo[i]['b_value'].set_text("{:.3f}".format(targets[1]))
                            self._conInfo[i]['b_value'].put(row, col, self._yellow)
                            col += self.sspacer

                            self._conInfo[i]['c_value'].set_text("{:.3f}".format(targets[2]))
                            self._conInfo[i]['b_value'].put(row, col, self._yellow)
                            col += self.sspacer

                            self._conInfo[i]['y_value'].set_text("{:.3f}".format(y))
                            self._conInfo[i]['y_value'].put(row, col, self._yellow)
                            col += self.sspacer

                            self._conInfo[i]['p_value'].set_text("{:.3f}".format(p))
                            self._conInfo[i]['p_value'].put(row, col, self._yellow)
                            col += self.sspacer

                            self._conInfo[i]['r_value'].set_text("{:.3f}".format(r))
                            self._conInfo[i]['r_value'].put(row, col, self._yellow)
                            col += self.sspacer


                            row += 1

                        self._scr.addstr(os.get_terminal_size().lines - 1, 0, "")
                        self._scr.refresh()
            except KeyboardInterrupt:
                pass
            
            self._controller.endLog()
    
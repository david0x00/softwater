from inputs import get_gamepad
import math
import time
import threading

class XboxController:
    MAX_TRIG_VAL = math.pow(2, 8)
    MAX_JOY_VAL = math.pow(2, 15)
    _state = {}

    def __init__(self, deadZone=0.1):
        for key in [
            'LJX', 'LJB', 'LJY',
            'RJX', 'RJY', 'RJB',
            'LT', 'RT',
            'LB', 'RB',
            'A', 'X', 'Y', 'B',
            'Start', 'Back',
            'DL', 'DR', 'DU', 'DD']:
            self._state[key] = {'value': 0, 'new': False}

        self._deadZone = deadZone
        self._last = 0
        self._monitor_thread = threading.Thread(target=self._monitor_controller, args=())
        self._monitor_thread.daemon = True
        self._monitor_thread.start()
    
    def connected(self):
        return time.time() - self._last < 1
    
    def LeftJoystickX(self):
        return self._get('LJX')
    
    def LeftJoystickButton(self):
        return self._get('LJB')

    def LeftJoystickY(self):
        return self._get('LJY')
    
    def RightJoystickX(self):
        return self._get('RJX')
    
    def RightJoystickButton(self):
        return self._get('RJB')

    def RightJoystickY(self):
        return self._get('RJY')

    def LeftTrigger(self):
        return self._get('LT')
    
    def RightTrigger(self):
        return self._get('RT')

    def LeftBumper(self):
        return self._get('LB')
    
    def RightBumper(self):
        return self._get('RB')
    
    def A(self):
        return self._get('A')
    
    def X(self):
        return self._get('X')
    
    def Y(self):
        return self._get('Y')
    
    def B(self):
        return self._get('B')
    
    def Start(self):
        return self._get('Start')
    
    def Back(self):
        return self._get('Back')
    
    def DPadLeft(self):
        return self._get('DL')
    
    def DPadRight(self):
        return self._get('DR')
    
    def DPadUp(self):
        return self._get('DU')
    
    def DPadDown(self):
        return self._get('DD')

    def _get(self, key):
        isNew = self._state[key]['new']
        self._state[key]['new'] = False
        return isNew, self._state[key]['value']

    def _set(self, key, value):
        self._state[key]['value'] = value
        self._state[key]['new'] = True
    
    def _clamp(self, val, max):
        val /= max
        if abs(val) < self._deadZone:
            return 0
        
        if val > 0:
            val -= self._deadZone
        else:
            val += self._deadZone
        return val / (1 - self._deadZone)

    def _monitor_controller(self):
        while True:
            events = get_gamepad()
            for event in events:
                self._last = time.time()
                if event.code == 'ABS_Y':
                    self._set('LJY', self._clamp(event.state, self.MAX_JOY_VAL))
                elif event.code == 'ABS_X':
                    self._set('LJX', self._clamp(event.state, self.MAX_JOY_VAL))
                elif event.code == 'ABS_RY':
                    self._set('RJY', self._clamp(event.state, self.MAX_JOY_VAL))
                elif event.code == 'ABS_RX':
                    self._set('RJX', self._clamp(event.state, self.MAX_JOY_VAL))
                elif event.code == 'ABS_Z':
                    self._set('LT', self._clamp(event.state, self.MAX_TRIG_VAL))
                elif event.code == 'ABS_RZ':
                    self._set('RT', self._clamp(event.state, self.MAX_TRIG_VAL))
                elif event.code == 'BTN_TL':
                    self._set('LB', event.state)
                elif event.code == 'BTN_TR':
                    self._set('RB', event.state)
                elif event.code == 'BTN_SOUTH':
                    self._set('A', event.state)
                elif event.code == 'BTN_NORTH':
                    self._set('Y', event.state)
                elif event.code == 'BTN_WEST':
                    self._set('X', event.state)
                elif event.code == 'BTN_EAST':
                    self._set('B', event.state)
                elif event.code == 'BTN_THUMBL':
                    self._set('LJB', event.state)
                elif event.code == 'BTN_THUMBR':
                    self._set('RJB', event.state)
                elif event.code == 'BTN_SELECT':
                    self._set('Back', event.state)
                elif event.code == 'BTN_START':
                    self._set('Start', event.state)
                elif event.code == 'ABS_HAT0Y':
                    if event.state == -1:
                        self._set('DU', 1)
                        self._set('DD', 0)
                    elif event.state == 1:
                        self._set('DU', 0)
                        self._set('DD', 1)
                    else:
                        self._set('DU', 0)
                        self._set('DD', 0)
                elif event.code == 'ABS_HAT0X':
                    if event.state == -1:
                        self._set('DL', 1)
                        self._set('DR', 0)
                    elif event.state == 1:  
                        self._set('DL', 0)
                        self._set('DR', 1)
                    else:
                        self._set('DL', 0)
                        self._set('DR', 0)

if __name__ == '__main__':
    con = XboxController()
    while True:
        print(con.LeftJoystickX())
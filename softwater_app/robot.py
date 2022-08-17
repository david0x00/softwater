from datalink import DataLink
from rate import Rate
from camera import Camera
from hardware import WaterRobot
import time

send_rate = Rate(10)

if __name__ == "__main__":
    camera = Camera()
    camera.start()
    link = DataLink("SoftWaterRobot", True)
    robot = WaterRobot(4, 8)

    try:
        while True:
            if send_rate.ready():
                robot.read_sensors()
                img = None
                while img is None:
                    img = camera.get()
                link.send({'data': {'keyframe': (time.perf_counter(), img, robot.values)}})
            
            if link.data_available():
                msg = link.get()['data']
                print(msg)
                if 'command' in msg.keys():
                    cmd = msg['command']
                    if 'running' in cmd.keys():
                        robot.set_pump(cmd['running'])
                        #robot.set_gate_valve(cmd['running'])
                    elif 'pump' in cmd.keys():
                        robot.set_pump(cmd['pump'])
                    elif 'gate' in cmd.keys():
                        robot.set_gate_valve(cmd['gate'])
                    elif 'cam setting' in cmd.keys():
                        setting, value = cmd['cam setting']
                        camera.set(setting, value)
                    elif 'pressurize' in cmd.keys():
                        id, pressed = cmd['pressurize']
                        robot.set_solenoid(id * 2, pressed)
                        if pressed:
                            robot.set_solenoid((id * 2) + 1, False)
                    elif 'depressurize' in cmd.keys():
                        id, pressed = cmd['depressurize']
                        robot.set_solenoid((id * 2) + 1, pressed)
                        if pressed:
                            robot.set_solenoid((id * 2), False)
                    elif 'set solenoids' in cmd.keys():
                        values = cmd['set solenoids']
                        any_on = False
                        for i in range(8):
                            if values[i]:
                                any_on = True
                            robot.set_solenoid(i, values[i])
                        robot.set_gate_valve(any_on)

            link.update()
    except KeyboardInterrupt:
        pass    
    robot.stop()
    camera.stop()

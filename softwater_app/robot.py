from datalink import DataLink
from rate import Rate
from camera import Camera
from hardware import WaterRobot
import time



if __name__ == "__main__":
    camera = Camera()
    camera.start()
    link = DataLink("SoftWaterRobot", True)
    main_rate = Rate(100)    
    robot = WaterRobot(4, 8)

    while True:
        if link.data_available():
            msg = link.get()['data']
            if 'command' in msg.keys():
                cmd = msg['command']
                if 'running' in cmd.keys():
                    if not cmd['running']:
                        break
                if 'get keyframe' in cmd.keys():
                    start = time.time()
                    #robot.read_sensors()
                    sens = (time.time() - start) * 1000
                    img = None
                    while img is None:
                        img = camera.get()
                    get_img = (time.time() - start) * 1000 - sens
                    msg = {'keyframe': (img, robot.values)}
                    link.send(msg)
                    total = (time.time() - start) * 1000
                    print(sens, get_img, total)

        link.update()
        #main_rate.sleep()
    
    link.send({'status': 'stopped'})
    
    robot.stop()
    camera.stop()

from datalink import DataLink
from rate import Rate
from camera import Camera
from hardware import WaterRobot



if __name__ == "__main__":
    import time
    '''cam = Camera()
    cam.start()
    link = DataLink("SoftWaterRobot", True)
    r = Rate(100)
    img_send_rate = Rate(20)

    while True:
        #ret, img = cap.read()
        if img_send_rate.ready():
            img = cam.get()
            if img is not None:
                msg = {"image": img}
                link.send(msg)
                link.update()
        r.sleep()'''
    
    robot = WaterRobot(4, 8)

    robot.set_pump(True)
    time.sleep(5)
    robot.set_pump(False)

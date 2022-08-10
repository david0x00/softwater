from datalink import DataLink
import threading
import queue
from rate import Rate
from camera import Camera



if __name__ == "__main__":
    cam = Camera()
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
        r.sleep()

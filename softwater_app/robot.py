import cv2
from datalink import DataLink


if __name__ == "__main__":
    cap = cv2.VideoCapture(1)
    link = DataLink("SoftWaterRobot", True)

    while True:
        ret, img = cap.read()
        msg = {"image": img}
        link.send(msg)
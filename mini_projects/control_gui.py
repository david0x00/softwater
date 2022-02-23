import tkinter as tk
from tkinter import *
from turtle import update
from PIL import ImageTk, Image
import cv2

"""Controls GUI to Get End Effector Target Location

Requires:
start, stop, and reset functions
updateTarget functions
update rate in seconds
opencv camera feed object
"""
class ControlGUI(tk.Tk):
    def __init__(self, start, stop, reset, updateTarget, cameraFeed=cv2.VideoCapture(0), updateRate=1000):
        super().__init__()
        self.start = start
        self.stop = stop
        self.reset = reset
        self.updateRate = updateRate
        self.cameraFeed = cameraFeed
        self.updateTarget = updateTarget
        self.cameraViewSize = (int(1920/2), int(1080/2))

    def updateRobotImage(self):
        global im
        im = self.getImages()
        self.testbedDisplay.itemconfig(self.image_on_canvas, image=im)
        #self.testbedDisplay.delete('all')
        #self.testbedDisplay.create_image(0, 0, anchor='nw', image=self.getImage())
        self.testbedDisplay.after(self.updateRate, self.updateRobotImage)
        print("updating image")
        self.testbedDisplay.update()

    def getImages(self):
        ret, cv_img = self.cameraFeed.read()
        resized_down = cv2.resize(cv_img, self.cameraViewSize, interpolation=cv2.INTER_LINEAR)
        b,g,r = cv2.split(resized_down)
        img = cv2.merge((r,g,b))
        cv2.imwrite("delete.png", img)
        print("got image")
        photo = ImageTk.PhotoImage(Image.fromarray(img))
        #photo.write("bruh.gif", format="gif")
        return photo

    def open(self):
        self.resizable(False, False)
        # Needs to scale back to original pixel coordinates
        def setTarget(event):
            target = (event.x * 2, event.y * 2)
            self.updateTarget(target)

        self.title('Control Target Selector')
        self.testbedDisplay = Canvas(self, width=self.cameraViewSize[0], height=self.cameraViewSize[1])
        im = self.getImages()
        print(type(im))
        self.image_on_canvas = self.testbedDisplay.create_image(0, 0, anchor='nw', image=im)
        print("bruh wtf")
        #self.testbedDisplay.after(self.updateRate * 5, self.updateRobotImage)
        self.testbedDisplay.bind('<Button-1>', setTarget)

        startButton = Button(self, text="Start", command=self.start, padx=10, pady=10)
        stopButton = Button(self, text="Stop", command=self.stop, padx=10, pady=10)
        resetButton = Button(self, text="Reset", command=self.reset, padx=10, pady=10)
        updateImages = Button(self, text="Capture", command=self.updateRobotImage, padx=10, pady=10)

        self.testbedDisplay.grid(row=0,column=1)
        startButton.grid(row=1,column=0)
        stopButton.grid(row=1,column=1)
        resetButton.grid(row=1,column=2)
        updateImages.grid(row=2,column=0)

        self.mainloop()

    def __del__(self):
        self.cameraFeed.release()

if __name__ == "__main__":
    def start():
        print("Start")
    def stop():
        print("Stop")
    def reset():
        print("Reset")
    def updateTarget(target):
        print(target[0], ",", target[1])
    cameraCap = cv2.VideoCapture(0)
    print(cameraCap.isOpened())
    gui = ControlGUI(start, stop, reset, updateTarget, cameraFeed=cameraCap)
    gui.open()
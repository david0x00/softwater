import tkinter as tk
from tkinter import *
from PIL import ImageTk, Image
import cv2

"""Controls GUI to Get End Effector Target Location

Requires:
start, stop, and reset functions
updateTarget functions
update rate in milli seconds
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

    # Updates canvas with new image from the camera
    def updateRobotImage(self):
        global im # Global so that when passed to the canvas, it doesn't get deleted by garbage collector
        im = self.getImages()
        self.robotViewer.itemconfig(self.image_on_canvas, image=im)
        #self.robotViewer.delete('all')
        #self.robotViewer.create_image(0, 0, anchor='nw', image=self.getImage())
        #self.robotViewer.after(self.updateRate, self.updateRobotImage)
        #print("Updating Robot Image")
        self.robotViewer.update() # TODO: Test if this line is needed

    # Returns tkinter PhotoImage from the camera feed resized to fit canvas
    def getImages(self):
        ret, cv_img = self.cameraFeed.read()
        resized_down = cv2.resize(cv_img, self.cameraViewSize, interpolation=cv2.INTER_LINEAR)
        b,g,r = cv2.split(resized_down) # Apparently the cv2 object has a different coloring order than tk's images
        img = cv2.merge((r,g,b))
        photo = ImageTk.PhotoImage(Image.fromarray(img))
        return photo

    def open(self):
        self.title('Control Target Selector')
        self.resizable(False, False)

        # Robot View Canvas
        self.robotViewer = Canvas(self, width=self.cameraViewSize[0], height=self.cameraViewSize[1])
        im = self.getImages()
        self.image_on_canvas = self.robotViewer.create_image(0, 0, anchor='nw', image=im)
        self.circleRadius = 2 # Pixels
        x = int(self.cameraViewSize[0] / 2)
        y = int(self.cameraViewSize[1] * .9)
        self.targetMarker = self.robotViewer.create_oval(x-self.circleRadius, y-self.circleRadius, x+self.circleRadius, y+self.circleRadius, width=5, outline="red", fill="red")

        # Needs to be scaled back to original pixel coordinates
        def setTarget(event):
            x = event.x
            y = event.y
            self.robotViewer.coords(self.targetMarker, x-self.circleRadius, y-self.circleRadius, x+self.circleRadius, y+self.circleRadius)
            self.updateRobotImage()
            target = (x * 2, y * 2) # 1080p from half resolution scaling
            self.updateTarget(target)
        self.robotViewer.bind('<Button-1>', setTarget)

        startButton = Button(self, text="Start", command=self.start, padx=10, pady=10)
        stopButton = Button(self, text="Stop", command=self.stop, padx=10, pady=10)
        resetButton = Button(self, text="Reset", command=self.reset, padx=10, pady=10)
        updateImages = Button(self, text="Capture", command=self.updateRobotImage, padx=10, pady=10)
        
        #self.robotViewer.after(self.updateRate * 5, self.updateRobotImage)

        self.robotViewer.grid(row=0,column=1)
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
    #print(cameraCap.isOpened())
    gui = ControlGUI(start, stop, reset, updateTarget, cameraFeed=cameraCap)
    gui.open()
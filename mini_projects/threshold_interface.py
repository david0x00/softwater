from fileinput import filename
import tkinter as tk
from tkinter import IntVar, ttk
from PIL import ImageTk, Image
import cv2
import numpy as np

# color_threshold = (np.array([43, 61, 145]), np.array([255, 255, 255]))
# lower = color_threshold[0]
# upper = None# same
def get_red_mask(image, blur, lower, upper):
    hsv_img = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    blur_img = cv2.GaussianBlur(hsv_img, blur, 0) # (3,3) blur
    red_mask = cv2.inRange(blur_img, lower, upper)
    red_mask = cv2.erode(red_mask, None, iterations=3)
    red_mask = cv2.dilate(red_mask, None, iterations=3)
    return red_mask

# root window
root = tk.Tk()
root.geometry('1280x720')
# root.resizable(False, False)
root.title('HSL Sliders')
maxHue, lowHue = 360, 0
maxSL, lowSL = 100, 0

sliderFrame = tk.Frame()
hueLower = IntVar()
satLower = IntVar()
lumLower = IntVar()
hueHigher = IntVar()
satHigher = IntVar()
lumHigher = IntVar()
def change(event):
    labelHueLower.config(text = "Hue Lower Bound: " + str(hueLower.get()))
    labelSatLower.config(text = "Sat Lower Bound: " + str(satLower.get()))
    labelLumLower.config(text = "Lum Lower Bound: " + str(lumLower.get()))
    labelHueHigher.config(text = "Hue Higher Bound: " + str(hueHigher.get()))
    labelSatHigher.config(text = "Sat Higher Bound: " + str(satHigher.get()))
    labelLumHigher.config(text = "Lum Higher Bound: " + str(lumHigher.get()))
    # print(labelHueLower.cget("text"))


sliders = [
    #Hue Lower Bound
    ttk.Scale( 
        master = sliderFrame,
        from_ = lowHue,
        to = maxHue,
        variable= hueLower,
        command = change
    ),
    #Saturation Lower Bound
    ttk.Scale(
        master = sliderFrame, 
        to = maxSL,
        from_ = lowSL,
        variable=satLower,
        command = change
    ),
    #Luminance Lower Bound
    ttk.Scale(
        master = sliderFrame, 
        to = maxSL,
        from_ = lowSL,
        variable = lumLower,
        command = change
    ),
    #Hue Upper Bound
    ttk.Scale(
        master = sliderFrame,
        to = maxHue,
        from_ = lowHue,
        variable = hueHigher,
        command = change
    ),
    #Saturation Upper Bound
    ttk.Scale(
        master = sliderFrame, 
        to = maxSL,
        from_ = lowSL,
        variable = satHigher,
        command = change
    ),
    #Luminance Upper Bound
    ttk.Scale(
        master = sliderFrame, 
        to = maxSL,
        from_ = lowSL,
        variable = lumHigher,
        command = change
    )
]

counter = 0
for i in sliders[0:3]:
    i.grid(
        column = 0,
        row = counter,
        sticky = 'w'
    )
    counter += 1
counter = 0
for i in sliders[3:]:
    i.grid(
        column = 1,
        row = counter,
        sticky = 'w'
    )
    counter += 1

def renderImage(filename = None, cv2Obj = None):
    global image,imageFromFile, red_mask
    if filename:
        image = Image.open(filename)
        image = image.resize((640, 480))
        imageFromFile = ImageTk.PhotoImage(image)

        cv2Image = cv2.imread(filename)
        # red_mask = get_red_mask(cv2Image, (3,3), np.array([hueLower.get(), satLower.get(), lumLower.get()]), np.array([hueHigher.get(), satHigher.get(), lumHigher.get()]))
        red_mask = get_red_mask(cv2Image, (3,3), np.array([43, 61, 145]), np.array([255, 255, 255]))
        red_mask = Image.fromarray(red_mask)
        red_mask = red_mask.resize((640, 480))
        red_mask = ImageTk.PhotoImage(red_mask)

    elif cv2Obj:
        pass
    imagePanel.config(image = imageFromFile)
    imagePanel.image = imageFromFile
    maskPanel.config(image = red_mask)
    maskPanel.image = red_mask
    print("called")
    imagePanel.pack()
    maskPanel.pack()
    imageFrame.pack()

imageFrame = tk.Frame()
# image = Image.open("./ud1.jpg")
# image = image.resize((640,480))
# imageFromFile = ImageTk.PhotoImage(image)
imagePanel = tk.Label(master = imageFrame)
maskPanel = tk.Label(master = imageFrame)
renderImage(filename = "./ud1.jpg")
imagePanel.pack(
    side = tk.LEFT
)
maskPanel.pack(
    side = tk.RIGHT
)
imageFrame.pack()

sliderFrame.pack()
labelFrame = tk.Frame()
labelHueLower = tk.Label(master = labelFrame, text = "Hue Lower Bound: 0.0")
labelHueLower.pack()
labelSatLower = tk.Label(master = labelFrame, text = "Sat Lower Bound: 0.0")
labelSatLower.pack()
labelLumLower = tk.Label(master = labelFrame, text = "Lum Lower Bound: 0.0")
labelLumLower.pack()
labelHueHigher = tk.Label(master = labelFrame, text = "Hue Higher Bound: 0.0")
labelHueHigher.pack()
labelSatHigher = tk.Label(master = labelFrame, text = "Sat Higher Bound: 0.0")
labelSatHigher.pack()
labelLumHigher = tk.Label(master = labelFrame, text = "Lum Higher Bound: 0.0")
labelLumHigher.pack()
labelFrame.pack()

buttonFrame = tk.Frame()
renderButton = tk.Button(buttonFrame, text="Render Image from Robot", command = renderImage)
# renderButton.grid(
#     column=4,
#     row = 4,
#     sticky= 'e'
# )
renderButton.pack()
buttonFrame.pack(
    side = tk.RIGHT
)

root.mainloop()
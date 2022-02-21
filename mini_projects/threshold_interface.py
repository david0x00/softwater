import tkinter as tk
from tkinter import IntVar, ttk
from PIL import ImageTk, Image
from numpy import var


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

imageFrame = tk.Frame()
image = Image.open("./ud2.jpg")
image = image.resize((640,480))
imageFromFile = ImageTk.PhotoImage(image)
imagePanel = tk.Label(master = imageFrame, image=imageFromFile)
imagePanel.pack()
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

def renderImage():
    image = Image.open("./ud1.jpg")
    image = image.resize((640, 480))
    imageFromFile = ImageTk.PhotoImage(image)
    imagePanel.config(image = imageFromFile)
    imagePanel.image = imageFromFile
    print("called")
    imagePanel.pack()
    imageFrame.pack()

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
import tkinter as Tk
import tkinter.font
from functools import partial
import threading
from tkinter import ttk

from PIL import Image, ImageTk
from robot import WaterRobot
import tkinter.ttk

def main():
    '''
    SETTINGS
    '''
    num_sensors = 4
    num_actuators = 8

    a = WaterRobot(15, num_sensors, num_actuators)

    def _begin():
        a.start()

    def _quit():
        print("Exit")
        a.to_exit = True
        a.stop()
        root.quit()
        root.destroy()

    def button_countdown(i, label):
        if i > 0:
            i -= 1
            label.set(i)
            root.after(1000, lambda: button_countdown(i, label))

    def add_button():
        Tk.Label(master=root, text="New Quota").pack()
        Tk.Button(master=root, text='QuotaNew', command=_quit).pack()

    def save_state():
        a.saveState()

    #IMAGE_PATH = 'application\images\my_robot.png'
    IMAGE_PATH = 'my_robot.png'
    WIDTH, HEIGHT = 1280,720

    root = Tk.Tk()
    #style = ttk.Style(root)
    #print(style.theme_names())
    #style.theme_use('clam')
    root.geometry('{}x{}'.format(WIDTH, HEIGHT))
    root.resizable(False, False)
    #root.overrideredirect(1)
    def __callback():
        pass
    root.protocol("WM_DELETE_WINDOW", __callback)

    canvas = Tk.Canvas(root, width=WIDTH, height=HEIGHT)
    canvas.pack()

    img = ImageTk.PhotoImage(Image.open(IMAGE_PATH).resize((WIDTH, HEIGHT), Image.ANTIALIAS))
    lbl = Tk.Label(root, image=img)
    lbl.img = img
    lbl.place(relx=0.5, rely=0.5, anchor='center')

    StartButton = Tk.Button(master=root, text='Start', command=_begin)  # the start button
    StartButton.place(x=1190, y=15)
    QuitButton = Tk.Button(master=root, text='Quit', command=_quit)  # the quit button
    QuitButton.place(x=1235, y=15)
    T = Tk.Label(master=root, text="Number of Sensors: " + str(len(a.pressure_sensors)))
    T.place(x=15, y=15)

    xvals = [100, 200, 100, 200]
    yvals = [100, 100, 200, 200]
    xvala = [300, 600, 300, 600, 900, 1200, 900, 1200]
    yvala = [300, 300, 400, 400, 300, 300, 400, 400]

    for i in range(0, num_sensors):

        Tk.Button(master=root, text='Read Sensor ' + str(i), command=a.pressure_sensors[i].read_sensor).place(x = xvals[i], y = yvals[i], anchor=Tk.CENTER)
        #Tk.Label(master=root, text="").pack()   SPACING

    for j in range(0, num_actuators):



        s = "Pressurizer"
        if (a.actuators[j].get_is_depressurizer() == True):
            s = "Depressurizer"
        Tk.Label(master=root, text=s + " Actuator #" + str(j)).place(x = xvala[j], y = yvala[j]-10, anchor=Tk.CENTER)
        move_up = partial(a.actuators[j].switch, (""))
        Tk.Button(master=root, text="Switch", command=move_up).place(x = xvala[j], y = yvala[j]+10, anchor=Tk.CENTER)
        #Tk.Label(master=root, text="").pack()   SPACING

    for k in range(0, 1):
        pos = [150, 300]
        s = "Two Way Switch"
        Tk.Label(master=root, text=s).pack()
        turn_off = partial(a.two_way_gate.switch, (0))
        turn_a = partial(a.two_way_gate.switch, (1))
        turn_b = partial(a.two_way_gate.switch, (2))
        Tk.Button(master=root, text="OFF", command=turn_off).place(x = pos[0], y = pos[1], anchor=Tk.CENTER)
        Tk.Button(master=root, text="A", command=turn_a).place(x = pos[0], y = pos[1] + 32, anchor=Tk.CENTER)
        Tk.Button(master=root, text="B", command=turn_b).place(x = pos[0], y = pos[1] + 64, anchor=Tk.CENTER)
        #Tk.Label(master=root, text="").pack()   SPACING

    entryb1 = Tk.StringVar(value=a.frequency)
    Tk.Label(root, text="Frequency: ").place(x = 635, y = 15, anchor=Tk.CENTER)
    Tk.Entry(root, textvariable=entryb1).place(x = 635, y = 35, anchor=Tk.CENTER)

    def print_content():
        content = entryb1.get()
        try:
            a.frequency = float(content)
            print("Set Frequency to: " + str(a.frequency))
        except:
            print("ERROR: Frequency input not numeric")

    b1 = Tk.Button(root, text="Set", command=print_content)
    b1.place(x = 635, y = 60, anchor=Tk.CENTER)
    Tk.Button(master=root, text='Save State', command=save_state).place(x = 960, y = 30, anchor=Tk.CENTER)

    vaal = (a.pressure_sensors[0]).get_value()
    counter = 10
    button_label = Tk.StringVar()
    button_label.set(counter)
    Tk.Button(root, textvariable=button_label).pack()
    R = Tk.Label(master=root, textvariable=button_label)
    R.pack(side=Tk.RIGHT)
    button_countdown(counter, button_label)
    Tk.Button(master=root, text='Quota', command=add_button).pack()

    root.mainloop()


if __name__ == "__main__":
    main()

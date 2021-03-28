import tkinter as tk
import tkinter.font
from functools import partial
from tkinter import ttk
import os
import os.path
from os import path
from PIL import Image, ImageTk
from robot import WaterRobot
from tkinter import messagebox
from tkinter.filedialog import asksaveasfile


class Application(tk.Tk):
    num_sensors = 4
    num_actuators = 8
    a = WaterRobot(15, num_sensors, num_actuators)
    update_speed = 100

    def __init__(self):
        super().__init__()

        print("Current working directory: {0}".format(os.getcwd()))
        if (os.path.exists('application/')):
            print("MOVING WORKING DIRECTORY")
            os.chdir('application/')
        print("Current working directory: {0}".format(os.getcwd()))

        WIDTH, HEIGHT = 1280, 720
        self.title("Softwater Robot")
        self.geometry('{}x{}'.format(WIDTH, HEIGHT))
        self.resizable(False, False)
        self.style = ttk.Style(self)
        self.tk.call('source', 'themes/breeze.tcl')
        self.style.theme_use('Breeze')
        self.protocol("WM_DELETE_WINDOW", self._quit)

        canvas = tk.Canvas(self, width=WIDTH, height=HEIGHT)
        canvas.pack()

        # Load Image Background
        IMAGE_PATH = 'my_robot.png'
        img = ImageTk.PhotoImage(Image.open(IMAGE_PATH).resize((WIDTH, HEIGHT), Image.ANTIALIAS))
        image_background = ttk.Label(self, image=img)
        image_background.img = img
        image_background.place(relx=0.5, rely=0.5, anchor='center')
        self.selected_theme = tk.StringVar()
        theme_frame = ttk.LabelFrame(self, text='Themes')
        theme_frame.pack()

        # Start & Stop Buttons
        start_button = ttk.Button(master=self, text='Start', command=self._begin)  # the start button
        start_button.place(x=1164, y=15)
        quit_button = ttk.Button(master=self, text='Stop', command=self.a.stop)  # the quit button
        quit_button.place(x=1164, y=45)

        # Information Displays
        num_sensors_display = ttk.Label(master=self, text="Number of Sensors: " + str(len(self.a.pressure_sensors)))
        num_sensors_display.place(x=15, y=15)
        global sensor_statuses
        sensor_statuses = ttk.Label(master=self, text="Sensors: " + str(self.a.values))
        sensor_statuses.place(x=15, y=30)

        # Read Sensors Buttons
        xvals = [100, 250, 100, 250]
        yvals = [100, 100, 150, 150]
        for i in range(0, self.num_sensors):
            read_button = ttk.Button(master=self, text='Read Sensor ' + str(i),
                                     command=self.a.pressure_sensors[i].read_sensor)
            read_button.place(x=xvals[i], y=yvals[i], anchor=tk.CENTER)

        # Activate Solenoids Buttons
        xvala = [300, 600, 300, 600, 900, 1200, 900, 1200]
        yvala = [300, 300, 400, 400, 300, 300, 400, 400]
        for j in range(0, self.num_actuators):
            button_label = "Pressurizer"
            if (self.a.actuators[j].get_is_depressurizer() == True):
                button_label = "Depressurizer"
            ttk.Label(master=self, text=button_label + " Actuator #" + str(j)).place(x=xvala[j], y=yvala[j] - 10,
                                                                                     anchor=tk.CENTER)
            switch_function = partial(self.a.actuators[j].switch)
            switch_button = ttk.Checkbutton(master=self, text="Switch", command=switch_function)
            switch_button.place(x=xvala[j], y=yvala[j] + 10, anchor=tk.CENTER)

        # Two Gates Buttons
        for k in range(0, 1):
            pos = [150, 300]
            button_label = "Two Gates Switch"
            ttk.Label(master=self, text=button_label).place(x=pos[0], y=pos[1], anchor=tk.CENTER)
            turn_a = partial(self.a.two_way_gate.switch, (0))
            turn_b = partial(self.a.two_way_gate.switch, (1))
            ttk.Checkbutton(master=self, text="Switch Gate A", command=turn_a).place(x=pos[0], y=pos[1] + 32,
                                                                                     anchor=tk.CENTER)
            ttk.Checkbutton(master=self, text="Switch Gate B", command=turn_b).place(x=pos[0], y=pos[1] + 64,
                                                                                     anchor=tk.CENTER)

        # Frequency Settings
        entryb1 = tk.StringVar(value=self.a.frequency)
        ttk.Label(self, text="Frequency: ").place(x=515, y=35, anchor=tk.CENTER)
        tk.Entry(self, textvariable=entryb1).place(x=635, y=35, anchor=tk.CENTER)
        set_frequency = partial(self.print_content, (entryb1))
        b1 = ttk.Button(self, text="Set", command=set_frequency)
        b1.place(x=765, y=35, anchor=tk.CENTER)

        # Save Dataset Functions
        ttk.Button(master=self, text='Save To', command=self.createfile).place(x=960, y=30, anchor=tk.CENTER)
        ttk.Button(master=self, text='Save Current State', command=self.save_state).place(x=960, y=60, anchor=tk.CENTER)

    def button_countdown(self, i, label):
        if i > 0:
            i -= 1
            label.set(i)
            self.after(1000, lambda: self.button_countdown(i, label))

    def add_button(self):
        ttk.Label(master=self, text="New Quota").pack()
        ttk.Button(master=self, text='QuotaNew', command=self._quit).pack()

    def save_state(self):
        self.a.saveState(self.data_filepath)

    def createfile(self):
        files = [('CSV Files', '*.csv')]
        file = asksaveasfile(filetypes=files, defaultextension='*.csv')
        if (file != None and path.exists(file.name)):
            self.a.data_filepath = file.name

    def print_content(self, input):
        content = input.get()
        try:
            if (float(content) > 0):
                self.a.frequency = float(content)
                print("Set Frequency to: " + str(self.a.frequency))
            else:
                tk.messagebox.showwarning(title=None, message="Frequency must be a positive number (greater than 0)")
                print("ERROR: Frequency input out of expected range")

        except:
            tk.messagebox.showwarning(title=None, message="ERROR: Frequency input not numeric")
            print("ERROR: Frequency input not numeric")

    def __callback(self):
        pass

    def _begin(self):
        while (self.a.data_filepath == None or not (path.exists(self.a.data_filepath))):
            self.createfile()
            if (self.a.data_filepath == None or not (path.exists(self.a.data_filepath))):
                tk.messagebox.showwarning(title=None, message="Please declare a dataset file to a valid path", )
        self.a.start()

    def _quit(self):
        if messagebox.askokcancel("Quit", "Are you sure you want to quit?"):
            print("Exit")
            self.a.to_exit = True
            self.a.stop()
            self.quit()
            self.destroy()

    def update_values(self):
        sensor_statuses.configure(text="Sensors" + str(self.a.values))
        self.after(self.update_speed, self.update_values)


if __name__ == "__main__":
    app = Application()
    app.update_values()
    app.mainloop()

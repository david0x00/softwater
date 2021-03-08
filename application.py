import sys


from robot import WaterRobot
import tkinter as Tk
from functools import partial
import csv



def main():


    '''
    SETTINGS
    '''
    num_sensors = 6
    num_actuators = 6

    a = WaterRobot(15, num_sensors, num_actuators)

    def _begin():
        a.start()

    def _quit():
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
        Tk.Label(master=root,text="New Quota").pack()
        Tk.Button(master=root, text='QuotaNew', command=_quit).pack()

    def save_state():
        a.saveState()

    root = Tk.Tk()
    StartButton = Tk.Button(master=root, text='Start', command=_begin)  # the quit button
    StartButton.pack(side=Tk.RIGHT, pady=5)
    QuitButton = Tk.Button(master=root, text='Quit', command=_quit)  # the quit button
    QuitButton.pack(side=Tk.RIGHT)

    T = Tk.Label(master=root, text = "Number of Sensors: "+ str(len(a.pressure_sensors)))
    T.pack()
    for i in range(0,num_sensors):
        Tk.Button(master=root, text='Read Sensor ' + str(i), command=a.pressure_sensors[i].read_sensor).pack()
    Tk.Label(master=root, text="").pack()  # SPACING
    for j in range(0, num_actuators):
        Tk.Label(master=root, text= "Actuator #" + str(j)).pack()
        move_up = partial(a.actuators[j].actuate_solenoid, ("UP"))
        Tk.Button(master=root, text='Move Up', command= move_up).pack()
        move_down = partial(a.actuators[j].actuate_solenoid, ("DOWN"))
        Tk.Button(master=root, text='Move Down', command=move_down).pack()
        Tk.Label(master=root, text="").pack() #SPACING

    vaal = (a.pressure_sensors[0]).get_value()
    counter = 10
    button_label = Tk.StringVar()
    button_label.set(counter)
    Tk.Button(root, textvariable=button_label).pack()

    Tk.Button(master=root, text='Save State', command=save_state).pack(side=Tk.RIGHT)

    R = Tk.Label(master=root, textvariable= button_label)
    R.pack(side=Tk.RIGHT)
    button_countdown(counter, button_label)
    Tk.Button(master=root, text='Quota', command=add_button).pack()
    root.mainloop()



if __name__ == "__main__":
    main()

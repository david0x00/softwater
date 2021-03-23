import sys


from robot import WaterRobot
import tkinter as Tk
from functools import partial
import csv



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
        Tk.Label(master=root,text="New Quota").pack()
        Tk.Button(master=root, text='QuotaNew', command=_quit).pack()

    def save_state():
        a.saveState()


    root = Tk.Tk()
    StartButton = Tk.Button(master=root, text='Start', command=_begin)  # the start button
    StartButton.pack(side=Tk.RIGHT, pady=5)
    QuitButton = Tk.Button(master=root, text='Quit', command=_quit)  # the quit button
    QuitButton.pack(side=Tk.RIGHT)

    T = Tk.Label(master=root, text = "Number of Sensors: "+ str(len(a.pressure_sensors)))
    T.pack()
    for i in range(0,num_sensors):
        Tk.Button(master=root, text='Read Sensor ' + str(i), command=a.pressure_sensors[i].read_sensor).pack()
    Tk.Label(master=root, text="").pack()  # SPACING

    for j in range(0, num_actuators):
        s = "Pressurizer"
        if (a.actuators[j].get_is_depressurizer() == True):
            s = "Depressurizer"
        Tk.Label(master=root, text= s + " Actuator #" + str(j)).pack()
        move_up = partial(a.actuators[j].switch, ("UP"))
        Tk.Button(master=root, text="Switch", command= move_up).pack()
        Tk.Label(master=root, text="").pack() #SPACING

    for k in range(0, 1):
        s = "Two Way Switch"
        Tk.Label(master=root, text= s).pack()
        turn_off = partial(a.two_way_gate.switch, (0))
        turn_a = partial(a.two_way_gate.switch, (1))
        turn_b = partial(a.two_way_gate.switch, (2))
        Tk.Button(master=root, text="OFF", command=turn_off).pack()
        Tk.Button(master=root, text="A", command=turn_a).pack()
        Tk.Button(master=root, text="B", command=turn_b).pack()
        Tk.Label(master=root, text="").pack()  # SPACING

    entryb1 = Tk.StringVar()
    Tk.Label(root, text="Frequency: ").pack()
    Tk.Entry(root, textvariable=entryb1).pack()
    def print_content():
        content = entryb1.get()
        print(content)
    b1 = Tk.Button(root, text="Set", command=print_content)
    b1.pack()



    Tk.Button(master=root, text='Save State', command=save_state).pack(side=Tk.RIGHT)

    vaal = (a.pressure_sensors[0]).get_value()
    counter = 10
    button_label = Tk.StringVar()
    button_label.set(counter)
    Tk.Button(root, textvariable=button_label).pack()
    R = Tk.Label(master=root, textvariable= button_label)
    R.pack(side=Tk.RIGHT)
    button_countdown(counter, button_label)
    Tk.Button(master=root, text='Quota', command=add_button).pack()

    root.mainloop()



if __name__ == "__main__":
    main()

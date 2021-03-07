import sys


from robot import WaterRobot
import tkinter as Tk



def main():
    a = WaterRobot(15, 2, 0)

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
        Tk.Button(master=root, text='QuotaNew', command=_quit).pack()

    root = Tk.Tk()
    StartButton = Tk.Button(master=root, text='Start', command=_begin)  # the quit button
    StartButton.pack(side=Tk.RIGHT, pady=5)
    QuitButton = Tk.Button(master=root, text='Quit', command=_quit)  # the quit button
    QuitButton.pack(side=Tk.RIGHT)
    T = Tk.Label(master=root, text = "Number of Sensors: "+ str(len(a.pressure_sensors)))
    T.pack(side = Tk.TOP)
    for i in range(0,2):
        Tk.Button(master=root, text='Quota', command=add_button).pack()
    vaal = (a.pressure_sensors[0]).get_value()

    counter = 10
    button_label = Tk.StringVar()
    button_label.set(counter)
    Tk.Button(root, textvariable=button_label).pack()

    R = Tk.Label(master=root, textvariable= button_label)
    R.pack(side=Tk.RIGHT)
    button_countdown(counter, button_label)

    root.mainloop()



if __name__ == "__main__":
    main()

from app import app


def pressurize0(pressed):
    print("Pressurize0:", pressed)
    app.robot_state_image_pane.show_pressure(0, 105.2)

def depressurize0(pressed):
    print("Depressurize0:", pressed)
    app.robot_state_image_pane.show_pressure(0, 100.2)

def pressurize1(pressed):
    print("Pressurize1:", pressed)

def depressurize1(pressed):
    print("Depressurize1:", pressed)

def pressurize2(pressed):
    print("Pressurize2:", pressed)

def depressurize2(pressed):
    print("Depressurize2:", pressed)

def pressurize3(pressed):
    print("Pressurize3:", pressed)

def depressurize3(pressed):
    print("Depressurize3:", pressed)

def pressurize4(pressed):
    print("Pressurize4:", pressed)

def depressurize4(pressed):
    print("Depressurize4:", pressed)  

def pressurize5(pressed):
    print("Pressurize5:", pressed)

def depressurize5(pressed):
    print("Depressurize5:", pressed)

def pump(pressed):
    print("Pump:", pressed)

def gate(pressed):
    print("Gate:", pressed)

def sensors(pressed):
    print("Sensors:", pressed)

def camera_view(pressed):
    print("Camera View:", pressed)

def tracker_view(pressed):
    print("Tracker View:", pressed)
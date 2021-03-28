
''' WEEK 1'''
# find an alternate way instead of sleep to "fire the methods or functions at a certain time"
# collect data and get pressure.
# either control the robot or give the robot procedures to execute.
# while the robot moves the data for pressure is being taken.
# TODO: add a function add another function that takes the photos of the robot as it changes position; this way we can see where the position of the robot is .
# TODO: every round we take a photo and save its positions and pressure, and the state of solenoid valves into a csv

# Priority 1: get data at a reliable frequency like 5 HZ. we have a variable Sampling frequency and changes how frequent we snap data
# Priority 2: Build a Soft Robot Class.
# Priority 3: How are we going to get input? allow manual control for robot actuating solenoids for now

'''WEEK 2'''
# In the GUI, Take data from pressure sensors -> actuate each solenoid.
# Setup and finish the Gui. Turn on solenoids, start experiment button, stop, such.

'''WEEK 3'''
# 4 Pressure Sensors, 8 Solenoid Actuators, 4 will pressurize a solenoid and 4 will depressurize. We have solenoid gate valve which is represented with on/off. we also have a water pump
# Write to CSV every sensor read. In the csv we need to write actuator states (Actuator is 1/0, solenoid is 1/0, Pump is 1/0, 1 = open, 0 = closed)

'''WEEK 4'''
# Add a 2 way pump switch
# Add a Gate solenoid valve
# finish the UI photo implementation
# add a text field that allows us to set frequency
# save dataset to a folder. browse
# I will create a start recording button for a set frequency

'''WEEK 5'''
# Communicate with David about
# Fix start bug
# For the switch buttons have a open/close status
# Wrap up code make it pretty;
# Add save to path functions

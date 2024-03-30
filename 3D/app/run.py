from usbcom import USBMessageBroker
from app import App

import serial.tools.list_ports
import time
import curses
from rich.console import Console


logo = """

  /$$$$$$             /$$$$$$    /$$                               /$$                        
 /$$__  $$           /$$__  $$  | $$                              | $$                        
| $$  \__/  /$$$$$$ | $$  \__/ /$$$$$$   /$$  /$$  /$$  /$$$$$$  /$$$$$$    /$$$$$$   /$$$$$$ 
|  $$$$$$  /$$__  $$| $$$$    |_  $$_/  | $$ | $$ | $$ |____  $$|_  $$_/   /$$__  $$ /$$__  $$
 \____  $$| $$  \ $$| $$_/      | $$    | $$ | $$ | $$  /$$$$$$$  | $$    | $$$$$$$$| $$  \__/
 /$$  \ $$| $$  | $$| $$        | $$ /$$| $$ | $$ | $$ /$$__  $$  | $$ /$$| $$_____/| $$      
|  $$$$$$/|  $$$$$$/| $$        |  $$$$/|  $$$$$/$$$$/|  $$$$$$$  |  $$$$/|  $$$$$$$| $$      
 \______/  \______/ |__/         \___/   \_____/\___/  \_______/   \___/   \_______/|__/      

 """

def connect(console):
    while True:    
        while True:
            console.print("Select Port:", style="green")
            ports = serial.tools.list_ports.comports()
            for (i, port) in enumerate(ports):
                console.print(f"{i}: {port.device}", style="yellow")
            if len(ports) == 0:
                console.print(f"No USB devices found", style="red")
                time.sleep(2)
                console.print("")
                continue
            console.print("")
            
            console.print(f"Selection: ", style="green", end="")
            try:
                selection = input()
            except EOFError:
                continue
            
            try:
                selection = int(selection)
                if selection >= len(ports):
                    continue
                break
            except:
                continue
        
        while True:
            console.print(f"Baud Rate (default: 2000000): ", style="green", end="")
            try:
                baudrate = input()
            except EOFError:
                continue
            
            try:
                if baudrate == "":
                    baudrate = 2000000
                else:
                    baudrate = int(baudrate)
                if baudrate < 1:
                    continue
                break
            except:
                continue
        
        return USBMessageBroker(ports[selection].device, baudrate)

def main(stdscr, usb, console):
    app = App(stdscr, usb, console)
    app.run()

if __name__ == '__main__':
    console = Console()
    console.print(logo, style="magenta")
    curses.wrapper(main, connect(console), console)
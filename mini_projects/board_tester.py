import board
import busio

i2c = busio.I2C(board.SCL, board.SDA)

import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn

ads_2 = ADS.ADS1115(i2c, address=0x4b)

from adafruit_mcp230xx.mcp23008 import MCP23008

mcp_2 = MCP23008(i2c, address=0x23)

sensor_pairs = [(ads_2, ADS.P1), (ads_2, ADS.P0)]

chan0 = AnalogIn(sensor_pairs[0][0], sensor_pairs[0][1])
chan1 = AnalogIn(sensor_pairs[1][0], sensor_pairs[1][1])

Va0 = chan0.voltage
Va1 = chan1.voltage

P0 = ((Va0 / 5.0) + 0.040) / 0.004
P1 = ((Va1 / 5.0) + 0.040) / 0.004

print("Pressure 0: " + str(P0))
print("Pressure 1: " + str(P1))

temp_pin
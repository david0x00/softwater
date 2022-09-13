import cv2
import os
import glob
import numpy as np
import math
import pandas as pd
import pickle
import statistics
from matplotlib import cm
from matplotlib import pyplot as plt
from sklearn.metrics import mean_squared_error
import matplotlib.patches as patches
from matplotlib.colors import ListedColormap, LinearSegmentedColormap, Normalize
from PIL import Image
import ast

x = [0.0]
y = [0.0]

df = pd.read_csv("./control_data_-7_29.csv")

row = df.iloc[-1]

for i in range(1,11):
    x.append(row["M" + str(i) + "X"])
    y.append(row["M" + str(i) + "Y"])

plt.plot(x,y, "o", color="red")

plt.xlim((-20,20))
plt.ylim((-5,35))

plt.show()

# x = ["M1-PL", "M1-PR", "M2-PL", "M2-PR"]
# y = []
# for k in x:
#     y.append(row[k])

# plt.bar(x,y)
# plt.ylim((100,115))
# plt.xlabel("Actuator Pressure Reading")
# plt.ylabel("Pressure (kPa)")
# plt.show()
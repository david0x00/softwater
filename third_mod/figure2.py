from matplotlib import cm
from matplotlib import pyplot as plt
from matplotlib.colors import ListedColormap, LinearSegmentedColormap, Normalize
import pandas as pd
import numpy as np
import glob
import math
import seaborn as sns
import os
from scipy.interpolate import interp1d

all_data_dir = "/Users/davidnull/phd/data/3rd_mod_basic_actuator"

time_press = []
time_depress = []

def round_up(n, decimals=0):
    multiplier = 10 ** decimals
    return math.ceil(n * multiplier) / multiplier

def round_down(n, decimals=0):
    multiplier = 10 ** decimals
    return math.floor(n * multiplier) / multiplier

def get_minvalue(inputlist):
    #get the minimum value in the list
    min_value = min(inputlist)
    #return the index of minimum value 
    min_index=inputlist.index(min_value)
    return min_index

all_data = {"pd": [], "theta": [], "dir": []}

for data_dir in glob.glob(all_data_dir + "/*"):
    for filename in glob.glob(data_dir + "/*.csv"):
        df = pd.read_csv(filename)
        mod_pfx = "M1"
        for i in range(2): 
            if i == 0:
                valve = mod_pfx + "-AR-IN"
                direction = "Pressurize"
            else:
                valve = mod_pfx + "-AR-OUT"
                direction = "Depressurize"

            groups = df[df[valve] == True].groupby((df[valve] != True).cumsum()).groups
            on_data_idxs = max(groups.values(), key=len)
            on_data = df.iloc[on_data_idxs]
            if i == 0:
                full_time = on_data["TIME"].iloc[-1] - on_data["TIME"].iloc[0]
                time_press.append(full_time)
            else:
                adjusted_on_data = on_data[(on_data[mod_pfx + "-PR"] - on_data[mod_pfx + "-PL"]) > -0.5]
                # #print(on_data)
                # print(adjusted_on_data["TIME"].iloc[0], adjusted_on_data["TIME"].iloc[0])
                # print(adjusted_on_data)
                full_time = adjusted_on_data["TIME"].iloc[-1] - on_data["TIME"].iloc[0]
                time_depress.append(full_time)

            pd_data = list((on_data[mod_pfx + "-PR"] - on_data[mod_pfx + "-PL"]).to_numpy())
            ratio_data = on_data["M6X"].div(on_data["M6Y"]).abs()
            theta_data = list(np.degrees(np.arctan(ratio_data)).to_numpy())

            interp_func = interp1d(pd_data, theta_data)

            new_pd_data = []

            start = round_up(min(pd_data),1)
            end = round_down(max(pd_data),1)
            x = start
            while x <= end:
                new_pd_data.append(x)
                x += 0.1
                x = round(x, 1)
            new_pd_data = np.array(new_pd_data)

            #new_pd_data = np.arange(math.ceil(min(pd_data)), math.floor(max(pd_data)), 1)

            new_theta_data = interp_func(new_pd_data)

            new_pd_data = list(new_pd_data)
            new_theta_data = list(new_theta_data)
            dir_list = [direction] * len(new_pd_data)
        
            all_data["pd"] += new_pd_data
            all_data["theta"] += new_theta_data
            all_data["dir"] += dir_list

print(time_press)
print(time_depress)
print("Average Pressurization Mod " + str(1) + ": " + str(sum(time_press) / len(time_press)))
print("Average depressurization Mod " + str(1) + ": " + str(sum(time_depress) / len(time_depress)))

all_data_df = pd.DataFrame.from_dict(all_data)
#sns.lineplot(x=pd_data_list[0], y=theta_data_list[0])
ax = sns.lineplot(data=all_data_df, x="pd", y="theta", hue="dir")
ax.set_ylim(-1, 35)
ax.set_xlim(-4, 23)
ax.set_xticks(np.arange(-4, 23, 5.0))
ax.set_yticks(np.arange(-1, 35, 5.0))
ax.set_xticklabels(x, fontsize=20)
plt.savefig("fig2.png")
import pandas as pd
import glob
import math
import matplotlib.pyplot as plt

ampc_dir = "/Users/davidnull/phd/data/Acc40_Ampc_r1/"
vs_dir = "/Users/davidnull/phd/data/Acc40_Visual_Servo_r1/"
X = "XEEX"
Y = "XEEY"

# run_dirs = glob.glob(vs_dir + "/*")
run_dirs = glob.glob(ampc_dir + "/*")

max_diff = 0
diff_list = []

for rd in run_dirs:
    vel_list = []
    run_dir = rd + "/"
    for fname in glob.glob(run_dir + '/*.csv'):
        if "debug_log" not in fname:
            csv_file = fname
            break
    df = pd.read_csv(csv_file)
    for index, row in df.iterrows():
        if index != 0:
            currx = row[X]
            curry = row[Y]
            diff = math.sqrt( (currx - prevx)**2 + (curry - prevy)**2 )
            diff_list.append(diff*10)
            vel_list.append(diff*10*2)
            if diff > max_diff:
                max_diff = diff
        prevx = row[X]
        prevy = row[Y]
    plt.plot(vel_list)
    plt.title(csv_file.split('/')[-2:])
    plt.show()

print(max_diff)
print(sum(diff_list) / len(diff_list))


# plt.hist(diff_list, density=True, bins=30)  # density=False would make counts
# plt.title("Per Timestep Distance Jump Probability (VS)")
# plt.ylabel('Probability')
# plt.xlabel('Distance Jump (mm)')
# plt.show()
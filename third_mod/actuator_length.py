import pandas as pd
import numpy as np
import glob

# 80mm
# training_data_dir = "/Users/davidnull/phd/data/3rd_stage_base_training/"
training_data_dir = "/Users/davidnull/phd/data/LRRL1518/"

def rad(deg):
    return deg * np.pi/180.0


def new_range(x_vals, y_vals, x1, x2, y1, y2):
    x_vals_base = x_vals[0]
    x_vals_end = x_vals[-1]
    y_vals_base = y_vals[0]
    y_vals_end = y_vals[-1]

    x_old_min = min(x_vals_base, x_vals_end)
    x_old_max = max(x_vals_base, x_vals_end)

    y_old_min = min(y_vals_base, y_vals_end)
    y_old_max = max(y_vals_base, y_vals_end)

    x_new_min = min(x1, x2)
    x_new_max = max(x1, x2)

    y_new_min = min(y1, y2)
    y_new_max = max(y1, y2)

    x_old_range = max(x_old_max - x_old_min, 0.2)
    y_old_range = max(y_old_max - y_old_min, 0.2)

    x_new_range = x_new_max - x_new_min
    y_new_range = y_new_max - y_new_min

    # print(x_old_min, x_old_max)
    # print(y_old_min, y_old_max)
    # print(x_new_min, x_new_max)
    # print(y_new_min, y_new_max)

    x_new = []
    y_new = []
    for i in range(len(x_vals)):
        if x_old_range == 0:
            x = x_new_min
        else:
            x = (((x_vals[i] - x_old_min) * x_new_range) / x_old_range) + x_new_min

        if y_old_range == 0:
            y = y_new_min
        else:
            y = (((y_vals[i] - y_old_min) * y_new_range) / y_old_range) + y_new_min

        x_new.append(x)
        y_new.append(y)
    
    length = 0
    for i in range(1, len(x_vals)):
        x1 = x_new[i - 1]
        y1 = y_new[i - 1] 

        x2 = x_new[i]
        y2 = y_new[i] 

        x_diff = x2 - x1
        y_diff = y2 - y1
        # print(x_diff, y_diff)
        length += np.sqrt((x_diff)**2 + (y_diff)**2)
    
    return x_new, y_new, length
        
for data_dir in glob.glob(training_data_dir + "/*"):
    for filename in glob.glob(data_dir + "/*.csv"):
        if "orig" not in filename:
            df = pd.read_csv(filename)

            for i in range(6):
                xml = "M" + str(i+1) + "XL"
                xmr = "M" + str(i+1) + "XR"
                yml = "M" + str(i+1) + "YL"
                ymr = "M" + str(i+1) + "YR"
                df[xml] = ''
                df[xmr] = ''
                df[yml] = ''
                df[ymr] = ''

            df["M1-AL-L"] = ''
            df["M1-AR-L"] = ''


            for index, row in df.iterrows():
                base_angle = row["A1"]
                end_angle = row["A2"] #- base_angle
                x_vals = row[["M1X", "M2X", "M3X", "M4X", "M5X", "M6X"]]
                y_vals = row[["M1Y", "M2Y", "M3Y", "M4Y", "M5Y", "M6Y"]]

                end_left_x = x_vals[-1] - np.cos(rad(end_angle))*4
                end_left_y = y_vals[-1] - np.sin(rad(end_angle))*4

                end_right_x = x_vals[-1] + np.cos(rad(end_angle))*4
                end_right_y = y_vals[-1] + np.sin(rad(end_angle))*4

                base_left_x = x_vals[0] - np.cos(rad(base_angle))*4
                base_left_y = y_vals[0] - np.sin(rad(base_angle))*4

                base_right_x = x_vals[0] + np.cos(rad(base_angle))*4
                base_right_y = y_vals[0] + np.sin(rad(base_angle))*4

                x_left_vals, y_left_vals, left_length = new_range(x_vals, y_vals, end_left_x, base_left_x, end_left_y, base_left_y)
                x_right_vals, y_right_vals, right_length = new_range(x_vals, y_vals, end_right_x, base_right_x, end_right_y, base_right_y)

                # for i in range(len(x_left_vals)):
                #     x1 = x_left_vals[i]
                #     y1 = y_left_vals[i]
                #     x2 = x_right_vals[i]
                #     y2 = y_right_vals[i]
                #     print(np.sqrt((x2-x1)**2 + (y2-y1)**2))

                for i in range(len(x_left_vals)):
                    xml = "M" + str(i+1) + "XL"
                    xmr = "M" + str(i+1) + "XR"
                    yml = "M" + str(i+1) + "YL"
                    ymr = "M" + str(i+1) + "YR"
                    df.loc[index, xml] = x_left_vals[i]
                    df.loc[index, xmr] = x_right_vals[i]
                    df.loc[index, yml] = y_left_vals[i]
                    df.loc[index, ymr] = y_right_vals[i]

                df.loc[index, "M1-AL-L"] = left_length
                df.loc[index, "M1-AR-L"] = right_length

                # quit()

            df.to_csv(data_dir + "/new_data.csv")

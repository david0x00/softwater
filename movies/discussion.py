import pandas as pd

df = pd.read_csv("./end_data_new.csv")

def outperformed():
    best_error = 0
    best_error_ood = 0
    best_timeoutside = 0
    best_timeoutside_ood = 0
    for index, row in df.iterrows():
        ampc_error = row["ampc_dist"]
        other_error = [row["simp_dist"], row["vs_dist"], row["cql_dist"], row["trpo_dist"], ]
        won_err = True
        for err in other_error:
            if err < ampc_error:
                won_err = False
        ampc_time = row["ampc_time_outside_goal"]
        other_time = [row["simp_time_outside_goal"], row["vs_time_outside_goal"], row["cql_time_outside_goal"], row["trpo_time_outside_goal"], ]
        won_time = True
        for time in other_time:
            if time < ampc_time:
                won_time = False

        if won_err:
            if index < 40:
                best_error += 1
            else:
                best_error_ood += 1
        
        if won_time:
            if index < 40:
                best_timeoutside += 1
            else:
                best_timeoutside_ood += 1
                
    print("Task Space: best error - " + str(best_error) + ", best time - " + str(best_timeoutside))
    print("OOD Space: best error - " + str(best_error_ood) + ", best time - " + str(best_timeoutside_ood))
    

def print_stats(prefix):
    print(prefix + " STATS:")
    print("Task Space")
    dist = df[prefix + "_dist"]
    mean = round(dist.mean(), 3)
    std = round(dist.std(), 3)
    print("Dist Err Mean: " + str(mean) + ", STD: " + str(std))
    reached = df[prefix + "_reached"].sum()
    rp = round(100 * reached / 40.0, 0)
    reached_end = df[prefix + "_reached_end"].sum()
    rep = round(100 * reached_end / 40.0, 0)
    print("Reached at all: " + str(reached) + "/40 " + str(rp) + "%, Reached at end: " + str(reached_end) + "/40 " + str(rep) + "%")
    time_outside = df[prefix + "_time_outside_goal"]
    mean = round(time_outside.mean(), 3)
    std = round(time_outside.std(), 3)
    print("Time Outside Goal Mean: " + str(mean) + ", STD: " + str(std))
    print("OOD space")
    dist = df[prefix + "_ood_dist"]
    mean = round(dist.mean(), 3)
    std = round(dist.std(), 3)
    print("Dist Err Mean: " + str(mean) + ", STD: " + str(std))
    reached = df[prefix + "_ood_reached"].sum()
    rp = round(100 * reached / 18.0, 0)
    reached_end = df[prefix + "_ood_reached_end"].sum()
    rep = round(100 * reached_end / 18.0, 0)
    print("Reached at all: " + str(reached) + "/18 " + str(rp) + "%, Reached at end: " + str(reached_end) + "/18 " + str(rep) + "%")
    time_outside = df[prefix + "_ood_time_outside_goal"]
    mean = round(time_outside.mean(), 3)
    std = round(time_outside.std(), 3)
    print("Time Outside Goal Mean: " + str(mean) + ", STD: " + str(std))

    print("\n")

outperformed()
print()
print_stats("simp")
print_stats("vs")
print_stats("cql")
print_stats("trpo")
print_stats("ampc")
# print(df.head())

# for index, row in df.iterrows():
#     print(row['simp_rms'], row['vs_rms'])


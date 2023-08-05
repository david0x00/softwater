import pandas as pd
import glob
import math
import matplotlib.pyplot as plt

end_data_file = "end_data_new.csv"
df = pd.read_csv(end_data_file)

# a = [0] * 10
# ik = [0] * 10
# vs = [0] * 10
# tr = [0] * 10
# cq = [0] * 10

a = [0] * 20
ik = [0] * 20
vs = [0] * 20
tr = [0] * 20
cq = [0] * 20

full_list = []

for index, row in df.iterrows():
    # if index < 40:
    if index >= 40:
        a[int(row["ampc_dist"])] += 1
        ik[int(row["simp_dist"])] += 1
        vs[int(row["vs_dist"])] += 1
        cq[int(row["cql_dist"])] += 1
        tr[int(row["trpo_dist"])] += 1


# tags = ('<1cm', '1-2cm', '2-3cm', '3-4cm', '4-5cm', '5-6cm', '6-7cm', '7-8cm', '8-9cm', '9-10cm')
tags_ood = ('<1cm', '1-2cm', '2-3cm', '3-4cm', '4-5cm', '5-6cm', '6-7cm', '7-8cm', '8-9cm', '9-10cm',
            '10-11cm', '11-12cm', '12-13cm', '13-14cm', '14-15cm', '15-16cm', '16-17cm', '17-18cm', '18-19cm', '19-20cm')
         #'Cromlech (0.925 improved, 7 serv.)', 'Cromlech (15 serv.)', 'Pangaea', 'ServiceCutter (4 serv.)')
# # insert some newlines in the tags to better fit into the plot
# tags = [tag.replace(' (', '\n(') for tag in tags]
# a = (0.385, 0.4128, 0.406, 0.5394, 0.7674, 0.306, 0.3505)
# b = (0.4025, 0.1935, 0.189, 0.189, 0.415, 0.238, 0.1714)
# c = (1, 0.3619, 0.5149, 1, 0.4851, 0.4092, 0.4407)
# d = (1, 0.3495, 0.4888, 1, 0.4861, 0.4985, 0.5213)
# # create a dataframe
# df = pd.DataFrame({"Learned IK": ik, "Visual Servo": vs, "CQL": cq, "TRPO": tr, "AutoMPC": a}, index=tags)
df = pd.DataFrame({"Learned IK": ik, "Visual Servo": vs, "CQL": cq, "TRPO": tr, "AutoMPC": a}, index=tags_ood)
df.plot.bar(rot=0, figsize=(12, 5))
# plt.title("Distribution of Distance Error for Task Space 40 Targets")
plt.title("Distribution of Distance Error for Task Space 18 OOD Targets")
plt.xlabel("Distance Error (cm)")
plt.ylabel("Number of Runs")
plt.tight_layout()  # fit labels etc. nicely into the plot
plt.show()

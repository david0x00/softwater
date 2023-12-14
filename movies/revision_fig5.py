import pandas as pd
import glob
import math
import matplotlib
import matplotlib.pyplot as plt
matplotlib.rcParams['pdf.fonttype'] = 42
matplotlib.rcParams['ps.fonttype'] = 42

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

data_in = [[],[],[],[],[]]
data_out = [[],[],[],[],[]]
for index, row in df.iterrows():
    if index < 40:
        data_in[0].append(row["simp_dist"])
        data_in[1].append(row["vs_dist"])
        data_in[2].append(row["cql_dist"])
        data_in[3].append(row["trpo_dist"])
        data_in[4].append(row["ampc_dist"])
    else:
        data_out[0].append(row["simp_dist"])
        data_out[1].append(row["vs_dist"])
        data_out[2].append(row["cql_dist"])
        data_out[3].append(row["trpo_dist"])
        data_out[4].append(row["ampc_dist"])


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

size=13
fig = plt.figure()
fig.set_size_inches(8, 4)

ax1 = fig.add_subplot(121)
ax2 = fig.add_subplot(122)

# df = pd.DataFrame({"Learned IK": ik, "Visual Servo": vs, "CQL": cq, "TRPO": tr, "AutoMPC": a}, index=tags_ood)
label_list = ["Open Loop IK", "Visual Servo", "CQL", "TRPO", "AutoMPC"]
ax1.boxplot(data_in, patch_artist = True, notch ='True')
ax2.boxplot(data_out, patch_artist = True, notch ='True')
ax1.set_xticklabels(label_list, rotation=30, size=size)
ax2.set_xticklabels(label_list, rotation=30, size=size)
ax1.set_title("Task Space Final Error Distributions", size=size)
ax2.set_title("OOD Final Error Distributions", size=size)
ax1.tick_params(labelsize=size)
ax1.label_outer()
ax2.tick_params(labelsize=size)
ax2.label_outer()
ax1.set_ylim((0,10))
ax2.set_ylim((0,10))
# df.plot.bar(rot=0, figsize=(12, 5))
# plt.title("Distribution of Distance Error for Task Space 40 Targets")
ax1.set_ylabel("Final Distance Error (cm)", size=size)
plt.tight_layout()  # fit labels etc. nicely into the plot
# plt.show()
plt.savefig('TaskBox.pdf', bbox_inches='tight')

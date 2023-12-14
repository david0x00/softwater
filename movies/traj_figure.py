import matplotlib
import matplotlib.pyplot as plt
import matplotlib 
import pandas as pd
import glob
matplotlib.rcParams['pdf.fonttype'] = 42
matplotlib.rcParams['ps.fonttype'] = 42

final_traj_dir = "/Users/davidnull/phd/data/Trajectories/final_trajectories/"

name_id = {
    "ampc": 4,
    "cql": 2,
    "olik": 0,
    "trpo": 3,
    "vs": 1
}

distance_errors = [[],[],[],[],[]]

color_id = {
    ("left", "up"): "blue",
    ("left", "down"): "orange",
    ("right", "up"): "green",
    ("right", "down"): "purple",
}

fig = plt.figure()
fig.set_size_inches(7, 2)

ax_titles = ["Open Loop IK", "Visual Servo", "CQL", "TRPO", "AutoMPC"]
axs = []
for i in range(5):
    axs.append(fig.add_subplot(151 + i))

size=6
for i, ax in enumerate(axs):
    ax.set(adjustable='box', aspect='equal')
    ax.set_ylim((23,31))
    ax.set_xlim((-9,9))
    ax.set_title(ax_titles[i], size=size)
    ax.set_xlabel("x (cm)", size=size)
    ax.set_ylabel("y (cm)", size=size)
    ax.tick_params(labelsize=size)
    ax.label_outer()

def plot_traj(ax_idx, traj_dir, direction, updown, path=False, targ=False, start=False, traj=False):
    ax = axs[ax_idx]
    sx = 0.0
    sy = 24.0
    ty = 29.0
    if direction == "left":
        tx = -7.0
    else:
        tx = 7.0

    csvfile = traj_dir + "/control_data_-9_25.csv"
    df = pd.read_csv(csvfile)
    df = df[df["WAYY"] != sy].reset_index()
    # df = df.where((df["WAYY"] > sy))
    df = df.drop_duplicates(subset=['WAYX', 'WAYY'], keep='first')
    if len(df) != 100:
        print(len(df))
        print(df)
    pathx = df["WAYX"]
    pathy = df["WAYY"]
    eex = df["XEEX"]
    eey = df["XEEY"]

    dist = df["DIST"].tolist()


    if path:
        ax.plot(pathx, pathy, color="black", linestyle="dashed", linewidth='0.6')
    if traj:
        ax.plot(eex, eey, color=color_id[(direction, updown)])
        distance_errors[ax_idx] += dist
    if targ:
        ax.plot(tx, ty, 'x', color="red", linewidth='0.1')
    if start:
        ax.plot(sx, sy, 'x', color="green")

def plot_all_trajs():
    for td in glob.glob(final_traj_dir + "/*"):
        print(td)
        if "mp4" not in td:
            tdl = td.split("/")[-1].split("_")
            ax_idx = name_id[tdl[0]]
            direction = tdl[3]
            updown = tdl[2]
            print(td, ax_idx)
            plot_traj(ax_idx, td, direction, updown, path=True)
            plot_traj(ax_idx, td, direction, updown, targ=True)
            # plot_traj(axs[ax_idx], td, direction, updown, start=True)
            plot_traj(ax_idx, td, direction, updown, traj=True)

plot_all_trajs()

for d in distance_errors:
    print(len(d))
    print(sum(d) / len(d))

# plt.show()


# plt.subplots_adjust(wspace=0, hspace=0)
plt.savefig('TrajFig.pdf', bbox_inches='tight')
    
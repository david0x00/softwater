import autompc as ampc # Version: 0.2
from autompc.sysid import MLP
from autompc.graphs import KstepPredAccGraph
import numpy as np
import pandas as pd
import pickle
from glob import glob
import matplotlib.pyplot as plt
import matplotlib
matplotlib.rcParams['pdf.fonttype'] = 42
matplotlib.rcParams['ps.fonttype'] = 42
import sys
sys.path.insert(0, "../utils")
import utils
sys.path.insert(1, "../experiment_scripts")
import generalization_experiment_01 as experiment
import argparse
import os
import cv2
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
from mpl_toolkits.axes_grid1 import make_axes_locatable

def plot_error_triangles(experiment_names, dists, colorbar=True):
    system = utils.get_system_ver2()
    all_goals = experiment.get_targets()+[[-13,25],[-13,27],[-13,29],[-11,31],[-9,33],[-7,35],[-5,37],[-3,39],[-1,39],[1,39],[3,39],[5,37],[7,35],[9,33],[11,31],[13,29],[13,27],[13,25]]

    def get_rectangle(targ, rms):
        edge_len = 2
        half_edge = edge_len / 2
        x = targ[0] - half_edge
        y = targ[1] - half_edge
        if rms >= 0:
            norm_rms = (rms - min_rms) / (max_rms - min_rms)
            color = viridis(norm_rms)
            return patches.Rectangle((x, y), edge_len, edge_len, color=color, ec=None)
        else:
            rms *= -1
            norm_rms = (rms - min_rms) / (max_rms - min_rms)
            color = viridis(norm_rms)
            return patches.Rectangle((x+0.125, y+0.125), edge_len-0.25, edge_len-0.25, linewidth=0.5, facecolor=color, edgecolor='red')
    
    fig = plt.figure()
    fig.set_size_inches(7, 2)
    for i, experiment_name in enumerate(experiment_names):
        fig.add_subplot(1,len(experiment_names),i+1)
        ax = fig.axes[i]

        levels = 256
        viridis = cm.get_cmap('viridis', levels)
        abs_max_rms = 6.56
        max_rms = 3.5
        min_rms = 0.0
        scaler = abs_max_rms/max_rms
        newcolors = viridis(np.linspace(0, scaler, levels))
        cmap = ListedColormap(newcolors)

        
        ax.set(adjustable='box', aspect='equal')
        ax.set_xlim((-14,14))
        ax.set_ylim((21,41))
        ax.set_title(experiment_name, size=6)
        ax.set_xlabel('x (cm)', size=6)
        if i == 0:
            ax.set_ylabel('y (cm)', size=6)
        
        ax.tick_params(labelsize=6)
        ax.label_outer()
        for targ, dist in dists[i].items():
            targ = ast.literal_eval(targ)
            rect_simp = get_rectangle(targ, dist)
            ax.add_patch(rect_simp)
    #ax.annotate('Task Space', xy=(0.5, 0.24), xycoords='axes fraction', ha='center', va='center', color='w', fontsize=6)
    norm = Normalize(vmin=0, vmax=abs_max_rms, clip=False)
    size=6
    divider = make_axes_locatable(ax)
    cax = divider.append_axes("right", size="5%", pad=0.0)
    cbar = plt.colorbar(cm.ScalarMappable(norm=norm, cmap=cmap), cax=cax)
    cbar.ax.tick_params(labelsize=size)
    cbar.set_label('$x_{ee}$ Position Error (cm)', fontsize=size)
    
    return fig

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--OLIK_path",
        type=str,
        default='/media/dohun/Seagate Backup Plus Drive/dohun autompc/acc40/',
        help="Path to open loop IK controller results"
    )
    parser.add_argument(
        "--VS_path",
        type=str,
        default='/media/dohun/Seagate Backup Plus Drive/dohun autompc/Acc40 Visual_Servo r1/',
        help="Path to visual servo controller results"
    )
    parser.add_argument(
        "--AutoMPC_path",
        type=str,
        default='/media/dohun/Seagate Backup Plus Drive/dohun autompc/09062022/',
        help="Path to AutoMPC controller results"
    )
    parser.add_argument(
        "--viz_result_path",
        type=str,
        default='./',
        help='Path to save the generated figure'
    )
    parser.add_argument(
        "--colorbar",
        type=bool,
        default=False,
        help='True if you want to visualize the color bar. Default: False'
    )
    args = parser.parse_args()

    system = utils.get_system_ver2()
    all_goals = experiment.get_targets()+[[-13,25],[-13,27],[-13,29],[-11,31],[-9,33],[-7,35],[-5,37],[-3,39],[-1,39],[1,39],[3,39],[5,37],[7,35],[9,33],[11,31],[13,29],[13,27],[13,25]]

    fig = plt.figure()
    fig.set_size_inches(7, 2)
    ax1 = fig.add_subplot(141)
    ax2 = fig.add_subplot(142)
    ax3 = fig.add_subplot(143)
    ax4 = fig.add_subplot(144)

    levels = 256
    viridis = cm.get_cmap('viridis', levels)
    abs_max_rms = 6.56
    max_rms = 3.5
    min_rms = 0.0
    scaler = abs_max_rms/max_rms
    newcolors = viridis(np.linspace(0, scaler, levels))
    cmap = ListedColormap(newcolors)

    # comment out to remove color bar
    norm = Normalize(vmin=0, vmax=abs_max_rms, clip=False)
    if colorbar:
        divider = make_axes_locatable(ax4)
        cax = divider.append_axes("right", size="5%", pad=0.0)
        cbar = plt.colorbar(cm.ScalarMappable(norm=norm, cmap=cmap), cax=cax)
        cbar.ax.tick_params(labelsize=size)
        cbar.set_label('$x_{ee}$ Position Error (cm)', fontsize=size)
        
    plt.subplots_adjust(wspace=0, hspace=0)

    def get_rectangle(targ, rms):
        edge_len = 2
        half_edge = edge_len / 2
        x = targ[0] - half_edge
        y = targ[1] - half_edge
        norm_rms = (rms - min_rms) / (max_rms - min_rms)
        color = viridis(norm_rms)
        print(x, y)
        rect = patches.Rectangle((x, y), edge_len, edge_len, color=color, ec=None)
        return rect

    ax1.set(adjustable='box', aspect='equal')
    ax2.set(adjustable='box', aspect='equal')
    ax3.set(adjustable='box', aspect='equal')
    ax4.set(adjustable='box', aspect='equal')
    ax1.set_ylim((21,41))
    ax1.set_xlim((-14,14))
    ax2.set_ylim((21,41))
    ax2.set_xlim((-14,14))
    ax3.set_ylim((21,41))
    ax3.set_xlim((-14,14))
    ax4.set_ylim((21,41))
    ax4.set_xlim((-14,14))

    size=6
    ax1.set_title('Open Loop IK', size=size)
    ax2.set_title('Visual Servo', size=size)
    ax3.set_title('AutoMPC', size=size)
    ax4.set_title('AutoMPC O.O.D', size=size)

    ax1.set_xlabel("X (cm)", size=size)
    ax2.set_xlabel("X (cm)", size=size)
    ax3.set_xlabel("X (cm)", size=size)
    ax4.set_xlabel("X (cm)", size=size)
    ax1.set_ylabel("Y (cm)", size=size)
    ax4.annotate('Task Space', xy=(0.5, 0.24), xycoords='axes fraction', ha='center', va='center', color='w', fontsize=size)
    ax1.tick_params(labelsize=size)
    ax2.tick_params(labelsize=size)
    ax3.tick_params(labelsize=size)
    ax4.tick_params(labelsize=size)
    ax1.label_outer()
    ax2.label_outer()
    ax3.label_outer()
    ax4.label_outer()

    dists = {}
    # OLIK
    for csv in sorted(glob(args.OLIK_path + '*/simple_comb/*/control*.csv')):
        result_path = os.path.dirname(os.path.realpath(csv))
        goal = [int(csv.split('_')[-2]), int(csv.split('_')[-1][:-4])]
        goal_idx = all_goals.index(goal)
        task = experiment.init_task(goal)
        df = pd.read_csv(csv)
        traj = ampc.Trajectory(system, df[system.observations].to_numpy(), df[system.controls].to_numpy())
        final_pos= np.array([df.M10X[len(df)-1], df.M10Y[len(df)-1]])
        dists[str(goal)]= np.sqrt(np.sum((final_pos-np.array(goal))**2))
    for targ, dist in dists.items():
        targ = ast.literal_eval(targ)
        rect_simp = get_rectangle(targ, dist)
        ax1.add_patch(rect_simp)
    dists = {}
    for csv in sorted(glob(args.VS_path + '*/control*.csv')):
        result_path = os.path.dirname(os.path.realpath(csv))
        goal = [int(csv.split('_')[-2]), int(csv.split('_')[-1][:-4])]
        goal_idx = all_goals.index(goal)
        task = experiment.init_task(goal)
        df = pd.read_csv(csv)
        traj = ampc.Trajectory(system, df[system.observations].to_numpy(), df[system.controls].to_numpy())
        final_pos= np.array([df.M10X[len(df)-1], df.M10Y[len(df)-1]])
        dists[str(goal)]= np.sqrt(np.sum((final_pos-np.array(goal))**2))
        print(dists[str(goal)])
    for targ, dist in dists.items():
        targ = ast.literal_eval(targ)
        rect_simp = get_rectangle(targ, dist)
        ax2.add_patch(rect_simp)
    dists = {}
    for csv in sorted(glob(args.AutoMPC_path + '*/*/control*.csv')):
        result_path = os.path.dirname(os.path.realpath(csv))
        goal = [int(csv.split('_')[-2]), int(csv.split('_')[-1][:-4])]
        goal_idx = all_goals.index(goal)
        task = experiment.init_task(goal)
        df = pd.read_csv(csv)
        traj = ampc.Trajectory(system, df[system.observations].to_numpy(), df[system.controls].to_numpy())
        final_pos= np.array([df.M10X[len(df)-1], df.M10Y[len(df)-1]])
        dists[str(goal)]= np.sqrt(np.sum((final_pos-np.array(goal))**2))
    for targ, dist in dists.items():
        targ = ast.literal_eval(targ)
        rect_simp = get_rectangle(targ, dist)
        targ_idx = all_goals.index(targ)
        if targ_idx in list(range(40)):
            ax3.add_patch(rect_simp)
            def get_gray_rectangle(targ, rms):
                edge_len = 2
                half_edge = edge_len / 2
                x = targ[0] - half_edge
                y = targ[1] - half_edge
                norm_rms = (rms - min_rms) / (max_rms - min_rms)
                rect = patches.Rectangle((x, y), edge_len, edge_len, color='gray', ec=None)
                return rect
            ax4.add_patch(get_gray_rectangle(targ, dist))
        else:
            ax4.add_patch(rect_simp)

    # comment out to remove color bar
    norm = Normalize(vmin=0, vmax=abs_max_rms, clip=False)
    if args.colorbar:
        divider = make_axes_locatable(ax4)
        cax = divider.append_axes("right", size="5%", pad=0.0)
        cbar = plt.colorbar(cm.ScalarMappable(norm=norm, cmap=cmap), cax=cax)
        cbar.ax.tick_params(labelsize=size)
        cbar.set_label('$x_{ee}$ Position Error (cm)', fontsize=size)

    # if e == 0:
    #     plt.savefig(directory + "/analysis/" + "/simp_acc40.png")
    # elif e == 1:
    #     plt.savefig(directory + "/analysis/" + "/ampc_acc40.png")
    # elif e == 2:
    #     plt.savefig(directory + "/analysis/" + "/vs_acc40.png")

    plt.subplots_adjust(wspace=0, hspace=0)
    plt.savefig(os.path.join(args.viz_result_path, 'Figure6.pdf'))
    #plt.show()

if __name__ == "__main__":
    main()

import torch
import torch.nn as nn
from torch.distributions import Categorical
from fwd_dynamics import LSTM_DYNAMICS, inverse_scale_data
import statistics
from trpo_min import SOFTROBOTSIM
from matplotlib import cm
from matplotlib.colors import ListedColormap, LinearSegmentedColormap, Normalize
import matplotlib.patches as patches
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np

xc = [[-9,-7,-5,-3,-1,1,3,5,7,9],
          [-9,-7,-5,-3,-1,1,3,5,7,9],
          [-7,-5,-3,-1,1,3,5,7],
          [-5,-3,-1,1,3,5],
          [-3,-1,1,3],
          [-1,1]]
yc = 25
idx_coords = []
for i, row in enumerate(xc):
    for x in row:
        y = yc + i*2
        idx_coords.append([x,y])

env = SOFTROBOTSIM()

agent = torch.load("actor_trpo_5000.pt")
agent.eval()
# count = 0
# for p in agent.parameters():
#     count += p.numel()
# print(count)
def get_agent_action(state, policy=None):
    state = torch.tensor(state).float().unsqueeze(0)  # Turn state into a batch with a single element
    if policy == None:
        dist = Categorical(agent(state))  # Create a distribution from probabilities for actions
    else:
        dist = Categorical(policy(state))  # Create a distribution from probabilities for actions
    return dist.sample().item()

def evaluate(x, y, policy=None):
    env.set_target(x, y)
    state = env.reset()
    done = False
    samples = []
    reward_list = []
    x_ee = []
    y_ee = []
    actions = []
    while not done:
        with torch.no_grad():
            action = get_agent_action(state, policy=policy)

        next_state, reward, done, _ = env.step(action)
        reward_list.append(reward)
        x_ee.append(inverse_scale_data(env.dynamics_output[0][13], x_marker=True))
        y_ee.append(inverse_scale_data(env.dynamics_output[0][23], y_marker=True))
        actions.append(action)
        # Collect samples
        samples.append((state, action, reward, next_state))
        state = next_state
    answer = -1 * float(reward_list[-1])
    sx = -1
    sy = 35
    if x == sx and y == sy:
        fig2, ax2 = plt.subplots()
        ax2.set_ylim((19,41))
        ax2.set_xlim((-11,11))
        rx = [sx - 1, sx + 1, sx + 1, sx - 1, sx - 1]
        ry = [sy - 1, sy - 1, sy + 1, sy + 1, sy - 1]
        ax2.plot(rx, ry, color="red")
        ax2.plot(x_ee, y_ee)
        # plt.plot(actions)
        # plt.plot(reward_list)
        print(inverse_scale_data(env.dynamics_output[0][0:4], pressure=True))
        # print(inverse_scale_data(env.dynamics_output[0][4:14], x_marker=True))
        # print(inverse_scale_data(env.dynamics_output[0][14:24], y_marker=True))
        plt.show()
    print(answer)
    return answer
    



# plt.plot(x_ee, y_ee)
# plt.plot(actions)

# plt.plot(reward_list)
# plt.show()


levels = 256
viridis = cm.get_cmap('viridis', levels)
abs_max_rms = 4.635
max_rms = 3.5
min_rms = 0.0
scaler = abs_max_rms/max_rms
newcolors = viridis(np.linspace(0, scaler, levels))
cmap = ListedColormap(newcolors)

def get_rectangle(targ, rms):
    edge_len = 2
    half_edge = edge_len / 2
    x = targ[0] - half_edge
    y = targ[1] - half_edge
    norm_rms = (rms - min_rms) / (max_rms - min_rms)
    color = viridis(norm_rms)
    rect = patches.Rectangle((x, y), edge_len, edge_len, color=color)
    return rect

fig, ax = plt.subplots()

ax.set_title(r"Evaluate")
ax.set(adjustable='box', aspect='equal')

average = 0
stdev_list = []
for key in idx_coords:
    end_error = evaluate(key[0], key[1])
    rect_simp = get_rectangle(key, end_error)
    ax.add_patch(rect_simp)
    average += end_error
    stdev_list.append(end_error)
average = average / len(idx_coords)
print(average)
stdev = statistics.pstdev(stdev_list)
print(stdev)

ax.set_ylim((19,41))
ax.set_xlim((-11,11))
ax.set_xlabel("X (cm)")
ax.set_ylabel("Y (cm)")
norm = Normalize(vmin=0, vmax=abs_max_rms, clip=False)
cbar = plt.colorbar(cm.ScalarMappable(norm=norm, cmap=cmap), ax=ax)
cbar.set_label('Root MSE (cm)')
plt.show()



# fig, ax = plt.subplots()
# ax.set(adjustable='box', aspect='equal')
# ax.set_ylim((19,41))
# ax.set_xlim((-11,11))
# ax.set_xlabel("X (cm)")
# ax.set_ylabel("Y (cm)")
# norm = Normalize(vmin=0, vmax=abs_max_rms, clip=False)
# cbar = plt.colorbar(cm.ScalarMappable(norm=norm, cmap=cmap), ax=ax)
# cbar.set_label('Distance Error (cm)')

# # define the animation function
# def animate(i):
#     if i >= 51:
#         return
#     multiplier = 100
#     # ax.clear()

#     if i == 0:
#         iteration_num = 0
#     else:
#         iteration_num = i*multiplier - 1
#     policy = torch.load("./policy_iterations/" + str(iteration_num) + ".pt")

#     average = 0
#     stdev_list = []
#     for key in idx_coords:
#         end_error = evaluate(key[0], key[1], policy=policy)
#         rect_simp = get_rectangle(key, end_error)
#         ax.add_patch(rect_simp)
#         average += end_error
#         stdev_list.append(end_error)
#     average = round(average / len(idx_coords),2)
#     print(average)
#     stdev = round(statistics.pstdev(stdev_list),2)
#     print(stdev)
#     ax.set_title("Training It: " + str(multiplier*i) + ", Ave: " + str(average) + ", STDev: " + str(stdev))

    

# # create the animation object
# ani = animation.FuncAnimation(fig, animate, frames=75)
# # plt.show()

# # save the animation as a video file
# ani.save('traiing_animation.gif', writer='ffmpeg')
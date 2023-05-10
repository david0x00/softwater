# https://medium.com/@vladogim97/trpo-minimal-pytorch-implementation-859e46c4232e
# https://gist.github.com/elumixor/c16b7bdc38e90aa30c2825d53790d217
import gym
import numpy as np
import torch
import torch.nn as nn
import matplotlib.pyplot as plt
from torch.optim import Adam
from torch.distributions import Categorical
from collections import namedtuple
import fwd_dynamics
from fwd_dynamics import LSTM_DYNAMICS
import game_sim
import time

SAVE_THIS_MODEL = False

class SOFTROBOTSIM:
    x_targs = [-9, -1, -5, -3, -1, 9, 1, 5, 3, 1]
    y_targs = [25, 25, 27, 31, 35, 25, 25, 27, 31, 35]
    # x_targs = [-1]
    # y_targs = [33]

    def __init__(self):
        self.state_size = 2 + 2 + 4
        #self.action_size = 2
        self.action_size = 256
        self.model = torch.load("lstm_model_1.pt")
        self.model.eval()
        self.targ_idx = 0
        self.new_target()
        self.init_state()
    
    def new_target(self):
        self.targ_idx = (self.targ_idx + 1) % len(self.x_targs)
        targ_x = fwd_dynamics.scale_data(self.x_targs[self.targ_idx], x_marker=True)
        targ_y = fwd_dynamics.scale_data(self.y_targs[self.targ_idx], y_marker=True)
        self.target = torch.FloatTensor([targ_x, targ_y])
    
    def set_target(self, x, y):
        targ_x = fwd_dynamics.scale_data(x, x_marker=True)
        targ_y = fwd_dynamics.scale_data(y, y_marker=True)
        self.target = torch.FloatTensor([targ_x, targ_y])


    def fwd_dynamics_step(self, x):
        with torch.no_grad():
            y_pred = self.model(x)
        return y_pred

    def scale_state(self, state):
        sol = fwd_dynamics.scale_data(state[:8], solenoid=True)
        press = fwd_dynamics.scale_data(state[8:12], pressure=True)
        x_mark = fwd_dynamics.scale_data(state[12:22], x_marker=True)
        y_mark = fwd_dynamics.scale_data(state[22:32], y_marker=True)
        new_state = torch.cat((sol, press, x_mark, y_mark), 0)
        return new_state
    
    def update_rl_state(self):
        x_ee = self.dynamics_output[0][13]
        y_ee = self.dynamics_output[0][23]
        x_mid = self.dynamics_output[0][8]
        y_mid = self.dynamics_output[0][18]
        x_t = self.target[0]
        y_t = self.target[1]
        e_x = x_t - x_ee
        e_y = y_t - y_ee
        # full = self.dynamics_output[0][4:].numpy()
        full = np.array([
            x_ee, y_ee, x_mid, y_mid
        ])
        stuff = np.array([
            x_t, y_t, e_x, e_y
        ])

        x_ee_s = fwd_dynamics.inverse_scale_data(x_ee, x_marker=True)
        y_ee_s = fwd_dynamics.inverse_scale_data(y_ee, y_marker=True)
        x_t_s = fwd_dynamics.inverse_scale_data(x_t, x_marker=True)
        y_t_s = fwd_dynamics.inverse_scale_data(y_t, y_marker=True)
        e_x_s = x_t_s - x_ee_s
        e_y_s = y_t_s - y_ee_s

        self.reward = -1 * np.sqrt((e_x_s*e_x_s) + (e_y_s*e_y_s))
        self.rl_state = np.concatenate((stuff, full), 0)
    
    def init_state(self):
        self.count = 0
        self.dynamics_start_state = torch.FloatTensor([
            0, 0, 0, 0, 0, 0, 0, 0,
            100, 100, 100, 100,
            0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
            2.899, 5.004, 7.090, 9.011, 12.888, 15.695, 17.628, 19.598, 21.641, 24.539
        ])
        scaled_state = self.scale_state(self.dynamics_start_state)
        self.dynamics_input = scaled_state.repeat(4,1)
        self.dynamics_input = self.dynamics_input[None, :, :]
        self.dynamics_output = self.fwd_dynamics_step(self.dynamics_input)

        self.update_rl_state()
 

    def reset(self):
        self.init_state()
        return self.rl_state

    def render(self):
        pass

    def step(self, action):
        self.count += 1
        action_tensor = torch.ones(8) * -1
        # action_tensor[action] = 1
        b = [action >> i & 1 for i in range(7,-1,-1)]
        for idx, v in enumerate(b):
            if v == 1:
                action_tensor[idx] = 1

        new_input = torch.cat((action_tensor, self.dynamics_output[0]), 0)
        new_input = new_input[None, None, :]
        self.dynamics_input = self.dynamics_input[:, 1:, :]
        self.dynamics_input = torch.cat((self.dynamics_input, new_input), 1)
        self.dynamics_output = self.fwd_dynamics_step(self.dynamics_input)
        self.update_rl_state()

        next_state = self.rl_state
        reward = self.reward
        done = False
        if self.count > 100:
            done = True
        placeholder = None
        return next_state, reward, done, placeholder

env = SOFTROBOTSIM()
state_size = env.state_size
num_actions = env.action_size
# quit()

# env = gym.make('CartPole-v0')

# state_size = env.observation_space.shape[0]
# num_actions = env.action_space.n

Rollout = namedtuple('Rollout', ['states', 'actions', 'rewards', 'next_states', ])


def train(epochs=100, num_rollouts=10, render_frequency=None):
    mean_total_rewards = []
    global_rollout = 0
    start_time = time.time()

    for epoch in range(epochs):
        rollouts = []
        rollout_total_rewards = []

        if epoch == 0 or (epoch % 100) == 99:
            torch.save(actor, "./policy_iterations/" + str(epoch) + ".pt")

        for t in range(num_rollouts):
            env.new_target()
            state = env.reset()
            done = False

            samples = []

            reward_list = []
            while not done:
                if render_frequency is not None and global_rollout % render_frequency == 0:
                    env.render()

                with torch.no_grad():
                    action = get_action(state)

                next_state, reward, done, _ = env.step(action)

                # reward_list.append(reward)

                # Collect samples
                samples.append((state, action, reward, next_state))

                state = next_state
            # print(reward_list)

            # Transpose our samples
            states, actions, rewards, next_states = zip(*samples)

            states = torch.stack([torch.from_numpy(state) for state in states], dim=0).float()
            next_states = torch.stack([torch.from_numpy(state) for state in next_states], dim=0).float()
            actions = torch.as_tensor(actions).unsqueeze(1)
            rewards = torch.as_tensor(rewards).unsqueeze(1)

            rollouts.append(Rollout(states, actions, rewards, next_states))

            rollout_total_rewards.append(rewards.sum().item())
            global_rollout += 1

        update_agent(rollouts)
        mtr = np.mean(rollout_total_rewards)
        print(f'E: {epoch}.\tMean total reward across {num_rollouts} rollouts: {mtr}')

        mean_total_rewards.append(mtr)

    end_time = time.time()
    print("-----Time----")
    print(end_time-start_time)

    plt.plot(mean_total_rewards)
    plt.show()


actor_hidden = 64
actor = nn.Sequential(nn.Linear(state_size, actor_hidden),
                      # nn.ReLU(),
                      nn.Tanh(),
                      nn.Linear(actor_hidden, num_actions),
                      nn.Softmax(dim=1))


def get_action(state):
    state = torch.tensor(state).float().unsqueeze(0)  # Turn state into a batch with a single element
    dist = Categorical(actor(state))  # Create a distribution from probabilities for actions
    return dist.sample().item()

# Critic takes a state and returns its values
critic_hidden = 32
critic = nn.Sequential(nn.Linear(state_size, critic_hidden),
                       nn.ReLU(),
                       nn.Linear(critic_hidden, 1))
critic_optimizer = Adam(critic.parameters(), lr=0.005)


def update_critic(advantages):
    loss = .5 * (advantages ** 2).mean()  # MSE
    critic_optimizer.zero_grad()
    loss.backward()
    critic_optimizer.step()


# delta, maximum KL divergence
# max_d_kl = 0.01
max_d_kl = 0.005


def update_agent(rollouts):
    states = torch.cat([r.states for r in rollouts], dim=0)
    actions = torch.cat([r.actions for r in rollouts], dim=0).flatten()

    advantages = [estimate_advantages(states, next_states[-1], rewards) for states, _, rewards, next_states in rollouts]
    advantages = torch.cat(advantages, dim=0).flatten()

    # Normalize advantages to reduce skewness and improve convergence
    advantages = (advantages - advantages.mean()) / advantages.std()

    update_critic(advantages)

    distribution = actor(states)
    distribution = torch.distributions.utils.clamp_probs(distribution)
    probabilities = distribution[range(distribution.shape[0]), actions]

    # Now we have all the data we need for the algorithm

    # We will calculate the gradient wrt to the new probabilities (surrogate function),
    # so second probabilities should be treated as a constant
    L = surrogate_loss(probabilities, probabilities.detach(), advantages)
    KL = kl_div(distribution, distribution)

    parameters = list(actor.parameters())

    g = flat_grad(L, parameters, retain_graph=True)
    d_kl = flat_grad(KL, parameters, create_graph=True)  # Create graph, because we will call backward() on it (for HVP)

    def HVP(v):
        return flat_grad(d_kl @ v, parameters, retain_graph=True)

    search_dir = conjugate_gradient(HVP, g)
    max_length = torch.sqrt(2 * max_d_kl / (search_dir @ HVP(search_dir)))
    max_step = max_length * search_dir

    def criterion(step):
        apply_update(step)

        with torch.no_grad():
            distribution_new = actor(states)
            distribution_new = torch.distributions.utils.clamp_probs(distribution_new)
            probabilities_new = distribution_new[range(distribution_new.shape[0]), actions]

            L_new = surrogate_loss(probabilities_new, probabilities, advantages)
            KL_new = kl_div(distribution, distribution_new)

        L_improvement = L_new - L

        if L_improvement > 0 and KL_new <= max_d_kl:
            return True

        apply_update(-step)
        return False

    i = 0
    while not criterion((0.9 ** i) * max_step) and i < 10:
        i += 1


def estimate_advantages(states, last_state, rewards):
    values = critic(states)
    last_value = critic(last_state.unsqueeze(0))
    next_values = torch.zeros_like(rewards)
    for i in reversed(range(rewards.shape[0])):
        last_value = next_values[i] = rewards[i] + 0.99 * last_value
    advantages = next_values - values
    return advantages


def surrogate_loss(new_probabilities, old_probabilities, advantages):
    return (new_probabilities / old_probabilities * advantages).mean()


def kl_div(p, q):
    p = p.detach()
    return (p * (p.log() - q.log())).sum(-1).mean()


def flat_grad(y, x, retain_graph=False, create_graph=False):
    if create_graph:
        retain_graph = True

    g = torch.autograd.grad(y, x, retain_graph=retain_graph, create_graph=create_graph)
    g = torch.cat([t.view(-1) for t in g])
    return g


def conjugate_gradient(A, b, delta=0., max_iterations=10):
    x = torch.zeros_like(b)
    r = b.clone()
    p = b.clone()

    i = 0
    while i < max_iterations:
        AVP = A(p)

        dot_old = r @ r
        alpha = dot_old / (p @ AVP)

        x_new = x + alpha * p

        if (x - x_new).norm() <= delta:
            return x_new

        i += 1
        r = r - alpha * AVP

        beta = (r @ r) / dot_old
        p = r + beta * p

        x = x_new
    return x


def apply_update(grad_flattened):
    n = 0
    for p in actor.parameters():
        numel = p.numel()
        g = grad_flattened[n:n + numel].view(p.shape)
        p.data += g
        n += numel


if __name__ == '__main__':
    # Train our agent
    train(epochs=5000, num_rollouts=10, render_frequency=50)

    if SAVE_THIS_MODEL:
        torch.save(actor, "actor_trpo.pt")
        torch.save(critic, "critic_trpo.pt")
## Reference link:
# https://towardsdatascience.com/deep-q-learning-tutorial-mindqn-2a4c855abffc#:~:text=Deep%20Q%2DLearning%20uses%20Experience,to%20train%20after%20each%20step.
## Reference Code:
# https://github.com/mswang12/minDQN/blob/main/minDQN.py

import tensorflow as tf
import numpy as np
from tensorflow import keras
import autompc
import pickle
import torch

from collections import deque
import time
import random

RANDOM_SEED = 5
tf.random.set_seed(RANDOM_SEED)
np.random.seed(RANDOM_SEED)

# An episode a full game
train_episodes = 300
test_episodes = 100



surrogate_filepath = 'surrogate.pkl'
with open(surrogate_filepath, 'rb') as f:
    surrogate = pickle.load(f)
torch_model = surrogate.net # This is a torch.nn.Module with trained weights that you can call forward to get infereence.

# example
act = torch.zeros(8).double()
obs = torch.ones(24).double()
print('x_t = ', obs)
obs = surrogate.pred(obs, act)
print('x_{t+1} = ', obs)

#def agent(state_shape, action_shape):
#    """ The agent maps X-states to Y-actions
#    e.g. The neural network output is [.1, .7, .1, .3]
#    The highest value 0.7 is the Q-Value.
#    The index of the highest action (0.7) is action #1.
#    """
#    learning_rate = 0.001
#    init = tf.keras.initializers.HeUniform()
#    model = keras.Sequential()
#    model.add(keras.layers.Dense(24, input_shape=state_shape, activation='relu', kernel_initializer=init))
#    model.add(keras.layers.Dense(12, activation='relu', kernel_initializer=init))
#    model.add(keras.layers.Dense(action_shape, activation='linear', kernel_initializer=init))
#    model.compile(loss=tf.keras.losses.Huber(), optimizer=tf.keras.optimizers.Adam(lr=learning_rate), metrics=['accuracy'])
#    return model
#
#def get_qs(model, state, step):
#    return model.predict(state.reshape([1, state.shape[0]]))[0]

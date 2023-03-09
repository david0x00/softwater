import torch
import fwd_dynamics
from fwd_dynamics import LSTM_DYNAMICS

# https://towardsdatascience.com/trust-region-policy-optimization-trpo-explained-4b56bd206fc2
model = torch.load("lstm_model_1.pt")
model.eval()

x, y = fwd_dynamics.val_dataset[0]
x = x[None, :, :]
y = y[None, :]
with torch.no_grad():
    y_pred = model(x)

print(x)
print(y)
print(y_pred)

loss = fwd_dynamics.loss_function(y_pred, y)
print(loss)

start_state = None

actor_hidden = 32
actor = nn.Sequential(nn.Linear(state_size, actor_hidden),
                      nn.ReLU(),
                      nn.Linear(actor_hidden, num_actions),
                      nn.Softmax(dim=1))


def get_action(state):
    pass

def train(epochs=100, batch_steps=1024, gamma=0.99, delta=0.005, la=0.98):

    for epoch in range(epochs):
        for t in range(batch_steps):
            state = start_state
            with torch.no_grad():
                action = get_action(state)

    pass
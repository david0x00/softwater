import pandas as pd
import numpy as np
import random

import torch
import torch.nn as nn
from torch.autograd import Variable 
from torch.utils.data import Dataset, DataLoader

df = pd.read_csv("all_data_organized.csv")

TORCH_SEED = 101
RANDOM_SEED = 10

PRESSURE_MIN_VAL = 96
PRESSURE_MAX_VAL = 123.1

X_MARKER_MIN_VAL = -18 
X_MARKER_MAX_VAL = 18

Y_MARKER_MIN_VAL = 0
Y_MARKER_MAX_VAL = 39

SOLENOID_MIN_VAL = 0
SOLENOID_MAX_VAL = 1

FILE_DATA_IDX = "data_index"

TRAIN_PERCENTAGE = 0.80
VALIDATION_PERCENTAGE = 0.05
TEST_PERCENTAGE = 0.15

SEQUENCE_LENGTH = 4
BATCH_SIZE = 4



## Normalize within the range [-1,+1]
def scale_data(data, pressure=False, x_marker=False, y_marker=False, solenoid=False):
    if pressure:
        min_val = PRESSURE_MIN_VAL
        max_val = PRESSURE_MAX_VAL
    elif x_marker:
        min_val = X_MARKER_MIN_VAL
        max_val = X_MARKER_MAX_VAL
    elif y_marker:
        min_val = Y_MARKER_MIN_VAL
        max_val = Y_MARKER_MAX_VAL
    elif solenoid:
        min_val = SOLENOID_MIN_VAL
        max_val = SOLENOID_MAX_VAL

    return (2*((data - min_val) / (max_val - min_val))) - 1

def inverse_scale_data(data, pressure=False, x_marker=False, y_marker=False, solenoid=False):
    if pressure:
        min_val = PRESSURE_MIN_VAL
        max_val = PRESSURE_MAX_VAL
    elif x_marker:
        min_val = X_MARKER_MIN_VAL
        max_val = X_MARKER_MAX_VAL
    elif y_marker:
        min_val = Y_MARKER_MIN_VAL
        max_val = Y_MARKER_MAX_VAL
    elif solenoid:
        min_val = SOLENOID_MIN_VAL
        max_val = SOLENOID_MAX_VAL

    return (0.5*(data + 1)*(max_val - min_val)) + min_val


## Normalize the Data
solenoid_labels = ["M1-AL-IN", "M1-AL-OUT", "M1-AR-IN", "M1-AR-OUT", "M2-AL-IN", "M2-AL-OUT", "M2-AR-IN", "M2-AR-OUT"]
pressure_labels = ["M1-PL", "M1-PR", "M2-PL", "M2-PR"]
x_marker_labels = ["M1X", "M2X", "M3X", "M4X", "M5X", "M6X", "M7X", "M8X", "M9X", "M10X"]
y_marker_labels = ["M1Y", "M2Y", "M3Y", "M4Y", "M5Y", "M6Y", "M7Y", "M8Y", "M9Y", "M10Y"]

x_labels = solenoid_labels + pressure_labels + x_marker_labels + y_marker_labels
y_labels = pressure_labels + x_marker_labels + y_marker_labels

solenoid_df = df[solenoid_labels]
pressure_df = df[pressure_labels]
x_marker_df = df[x_marker_labels]
y_marker_df = df[y_marker_labels]
file_idx_df = df[[FILE_DATA_IDX]]

pressure_df = scale_data(pressure_df, pressure=True)
x_marker_df = scale_data(x_marker_df, x_marker=True)
y_marker_df = scale_data(y_marker_df, y_marker=True)
solenoid_df = scale_data(solenoid_df, solenoid=True)

data_dfs = [solenoid_df, pressure_df, x_marker_df, y_marker_df, file_idx_df]
data_full = pd.concat(data_dfs, axis=1)
shuffled_idxs_full = list(range(len(data_full)))
random.seed(RANDOM_SEED)
random.shuffle(shuffled_idxs_full)

## Format the data for the network
## https://www.crosstab.io/articles/time-series-pytorch-lstm/
class SequenceDataset(Dataset):
    def __init__(self, dataframe, features, target, sequence_length=4, train=False, validation=False, test=False):
        self.features = features
        self.target = target
        self.sequence_length = sequence_length
        self.y = torch.tensor(dataframe[target].values).float()
        self.x = torch.tensor(dataframe[features].values).float()
        self.data_idxs = dataframe[FILE_DATA_IDX]
        self.init_partitions()
        self.partition_idxs = list(range(len(data_full)))
        if train:
            self.partition_idxs = self.train_set
        elif validation:
            self.partition_idxs = self.validation_set
        elif test:
            self.partition_idxs = self.test_set

    def init_partitions(self):
        train_idx_end = int(len(data_full) * TRAIN_PERCENTAGE)
        validation_idx_end = int(len(data_full) * (VALIDATION_PERCENTAGE + TRAIN_PERCENTAGE))
        self.train_set = shuffled_idxs_full[:train_idx_end]
        self.validation_set = shuffled_idxs_full[train_idx_end:validation_idx_end]
        self.test_set = shuffled_idxs_full[validation_idx_end:]

    def __len__(self):
        return len(self.partition_idxs)

    def __getitem__(self, idx):
        i = self.partition_idxs[idx]
        i_adj = self.data_idxs[i]
        if i_adj >= self.sequence_length:
            i_start = i - self.sequence_length
            x = self.x[i_start:i, :]
        else:
            padding = self.x[i-i_adj].repeat(self.sequence_length - i_adj, 1)
            x = self.x[i-i_adj:i, :]
            x = torch.cat((padding, x), 0)

        return x, self.y[i]

train_dataset = SequenceDataset(
    data_full,
    x_labels,
    y_labels,
    train=True
)

val_dataset = SequenceDataset(
    data_full,
    x_labels,
    y_labels,
    validation=True
)

test_dataset = SequenceDataset(
    data_full,
    x_labels,
    y_labels,
    test=True
)

# x, y = train_dataset[i]

torch.manual_seed(TORCH_SEED)

train_loader = DataLoader(train_dataset, batch_size=BATCH_SIZE, shuffle=False)
val_loader = DataLoader(val_dataset, batch_size=BATCH_SIZE, shuffle=False)
test_loader = DataLoader(test_dataset, batch_size=BATCH_SIZE, shuffle=False)

# x,y = next(iter(train_loader))


class LSTM_DYNAMICS(nn.Module):
    def __init__(self, num_sensors, hidden_units, num_outputs):
        super().__init__()
        self.num_sensors = num_sensors
        self.hidden_units = hidden_units
        self.num_outputs = num_outputs
        self.num_layers = 1
        
        self.lstm = nn.LSTM(
            input_size=num_sensors,
            hidden_size=hidden_units,
            batch_first=True,
            num_layers=self.num_layers
        )

        self.linear = nn.Linear(in_features=self.hidden_units, out_features=num_outputs)
    
    def forward(self, x):
        batch_size = x.shape[0]
        h0 = torch.zeros(self.num_layers, batch_size, self.hidden_units).requires_grad_()
        c0 = torch.zeros(self.num_layers, batch_size, self.hidden_units).requires_grad_()

        _, (hn, _) = self.lstm(x, (h0, c0))
        #out = self.linear(hn[0]).flatten()
        out = self.linear(hn[0])

        return out

## Istantiate the model
learning_rate = 5e-5
num_hidden_units = 128

loss_function = nn.MSELoss()

if __name__ == "__main__":

    model = LSTM_DYNAMICS(num_sensors=len(x_labels), hidden_units=num_hidden_units, num_outputs=len(y_labels))
    optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate)
    ## Train the Model

    def train_model(data_loader, model, loss_function, optimizer):
        num_batches = len(data_loader)
        total_loss = 0
        model.train()

        for X, y in data_loader:
            output = model(X)
            loss = loss_function(output, y)

            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

            total_loss += loss.item()

        avg_loss = total_loss / num_batches
        print(f"Train loss: {avg_loss}")

    def test_model(data_loader, model, loss_function):

        num_batches = len(data_loader)
        total_loss = 0

        model.eval()
        with torch.no_grad():
            for X, y in data_loader:
                output = model(X)
                total_loss += loss_function(output, y).item()

        avg_loss = total_loss / num_batches
        print(f"Test loss: {avg_loss}")


    print("Untrained test\n--------")
    test_model(test_loader, model, loss_function)
    print()

    for ix_epoch in range(2):
        print(f"Epoch {ix_epoch}\n---------")
        train_model(train_loader, model, loss_function, optimizer=optimizer)
        test_model(test_loader, model, loss_function)
        print()

    # x, y = val_dataset[0]
    # x = x[None, :, :]
    # y = y[None, :]
    # model.eval()
    # with torch.no_grad():
    #     y_pred = model(x)

    # print(x)
    # print(y)
    # print(y_pred)

    # loss = loss_function(y_pred, y)
    # print(loss)

    # torch.save(model, "lstm_model_1.pt")

    # model = torch.load("lstm_model_1.pt")
    model.eval()

    train_set_errors = []
    for val in train_dataset:
        x, y = val
        x = x[None, :, :]
        y = y[None, :]
        with torch.no_grad():
            y_pred = model(x)
        
        xe_true = y[0][13]
        xe_pred = y_pred[0][13]
        xe_true_inv = inverse_scale_data(xe_true, x_marker=True)
        xe_pred_inv = inverse_scale_data(xe_pred, x_marker=True)

        ye_true = y[0][23]
        ye_pred = y_pred[0][23]
        ye_true_inv = inverse_scale_data(ye_true, y_marker=True)
        ye_pred_inv = inverse_scale_data(ye_pred, y_marker=True)

        xe_error = xe_true_inv - xe_pred_inv
        # print(xe_true_inv)
        # print(xe_pred_inv)
        # print(xe_error)
        ye_error = ye_true_inv - ye_pred_inv
        # print(ye_true_inv)
        # print(ye_pred_inv)
        # print(ye_error)
        error = np.sqrt(xe_error*xe_error + ye_error*ye_error)
        # print(error)
        train_set_errors.append(error)

    train_iqr_arr = np.array(train_set_errors)
    print("Train Set")
    print("Average Error: " + str(train_iqr_arr.mean()) + " cm")
    q3, q1 = np.percentile(train_iqr_arr, [75 ,25])
    print("IQR (cm): " + str(q1) + ", " + str(q3))


    test_set_errors = []
    for val in test_dataset:
        x, y = val
        x = x[None, :, :]
        y = y[None, :]
        with torch.no_grad():
            y_pred = model(x)
        
        xe_true = y[0][13]
        xe_pred = y_pred[0][13]
        xe_true_inv = inverse_scale_data(xe_true, x_marker=True)
        xe_pred_inv = inverse_scale_data(xe_pred, x_marker=True)

        ye_true = y[0][23]
        ye_pred = y_pred[0][23]
        ye_true_inv = inverse_scale_data(ye_true, y_marker=True)
        ye_pred_inv = inverse_scale_data(ye_pred, y_marker=True)

        xe_error = xe_true_inv - xe_pred_inv
        # print(xe_true_inv)
        # print(xe_pred_inv)
        # print(xe_error)
        ye_error = ye_true_inv - ye_pred_inv
        # print(ye_true_inv)
        # print(ye_pred_inv)
        # print(ye_error)
        error = np.sqrt(xe_error*xe_error + ye_error*ye_error)
        # print(error)
        test_set_errors.append(error)

    test_iqr_arr = np.array(test_set_errors)
    print("Testing Set")
    print("Average Error: " + str(test_iqr_arr.mean()) + " cm")
    q3, q1 = np.percentile(test_iqr_arr, [75 ,25])
    print("IQR (cm): " + str(q1) + ", " + str(q3))
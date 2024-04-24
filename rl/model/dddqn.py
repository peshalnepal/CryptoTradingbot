import torch
import torch.nn as nn

class DDDQN(torch.nn.Module):
    def __init__(self, input_features, window_size):
        super().__init__()
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.input_size = input_features * window_size
        self.leaky_relu = torch.nn.LeakyReLU(negative_slope=0.1)
        self.d1 = torch.nn.Linear(self.input_size, 256)
        self.bn1 = torch.nn.BatchNorm1d(256)
        self.d2 = torch.nn.Linear(256, 512)
        self.bn2 = torch.nn.BatchNorm1d(512)
        self.drop1 = torch.nn.Dropout(0.3)
        self.d3 = torch.nn.Linear(512, 1024)
        self.bn3 = torch.nn.BatchNorm1d(1024)
        self.drop2 = torch.nn.Dropout(0.3)
        self.d4 = torch.nn.Linear(1024, 512)
        self.bn4 = torch.nn.BatchNorm1d(512)
        self.drop3 = torch.nn.Dropout(0.3)
        self.d5 = torch.nn.Linear(512, 256)
        self.bn5 = torch.nn.BatchNorm1d(256)
        self.drop4 = torch.nn.Dropout(0.3)
        self.dv1 = torch.nn.Linear(256, 128)  # value hidden layer
        self.da1 = torch.nn.Linear(256, 128)  # actions hidden layer
        self.dv2 = torch.nn.Linear(128, 1)  # value output
        self.da2 = torch.nn.Linear(128, 9)  # actions output

    def forward(self, input_data):
        input_data = input_data.reshape(input_data.size(0), -1)  # Flatten the input tensor
        x = self.leaky_relu(self.d1(input_data)).to(self.device)
        x = self.bn1(x)
        x = x.view(x.size(0), -1)  # equivalent to Flatten()
        x = self.leaky_relu(self.d2(x))
        x = self.bn2(x)
        x = self.drop1(x)
        x = self.leaky_relu(self.d3(x))
        x = self.bn3(x)
        x = self.drop2(x)
        x = self.leaky_relu(self.d4(x))
        x = self.bn4(x)
        x = self.drop3(x)
        x = self.leaky_relu(self.d5(x))
        x = self.bn5(x)
        x = self.drop4(x)
        v = self.leaky_relu(self.dv1(x))
        a = self.leaky_relu(self.da1(x))
        v = self.dv2(v)
        a = self.da2(a)
        Q = v + (a - torch.mean(a, dim=1, keepdim=True))
        return Q

    def advantage(self, state):
        x = self.leaky_relu(self.d1(state))
        x = self.bn1(x)
        x = x.view(x.size(0), -1)
        x = self.leaky_relu(self.d2(x))
        x = self.bn2(x)
        x = self.drop1(x)
        x = self.leaky_relu(self.d3(x))
        x = self.bn3(x)
        x = self.drop2(x)
        x = self.leaky_relu(self.d4(x))
        x = self.bn4(x)
        x = self.drop(x)
        x = self.leaky_relu
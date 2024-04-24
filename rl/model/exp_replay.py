import numpy as np
import torch

class ExpReplay():
    def __init__(self, num_features, window_size, device, buffer_size=1000000):
        self.num_features = num_features
        self.device = device
        self.buffer_size = buffer_size
        self.state_mem = np.zeros((self.buffer_size, self.num_features, window_size), dtype=np.float32)
        self.action_mem = np.ones((self.buffer_size), dtype=np.int32)
        self.reward_mem = np.zeros((self.buffer_size), dtype=np.compat.long)
        self.next_state_mem = np.zeros((self.buffer_size, self.num_features, window_size), dtype=np.float32)
        self.done_mem = np.zeros((self.buffer_size), dtype=bool)
        self.counter = 0

    def add_exp(self, state, action, reward, next_state, done):
        pointer = self.counter % self.buffer_size
        self.state_mem[pointer] = state.cpu().numpy()
        self.action_mem[pointer] = action
        self.reward_mem[pointer] = reward
        self.next_state_mem[pointer] = next_state.cpu().numpy()
        self.done_mem[pointer] = 1 - int(done)
        self.counter += 1


    def sample_exp(self, batch_size=64):
        max_mem = min(self.counter, self.buffer_size)
        batch = np.random.choice(max_mem, batch_size, replace=False)
        states = torch.tensor(self.state_mem[batch], dtype=torch.float32).to(self.device)
        actions = torch.tensor(self.action_mem[batch], dtype=torch.int64).to(self.device)
        rewards = torch.tensor(self.reward_mem[batch], dtype=torch.float32).to(self.device)
        next_states = torch.tensor(self.next_state_mem[batch], dtype=torch.float32).to(self.device)
        dones = torch.tensor(self.done_mem[batch], dtype=torch.bool).to(self.device)
        return states, actions, rewards, next_states, dones
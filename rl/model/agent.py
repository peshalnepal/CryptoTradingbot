import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.optim.lr_scheduler import ExponentialLR
from .dddqn import DDDQN
from .exp_replay import ExpReplay

class Agent_DQN():
    def __init__(self, data_shape, num_episodes, window_size=48, gamma=0.99, update_interval=96, lr=0.01, min_epsilon=0.02):

        self.required_btc_to_sell =  0.001
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.window_size = window_size
        self.data_shape = data_shape
        self.portfolio = [0, 0, 0]  # [total BTC, cash_held, total_portfolio_value (BTC value + cash held - initial investment)]
        self.gamma = gamma
        self.num_episodes = num_episodes
        self.epsilon = 1.0
        self.min_epsilon = min_epsilon
        self.update_interval = update_interval
        self.trainstep = 0
        self.memory = ExpReplay(self.window_size, data_shape[1], self.device)
        self.batch_size = 128
        self.online_net = DDDQN(self.data_shape[1], window_size).to(self.device)
        self.target_net = DDDQN(self.data_shape[1], window_size).to(self.device)
        self.target_net.load_state_dict(self.online_net.state_dict())

        initial_learning_rate = lr
        decay_steps = self.num_episodes * self.data_shape[0] // 10  # You can adjust the divisor to control the decay rate
        decay_rate = 0.9  # You can adjust this value to control the decay rate
        self.optimizer = optim.Adam(self.online_net.parameters(), lr=initial_learning_rate)
        self.scheduler = ExponentialLR(self.optimizer, gamma=decay_rate)
        self.criterion = nn.MSELoss()


    def get_action(self, state, cash_balance):
        if np.random.rand() <= self.epsilon:
            if self.portfolio[0] > self.required_btc_to_sell:
                return np.random.choice([0, 1, 2, 3,])
            elif cash_balance > 0:
                return np.random.choice([5, 6, 7, 8])
            else:
                action = 4  # hold
                return action
        else:
            with torch.no_grad():
                self.online_net.eval()  # Set the model to evaluation mode
                actions = self.online_net(state)
                self.online_net.train()  # Set the model back to training mode
                if self.portfolio[0] > self.required_btc_to_sell:
                    action = torch.argmax(actions).item()
                elif cash_balance > 0:
                    action = torch.argmax(actions[0, 4:]) + 4
                else:
                    action = 4  # hold action
            return action

    def update_target(self):
        self.target_net.load_state_dict(self.online_net.state_dict())

    def update_epsilon(self):
        if self.epsilon > self.min_epsilon:
            b = self.min_epsilon**(1/(self.num_episodes*self.data_shape[0]))
            self.epsilon = b**self.trainstep

    def train(self):
        if self.memory.counter < self.batch_size:
            return

        if self.trainstep % self.update_interval == 0:
            self.update_target()

        states, actions, rewards, next_states, dones = self.memory.sample_exp(self.batch_size)

        states = states.to(self.device).float()
        actions = actions.to(self.device).long()
        rewards = rewards.to(self.device).float()
        next_states = next_states.to(self.device).float()
        dones = dones.to(self.device).float()

        q_next_state_online_net = self.online_net(next_states)
        q_next_state_target_net = self.target_net(next_states)

        max_action = torch.argmax(q_next_state_online_net, dim=1).to(self.device)

        batch_index = torch.arange(self.batch_size, dtype=torch.int64).to(self.device)

        q_predicted = self.online_net(states)
        q_target = q_predicted.clone().detach()

        q_target[batch_index, actions] = rewards + self.gamma * q_next_state_target_net[batch_index, max_action] * dones

        loss = self.criterion(q_predicted, q_target)
        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()

        self.update_epsilon()
        self.trainstep += 1
        return loss.item()


    def save_model(self):
        import os

        output_directory = "output"
        online_model_directory = os.path.join(output_directory, "online_model")
        target_model_directory = os.path.join(output_directory, "target_model")

        os.makedirs(online_model_directory, exist_ok=True)
        os.makedirs(target_model_directory, exist_ok=True)

        torch.save(self.online_net.state_dict(), os.path.join(online_model_directory, 'model.pt'))
        torch.save(self.target_net.state_dict(), os.path.join(target_model_directory, 'model.pt'))

    def load_model(self, model_path):
        """Loads a trained model from a .pt file.

        Args:
            model_path (str): Path to the model file.
        """
        checkpoint = torch.load(model_path, map_location=self.device)
        self.online_net.load_state_dict(checkpoint)
        self.target_net.load_state_dict(checkpoint)


    def calculate_reward(self, t, BTC_df, BTC_close_price_unscaled, amount_to_sell, initial_investment, trading_fee_rate):
        BTC_held, cash_held, previous_portfolio_value = self.portfolio

        unscaled_close_price = BTC_close_price_unscaled["Close"].iloc[t]
        value_of_BTC_sold = unscaled_close_price * amount_to_sell
        trading_fee = value_of_BTC_sold * trading_fee_rate
        cash_received = value_of_BTC_sold - trading_fee
        new_cash_held = cash_held + cash_received
        new_BTC_held = BTC_held - amount_to_sell

        # Calculate portfolio value
        btc_cash_value = new_BTC_held * unscaled_close_price
        new_portfolio_value = new_cash_held + btc_cash_value

        # Calculate the reward based on the change in portfolio value
        portfolio_difference = new_portfolio_value - previous_portfolio_value
        # reward = 1 if portfolio_difference > 0 else -1
        print(f"--SOLD: Giving reward to RL Model --\nportfolio_diff - {portfolio_difference}\n")
        

        # Update portfolio
        self.portfolio = [new_BTC_held, new_cash_held, new_portfolio_value]
        
        return trading_fee, portfolio_difference

    def trade(self, t, action, BTC_df, BTC_df_unscaled, initial_investment, trading_fee_rate):
        reward = 0
        BTC_held, cash_balance, previous_portfolio_value = self.portfolio
        sell_percentages = [0.025, 0.05, 0.075, .1]
        buy_percentages = [0.025, 0.05, 0.075, .1]

        if action >= 0 and action <= 3 and BTC_held > 0.01:
            print("Selling: " + str(sell_percentages[action]) + "% of portfolio at BTC price " + str(BTC_df_unscaled["Close"].iloc[t]))
            print("Current cash_balance: " + str(round(cash_balance, 2)))
            
            sell_percentage = sell_percentages[action]
            amount_to_sell = BTC_held * sell_percentage

            while amount_to_sell > 0 and self.portfolio[0] > 0.01:
                print("BTC amount: " + str(round(BTC_held, 7)))
                print("Current ask price: " + str(BTC_df_unscaled["Close"].iloc[t]))
                print('----------------')       

                fee, reward = self.calculate_reward(t, BTC_df, BTC_df_unscaled, amount_to_sell, initial_investment, trading_fee_rate)

                BTC_held, cash_balance, _ = self.portfolio # Update portfolio after selling

                print("Amount BTC sold: " + str(amount_to_sell))
                print("Selling price: " + str(BTC_df_unscaled["Close"].iloc[t]))
                print("Trading fee: " + str(fee))
                print("New BTC amount: " + str(round(BTC_held, 7)))
                print("New cash_balance: " + str(round(cash_balance, 2)))
                print("___________________")
                amount_to_sell = 0
        elif action == 4:
            print("Hold: Price is " + str(BTC_df_unscaled["Close"].iloc[t]))
            self.portfolio[2] = cash_balance + (BTC_held * BTC_df_unscaled["Close"].iloc[t]) - initial_investment
            reward = -0.01
        elif action >= 5 and cash_balance >= 0:
            # print("Buy BTC with: " + str(buy_percentages[action - 5]) + "% of cash_balance at BTC price " + str(BTC_df_unscaled["Close"].iloc[t]))
            buy_percentage = buy_percentages[action - 5]
            BTC_to_buy = (cash_balance * buy_percentage) / BTC_df_unscaled["Close"].iloc[t]
            print("Current cash_balance: " + str(round(cash_balance, 2)))
            print("Current BTC amount: " + str(round(BTC_held, 7)))
            print("BTC purchased: " + str(BTC_to_buy))
            self.portfolio[0] += BTC_to_buy
            self.portfolio[1] -= BTC_df_unscaled["Close"].iloc[t] * BTC_to_buy
            self.portfolio[2] = self.portfolio[1] + (self.portfolio[0] * BTC_df_unscaled["Close"].iloc[t]) - initial_investment
            print("New cash_balance: " + str(round(self.portfolio[1], 2)))
        return reward


    def get_state(self, t, BTC_df):
        num_rows = t - self.window_size + 1
        if num_rows >= 0:
            window = torch.tensor(BTC_df.iloc[num_rows : t + 1].values, dtype=torch.float32).to(self.device)
        else:
            first_row = torch.tensor(BTC_df.iloc[0].values, dtype=torch.float32).unsqueeze(0).to(self.device)
            num_repeats = (-num_rows, 1)
            repeated_first_row = first_row.repeat(num_repeats)
            new_data = torch.tensor(BTC_df.iloc[0 : t + 1].values, dtype=torch.float32).to(self.device)
            window = torch.cat((repeated_first_row, new_data), dim=0)
        return window.unsqueeze(0)

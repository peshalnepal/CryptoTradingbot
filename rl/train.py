from .model.agent import Agent_DQN
from .get_data import get_data
import json
from time import time
from tqdm import tqdm

NUM_EPISODES = 50
INITIAL_INVESTMENT = 1000

def train_rl_model(data):
    train_df, _, train_close, _ = get_data(data, split_ratio=0.8, train_test=True)
    trading_agent = Agent_DQN(train_df.shape, NUM_EPISODES, window_size=48, gamma=0.95, update_interval=96, lr=0.01, min_epsilon=0.02)

    episode_mem = [{"Actions": [], "BTC Held": [], "Cash Held": [], "Portfolio Value": [], "Reward": [], "Done": [], "Epsilon": [], "MSE Loss": []} for i in range(NUM_EPISODES)]
    t0 = time()

    ######################## Training ########################
    for s in tqdm(range(NUM_EPISODES)):
        print(f"\n===== Episode {s + 1} / {NUM_EPISODES} =====")
        state = trading_agent.get_state(0, train_df)
        cash_balance = INITIAL_INVESTMENT
        portfolio_value_usd = INITIAL_INVESTMENT
        # Reset the agent's portfolio at the beginning of each episode
        trading_agent.portfolio = [0 , INITIAL_INVESTMENT, portfolio_value_usd]

        done = False
        for t in range(len(train_df) - 1):
            if done:
                break
            action = trading_agent.get_action(state, cash_balance)
            next_state = trading_agent.get_state(t + 1, train_df)
            reward = trading_agent.trade(t, action, train_df, train_close, INITIAL_INVESTMENT, trading_fee_rate = 0.0075)
            BTC_held, cash_held, new_portfolio_value = trading_agent.portfolio
            cash_balance = cash_held  # update cash balance
            portfolio_value_usd = new_portfolio_value  # update portfolio value

            if t != 0:  # if not the first trade
                done = cash_balance <= 1 and BTC_held <= 0.01
            trading_agent.memory.add_exp(state, action, reward, next_state, done)
            loss = trading_agent.train()
            if not loss:
                loss = 0
            state = next_state

            episode_mem[s]["Actions"].append(int(action))
            episode_mem[s]["BTC Held"].append(float(BTC_held))
            episode_mem[s]["Cash Held"].append(round(float(cash_balance), 2))
            episode_mem[s]["Portfolio Value"].append(float(portfolio_value_usd))
            episode_mem[s]["Reward"].append(float(reward))
            episode_mem[s]["Done"].append(bool(done))
            episode_mem[s]["Epsilon"].append(trading_agent.epsilon)
            episode_mem[s]["MSE Loss"].append(float(loss))

            if t % 100 == 0:
                print(f"BTC Held: {round(episode_mem[s]['BTC Held'][t], 7)}  |  Cash Held: {round(episode_mem[s]['Cash Held'][t], 2)}  |  Portfolio Value: {round(episode_mem[s]['Portfolio Value'][t], 3)}  |   MSE Loss: {round(episode_mem[s]['MSE Loss'][t], 3)}")

    with open('rl/train_output_files/training_scores.out', 'a') as f:
            f.write(f"EPISODE {s} (runtime: {time() - t0})   | Portfolio Value is {round(episode_mem[s]['Portfolio Value'][-1], 3)} Epsilon is {round(trading_agent.epsilon, 3)}   |   MSE Loss is {round(episode_mem[s]['MSE Loss'][-1], 3)}\n")

    with open('rl/train_output_files/episode_mem.json', 'w') as f:
        json.dump(episode_mem, f)

    trading_agent.save_model()
    
    return train_df.shape


from .model.agent import Agent_DQN
from .get_data import get_data
import json
from time import time

NUM_EPISODES = 10
INITIAL_INVESTMENT = 1000

def test_rl_model(data):
    train_df, test_df, _, test_close = get_data(data, split_ratio=0.8, train_test=True)

    model_path = 'rl/output/target_model/model.pt'
    trading_agent = Agent_DQN(train_df.shape, NUM_EPISODES, window_size=48, gamma=0.95, update_interval=96, lr=0.01, min_epsilon=0.02)
    trading_agent.load_model(model_path)

    t0 = time()
    testing_mem = {"Actions": [], "BTC Held": [], "Cash Held": [], "Portfolio Value": [], "Reward": [], "Done": []}
    trading_agent.epsilon = 0
    state = trading_agent.get_state(0, test_df)
    cash_balance = INITIAL_INVESTMENT
    portfolio_value_usd = INITIAL_INVESTMENT
    # Reset the agent's portfolio at the beginning of each episode
    trading_agent.portfolio = [0 , INITIAL_INVESTMENT, portfolio_value_usd]
    # Reset the agent's portfolio at the beginning of each episode

    done = False
    for t in range(len(test_df) - 1):
        if done:
            break
        action = trading_agent.get_action(state, cash_balance)
        next_state = trading_agent.get_state(t + 1, test_df)
        reward = trading_agent.trade(t, action, test_df, test_close, INITIAL_INVESTMENT, trading_fee_rate = 0.01)
        BTC_held, cash_held, new_portfolio_value  = trading_agent.portfolio
        cash_balance = cash_held  # update cash balance
        portfolio_value_usd = new_portfolio_value  # update portfolio value
        if t != 0:  # if not the first trade
                done = cash_balance <= 1 and BTC_held <= 0.01
        state = next_state

        testing_mem["Actions"].append(int(action))
        testing_mem["BTC Held"].append(float(BTC_held))
        testing_mem["Cash Held"].append(round(float(cash_balance),2))
        testing_mem["Portfolio Value"].append(float(portfolio_value_usd))
        testing_mem["Reward"].append(float(reward))
        testing_mem["Done"].append(bool(done))

        if t % 1 == 0:
            print(f"BTC Held: {round(testing_mem['BTC Held'][t], 7)}  |  Cash Held: {round(testing_mem['Cash Held'][t], 2)}  |  Portfolio Value: {round(testing_mem['Portfolio Value'][t], 3)}")

    with open('rl/test_output_files/testing_scores.out', 'a') as f:
        f.write(f"TESTING (runtime: {time() - t0})   |  Portfolio Value is {round(testing_mem['Portfolio Value'][-1], 3)}\n")

    with open('rl/test_output_files/testing_mem.json', 'w') as f:
        json.dump(testing_mem, f)



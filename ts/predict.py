import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from flask import Flask, request
from .torchtsmixer import TSMixer
from .utils.preprocess import preprocess_data

app = Flask(__name__)
# Model parameters
sequence_length = 70
prediction_length = 10
input_channels = 6
output_channels = 6
# Create the TSMixer model
model = TSMixer(sequence_length, prediction_length, input_channels, output_channels)
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

model=model.to(device)
# Loss function and optimizer
criterion = nn.MSELoss()
optimizer = optim.Adam(model.parameters(), lr=0.001)

@app.route('/', methods=['GET'])
def test_connection():
    print("got pinged")
    return "being pingged"

@app.route('/datas', methods=['POST'])
def handle_post():
    # Assuming the list is sent as JSON in the body of the POST request
    json_data = request.json
    your_list = json_data.get("OHLCVT")
    columns=["Timestamp","Open","High","Low","Close","Volume"]
    df = pd.DataFrame(your_list, columns=columns)
    df=preprocess_data(df)
    
    data=np.array(df,dtype=np.float32)
    data=torch.from_numpy(data)
    model.load_state_dict(torch.load("model.pt"))
    model.eval()

    predicted=model(data)
    
    return 'List received', 200

def predict_price(ohlcv_obj):
    # Assuming the list is sent as JSON in the body of the POST request
    df = pd.DataFrame(ohlcv_obj)
    df=preprocess_data(df,columns_to_remove = ["Volume", "Timestamp","%K"])
    df=df.tail(70)
    df=df.reset_index(drop=True)
    data=np.array(df,dtype=np.float32)
    data=torch.from_numpy(data)
    data=data.unsqueeze(0)
    data=data.to(device)
    # print(data.shape)
    model.load_state_dict(torch.load(".\pytorch_tsmixer\model.pt"))
    model.eval()
    # print(data.shape)
    predicted=model(data)
    
    return predicted

if __name__ == '__main__':
    app.run(host="0.0.0.0",port=5000,debug=True)
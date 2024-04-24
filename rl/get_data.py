import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split

def get_data(data, split_ratio=0.8, train_test=False):
    

    # convert date to datetime if it isn't the index
    if data.index.name != 'Timestamp':
        data['Timestamp'] = pd.to_datetime(data['Timestamp'], infer_datetime_format=True)
        print('Timestamp converted to datetime.')
        # set date as index
        data = data.set_index('Timestamp')
        print('Timestamp set as index.')
    
    # drop nan values
    data = data.dropna()
    print('NaN values dropped.')
    
    if train_test:
        cols = data.columns.tolist()
        train_unscaled, test_unscaled = train_test_split(data, train_size=split_ratio,shuffle=False)
        train_scaled = pd.DataFrame(MinMaxScaler().fit_transform(train_unscaled), columns=cols)
        test_scaled = pd.DataFrame(MinMaxScaler().fit_transform(test_unscaled), columns=cols)
        print('Data split.')
        # set the index to the date
        train_unscaled = pd.DataFrame(train_unscaled,  columns=cols)
        test_unscaled = pd.DataFrame(test_unscaled,  columns=cols)
        # convert train_unscaled and test_unscaled to df with only the Close column
        #train_unscaled = train_unscaled[['Close']]
        train_unscaled = train_unscaled.drop(train_unscaled.columns.difference(['Close']), axis=1)
        #test_unscaled = test_unscaled[['Close']]
        test_unscaled = test_unscaled.drop(test_unscaled.columns.difference(['Close']), axis=1)

        train_unscaled.to_csv("rl/train_output_files/train_unscaled.csv")
        train_scaled.to_csv("rl/train_output_files/train_scaled.csv")
        print('Train data saved.')
        test_unscaled.to_csv("rl/test_output_files/test_unscaled.csv")
        test_scaled.to_csv("rl/test_output_files/test_scaled.csv")
        print('Test data saved.')
        return train_scaled, test_scaled, train_unscaled, test_unscaled

    return data
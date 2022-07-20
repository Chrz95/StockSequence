import os, glob
import pandas as pd
import numpy as np
import datetime

List = []

def IsGoodStock(Stocks,name):
    N = len(Stocks)
    high_low = Stocks["High"].subtract(Stocks["Low"], fill_value=0)
    start_mean_low = np.mean(Stocks.iloc[0:int(N*0.1)]["Low"])
    end_mean_low = np.mean(Stocks.iloc[-int(N*0.1):-1]["Low"])
    start_mean_high = np.mean(Stocks.iloc[0:int(N * 0.1)]["High"])
    end_mean_high = np.mean(Stocks.iloc[-int(N * 0.1):-1]["High"])
    mean_low = np.mean(Stocks["Low"])

    first_val = Stocks.iloc[0]["Low"]
    last_val = Stocks.iloc[-1]["Low"]
    min_val_low = np.min(Stocks["Low"])
    max_val_high = np.max(Stocks["High"])
    high_low_mean = np.mean(high_low)

    if  (high_low_mean>10):
        print(name, N, start_mean_low, high_low_mean)

    return Stocks

def MyReadCSV(dir):
    # Ignore empty files
    if os.path.getsize(dir) == 0:
        return pd.DataFrame()

    Stocks = pd.read_csv(dir)

    List.append(dir.split('\\')[1])
    Stocks["Stock"] = dir.split('\\')[1].split('.')[0]
    return IsGoodStock(Stocks,Stocks["Stock"].iloc[0])


def ReadStocks(dir="Stocks"):
    Stocks = pd.concat(map(MyReadCSV, glob.glob(dir + '/*.txt')))
    return Stocks

if __name__ == "__main__":
    Stocks = ReadStocks("Best (Big)")
    print(List)
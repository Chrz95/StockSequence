import os, glob
import pandas as pd
import numpy as np


def MyReadCSV(dir):
    # Ignore empty files
    if os.path.getsize(dir) == 0:
        return pd.DataFrame()

    Stocks = pd.read_csv(dir)
    Stocks["Stock"] = dir.split('\\')[1].split('.')[0]
    return Stocks


def ReadStocks(dir="Stocks"):
    Stocks = pd.concat(map(MyReadCSV, glob.glob(dir + '/*.txt')))
    Stocks['Date'] = pd.to_datetime(Stocks['Date'])
    return Stocks.sort_values(by='Date', ascending=True)

def split(a, n):
    k, m = divmod(len(a), n)
    return (a[i*k+min(i, m):(i+1)*k+min(i+1, m)] for i in range(n))

def Buy_SellStocks(Stocks, N=1000):
    if (N <= 1000):
        Results = open("small.txt", 'w+')
    else:
        Results = open("large.txt", 'w+')

    Balance = 1
    Portofolio = 0
    BoughtStocks = {}  # {NameOfStock:AmountofStocks}
    seq_cnt = 0

    balance_lst = [1]
    port_list = [0]

    Results.write("{}\n".format(N))

    Partitions = list(split(range(len(Stocks)), N))
    Partitions = [(x[0],x[-1]) for x in Partitions]

    for seq_cnt,Partition in enumerate(Partitions):
        start,end = Partition
        Data = Stocks.iloc[start:end]
        column = Data["Low"]
        buy_low_val = column.min()
        buy_low_val_pos = column.idxmin()

        numberOfDifferentStocks = 0
        for i in BoughtStocks.values():
            if (i != 0):
                numberOfDifferentStocks = numberOfDifferentStocks + 1

        if (seq_cnt < N - numberOfDifferentStocks):
            if (buy_low_val <= Balance): # Buy low
                volume = Stocks.iloc[buy_low_val_pos]["Volume"]
                stock = Stocks.iloc[buy_low_val_pos]["Stock"]
                date = Stocks.iloc[buy_low_val_pos]["Date"]

                # Buy low
                if (Stocks.iloc[buy_low_val_pos]["Stock"] in BoughtStocks):
                    if (buy_low_val == 0):
                        Amount = 1
                    else:
                        Amount = min(volume // 10, Balance // buy_low_val, BoughtStocks[stock] + 1)
                    BoughtStocks[stock] += Amount
                else:
                    if (buy_low_val == 0):
                        Amount = 1
                    else:
                        Amount = min(volume // 10, Balance // buy_low_val, 1)
                    BoughtStocks[stock] = Amount

                Balance = Balance - (buy_low_val * Amount)
                balance_lst.append(Balance)

                Results.write("{} {} {} {}\n".format(date.date(), "buy-low", stock.upper(), int(Amount)))
            else: # Sell High
                for stock_name in BoughtStocks.keys():
                    if (BoughtStocks[stock_name] != 0):
                        Stock_rows = Data[Data["Stock"] == stock_name]
                        Stock_rows = Stock_rows[Stock_rows["Volume"] != 0]
                        column = Stock_rows["High"]

                        if (len(column) == 0):
                            print("Column = 0")
                            continue

                        sell_high_val = column.max()
                        sell_high_val_pos = column.idxmax()
                        date = Stocks.iloc[sell_high_val_pos]["Date"]
                        volume = Stocks.iloc[sell_high_val_pos]["Volume"]

                        Amount = min(int(volume // 10), BoughtStocks[stock_name])

                        # Sell high
                        BoughtStocks[stock_name] -= Amount
                        Balance += sell_high_val * Amount
                        balance_lst.append(Balance)

                        Results.write("{} {} {} {}\n".format(date.date(), "sell-high", stock_name.upper(), int(Amount)))
                        break # Only one sell per partition
        else: # If you reach the end, sell everything
            for stock_name in BoughtStocks.keys():
                if (BoughtStocks[stock_name] != 0):
                    Stock_rows = Data[Data["Stock"] == stock_name]
                    Stock_rows = Stock_rows[Stock_rows["Volume"] != 0]
                    column = Stock_rows["High"]

                    if (len(column) == 0):
                        print("Column = 0")
                        continue

                    sell_high_val = column.max()
                    sell_high_val_pos = column.idxmax()

                    date = Stocks.iloc[sell_high_val_pos]["Date"]
                    volume = Stocks.iloc[sell_high_val_pos]["Volume"]

                    Amount = min(int(volume // 10), BoughtStocks[stock_name])

                    # Sell high
                    BoughtStocks[stock_name] -= Amount
                    Balance += sell_high_val * Amount
                    balance_lst.append(Balance)

                    Results.write("{} {} {} {}\n".format(date.date(), "sell-high", stock_name.upper(), int(Amount)))
                    break  # Only one sell per partition


    #print(Balance)
    Results.close()
    return Balance

if __name__ == "__main__":
    Stocks = ReadStocks("Stocks")
    Stocks = Stocks.reset_index() # Set index from 0 to ..
    Stocks.to_csv("Data.csv", index = False)
    #print(Stocks.head(50))
    #print()
    #print(Stocks.dtypes)

    """
    MaxBalance = 1
    MaxN = 10
    for N in range(500,1000):
        print(N)
        Balance = Buy_SellStocks(Stocks, N)
        if (Balance > MaxBalance):
            MaxBalance = Balance
            MaxN = N
            
    print("==============")
    print(MaxN,MaxBalance)
    """
    Balance = Buy_SellStocks(Stocks, 50000)
    print(Balance)

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



def ReadStocks(dir="Stocks"):
    Stocks = pd.concat(map(MyReadCSV, glob.glob(dir + '/*.txt')))
    Stocks['Date'] = pd.to_datetime(Stocks['Date'])
    return Stocks.sort_values(by='Date', ascending=True)


def Buy_SellStocks(Stocks, N=1000):

    buy_range = 10
    original_sell_range = 106
    sell_range = 20
    Balance_record = []

    bad_pair = False

    if (N <= 1000):
        Results = open("small.txt",'w+')
    else:
        Results = open("large.txt", 'w+')

    Balance = 1
    Portofolio = 0
    BoughtStocks = {}  # {NameOfStock:AmountofStocks}

    seq_cnt = 0
    stock_cnt = 0
    CurrentPos = 0

    balance_lst = [1]
    port_list = [0]

    Results.write("{}\n".format(N))

    while (stock_cnt < N):
        print(stock_cnt)
        end = min(CurrentPos + buy_range, len(Stocks))
        column = Stocks.iloc[CurrentPos:end]["Low"]

        if (len(column) == 0):
            buy_range = buy_range + 10
            continue

        buy_low_val = column.min()
        buy_low_val_pos = column.idxmin()

        numberOfDifferentStocks = 0
        for i in BoughtStocks.values():
            if (i != 0):
                numberOfDifferentStocks = numberOfDifferentStocks + 1

        if (stock_cnt >= N - numberOfDifferentStocks): # If we reach the end, sell everything
            for stock_name in BoughtStocks.keys():
                if (BoughtStocks[stock_name] != 0):
                    end = min(CurrentPos + sell_range, len(Stocks))
                    range_rows = Stocks.iloc[CurrentPos:end]
                    Stock_rows = range_rows[range_rows["Stock"] == stock_name]
                    Stock_rows = Stock_rows[Stock_rows["Volume"] != 0]
                    column = Stock_rows["High"]

                    if (len(column) == 0):
                        sell_range = sell_range + 10
                        continue

                    sell_range = original_sell_range

                    sell_high_val = column.max()
                    sell_high_val_pos = column.idxmax()
                    date = Stocks.iloc[sell_high_val_pos]["Date"]
                    volume = Stocks.iloc[sell_high_val_pos]["Volume"]

                    Amount = min(volume // 10, BoughtStocks[stock_name])

                    # Sell high
                    BoughtStocks[stock_name] -= Amount
                    Balance += sell_high_val*Amount
                    balance_lst.append(Balance)

                    Results.write("{} {} {} {}\n".format(date.date(), "sell-high", stock_name.upper(), int(Amount)))

                    CurrentPos = sell_high_val_pos + 1
                    stock_cnt = stock_cnt + 1
        else:
            if (buy_low_val <= Balance):
                volume = Stocks.iloc[buy_low_val_pos]["Volume"]
                stock = Stocks.iloc[buy_low_val_pos]["Stock"]
                date = Stocks.iloc[buy_low_val_pos]["Date"]

                # Buy low
                if (Stocks.iloc[buy_low_val_pos]["Stock"] in BoughtStocks):
                    Amount = min(volume // 10, Balance // buy_low_val, BoughtStocks[stock] + 1)
                    BoughtStocks[stock] += Amount
                else:
                    Amount = min(volume // 10, Balance // buy_low_val, 1)
                    BoughtStocks[stock] = Amount

                Balance = Balance - (buy_low_val * Amount)
                balance_lst.append(Balance)

                Results.write("{} {} {} {}\n".format(date.date(),"buy-low",stock.upper(),int(Amount)))

                CurrentPos = buy_low_val_pos + 1
                stock_cnt = stock_cnt + 1
            else: # Cannot buy anymore, time to sell all the stocks we have accumulated
                for stock_name in BoughtStocks.keys():
                    if (BoughtStocks[stock_name] != 0):
                        end = min(CurrentPos + sell_range, len(Stocks))
                        range_rows = Stocks.iloc[CurrentPos:end]
                        Stock_rows = range_rows[range_rows["Stock"] == stock_name]
                        Stock_rows = Stock_rows[Stock_rows["Volume"] != 0]
                        column = Stock_rows["High"]

                        if (len(column) == 0):
                            sell_range = sell_range + 10
                            continue

                        sell_range = original_sell_range

                        sell_high_val = column.max()
                        sell_high_val_pos = column.idxmax()
                        date = Stocks.iloc[sell_high_val_pos]["Date"]
                        volume = Stocks.iloc[sell_high_val_pos]["Volume"]

                        Amount = min(int(volume // 10), BoughtStocks[stock_name])

                        # Sell high
                        BoughtStocks[stock_name] -= Amount
                        Balance += sell_high_val*Amount
                        balance_lst.append(Balance)

                        Results.write("{} {} {} {}\n".format(date.date(), "sell-high", stock_name.upper(), int(Amount)))

                        CurrentPos = sell_high_val_pos + 1
                        stock_cnt = stock_cnt + 1
                        break

    Results.close()
    print(Balance)

if __name__ == "__main__":
    Stocks = ReadStocks("Stocks")
    Stocks = Stocks.reset_index() # Set index from 0 to ...
    Stocks.to_csv("Data.csv", index = False)
    #print(Stocks.head(50))
    #print()
    #print(Stocks.dtypes)
    Buy_SellStocks(Stocks, 10000)

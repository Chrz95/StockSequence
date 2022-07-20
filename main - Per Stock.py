import os, glob
import pandas as pd

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
    prev_date = 0

    for i in range(len(Stocks)): # Go over each stock

        if (seq_cnt >= N):
            break

        low = Stocks.iloc[i]["Low"]
        open_val = Stocks.iloc[i]["Open"]
        high = Stocks.iloc[i]["High"]
        close = Stocks.iloc[i]["Close"]
        volume = Stocks.iloc[i]["Volume"]
        stock = Stocks.iloc[i]["Stock"]
        date = Stocks.iloc[i]["Date"]

        if (date != prev_date):
            if (low <= Balance): # Buy-low,sell-high
                ######### Buy Low ##########
                if (Stocks.iloc[i]["Stock"] in BoughtStocks):
                    Amount = min(volume // 10, Balance // low, BoughtStocks[stock] + 1)
                    BoughtStocks[stock] += Amount
                else:
                    Amount = min(volume // 10, Balance // low, 1)
                    BoughtStocks[stock] = Amount

                Balance = Balance - (low * Amount)
                balance_lst.append(Balance)

                Results.write("{} {} {} {}\n".format(date.date(), "buy-low", stock.upper(), int(Amount)))
                prev_action = "buy-low"
                seq_cnt = seq_cnt + 1
            else:
                # Sell high
                if (stock in BoughtStocks):
                    Amount = min(int(volume // 10), BoughtStocks[stock])

                    if (Amount != 0):
                        BoughtStocks[stock] -= Amount
                        Balance += high * Amount
                        balance_lst.append(Balance)

                        Results.write("{} {} {} {}\n".format(date.date(), "sell-high", stock.upper(), int(Amount)))
                        prev_action = "sell-high"
                        seq_cnt = seq_cnt + 1
        else:
            if (prev_action == "sell-high"): # Buy close or sell close according to available money:
                if (close <= Balance):  # Buy-close,sell-close
                    ######### Buy close ##########
                    if (Stocks.iloc[i]["Stock"] in BoughtStocks):
                        Amount = min(volume // 10, Balance // close, BoughtStocks[stock] + 1)
                        BoughtStocks[stock] += Amount
                    else:
                        Amount = min(volume // 10, Balance // close, 1)
                        BoughtStocks[stock] = Amount

                    Balance = Balance - (close * Amount)
                    balance_lst.append(Balance)

                    Results.write("{} {} {} {}\n".format(date.date(), "buy-close", stock.upper(), int(Amount)))
                    prev_action = "buy-close"
                    seq_cnt = seq_cnt + 1
                else:
                    # Sell close
                    if (stock in BoughtStocks):
                        Amount = min(int(volume // 10), BoughtStocks[stock])

                        if (Amount != 0):
                            BoughtStocks[stock] -= Amount
                            Balance += close * Amount
                            balance_lst.append(Balance)

                            Results.write("{} {} {} {}\n".format(date.date(), "sell-close", stock.upper(), int(Amount)))
                            prev_action = "sell-close"
                            seq_cnt = seq_cnt + 1

        prev_date = date

    return Balance

if __name__ == "__main__":
    Stocks = ReadStocks("Stocks")
    Stocks = Stocks.reset_index() # Set index from 0 to ..
    Stocks.to_csv("Data.csv", index = False)
    Balance = Buy_SellStocks(Stocks, 100000)
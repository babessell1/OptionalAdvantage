#!/usr/bin/python3
import sys
from yahoo_fin.options import *
from yahoo_fin.stock_info import *
import matplotlib.pyplot as plt
import pandas as pd
from pandas.plotting import register_matplotlib_converters
import numpy as np
from datetime import date, datetime, timedelta
from project_methods.stockTools import *

register_matplotlib_converters()

################################################################################
################################################################################


# define tickers and timeFrame
tickers = ["MSFT", "AAPL"]
startDate = "03/01/2020"
currentDate = "04/02/2020"
#timeFrame = [startDate, currentDate]

#argList = str(sys.argv)
#print(argList)
tick = 'py', '10/13/2020', 'MSFT'
print(tick[2:])
tickers = sys.argv[3:]
startDate = 0
currentDate = int(sys.argv[1]) # number of days
num_of_days_threshold = int(sys.argv[2])

timeFrame = [startDate, currentDate]

#declare list for volatility values
volList = np.zeros(shape=len(tickers))
bestStrikePrices = np.zeros(shape=len(tickers))
callAskList = np.zeros(shape=len(tickers))
putAskList = np.zeros(shape=len(tickers))
#bestCallContracts = np.empty(shape=len(tickers), dtype=str)
bestCallContracts = []
#bestPutContracts = np.empty(shape=len(tickers), dtype=str)
bestPutContracts = []
#iterate through tickers, append volatility values for each
for i in range(len(tickers)):
    ticker = tickers[i]
    # pull stock data from yahoo finance
    df_stock = pullStockData(timeFrame, ticker , False)
    #print(df_stock.head())
    # calculate volatility, add return values to dataFrame
    volatility = calcVolatility(df_stock, ticker)
    volList[i] = volatility

    # find first expiration date above threshold
    ticker = tickers[i]
    expDate = findExpDate(ticker, num_of_days_threshold)
    optchain = get_options_chain(ticker, expDate)
    calls = optchain.get('calls')
    # print(calls)
    puts = optchain.get('puts')
    #print(puts)

    strikeList_calls = calls.Strike.to_numpy()
    strikeList_puts = puts.Strike.to_numpy()

    currentPrice = get_live_price(ticker)
    # find put/call price closest to current stock price
    closest_j_calls = closest(strikeList_calls, currentPrice, 0)
    closest_j_puts = closest(strikeList_puts, currentPrice, 0)
    closest_strikePrice_calls = strikeList_calls[closest_j_calls]
    closest_strikePrice_puts = strikeList_puts[closest_j_puts]

    if closest_strikePrice_calls == closest_strikePrice_puts:
        print('Strike Price: ' + str(closest_strikePrice_calls))
        callAsk = calls['Ask'][closest_j_calls]
        putAsk = puts['Ask'][closest_j_puts]
        callContract = calls['Contract Name'][closest_j_calls]
        putContract = puts['Contract Name'][closest_j_puts]
        bestStrikePrices[i] = closest_strikePrice_calls
        callAskList[i] = callAsk
        putAskList[i] = putAsk
        bestCallContracts.append(callContract)
        bestPutContracts.append(putContract)
        #bestStrikePrices[i] = closest_strikePrice_calls
        #bestCallContracts[i] = callContract
        #bestPutContracts[i] = putContract

    else:
        warnings.warn("Call and put strike prices are not the same:\nCall = "
         + str(closest_strikePrice_calls) + "\nPut = " +
         str(closest_strikePrice_puts) + "\nskipping to next ticker...")
        bestStrikePrices[i] = np.nan
        callAskList[i] = np.nan
        putAskList[i] = np.nan
        #bestCallContracts[i] = 'N/A'
        #bestPutContracts[i] = 'N/A'
        bestCallContracts.append("N/A")
        bestPutContracts.append("N/A")

print("\n\nTickers")
print(tickers)
print("\nVolatilities: ")
print(volList)
print("\nBest Strike Prices: ")
print(bestStrikePrices)
print("\nBest Call Asking Prices: ")
print(callAskList)
print("\nBest Put Asking Prices: ")
print(putAskList)
print("\nBest Call Contracts: ")
print(bestCallContracts)
print("\nBest Put Contracts: ")
print(bestPutContracts)

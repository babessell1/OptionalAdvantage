from yahoo_fin.options import *
from yahoo_fin.stock_info import *
import matplotlib.pyplot as plt
import pandas as pd
from pandas.plotting import register_matplotlib_converters
import numpy as np
from datetime import date, datetime, timedelta
from project_methods.stockTools import *
import sys
import warnings


register_matplotlib_converters()
pd.set_option('display.max_columns', None)

################################################################################
################################################################################

# define tickers and timeFrame
tickers = ["MSFT", "AAPL"]
#tickers = ["MSFT"]
#startDate = "04/01/2019"
#currentDate = "04/01/2020"
startDate = 0
currentDate = 1000
timeFrame = [startDate, currentDate]
interestRate = 0.0013
compoundDivYield = 0

#declare list for volatility values
currentPriceList = np.zeros(shape=len(tickers))
volList = np.zeros(shape=len(tickers))
strikePriceList = np.zeros(shape=len(tickers))
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
    volatility, annu_volatility = calcVolatility(df_stock, ticker)
    volList[i] = volatility


    # find first expiration date above threshold
    ticker = tickers[i]
    num_of_days_threshold = 20
    expDate, days2expiration = findExpDate(ticker, num_of_days_threshold)
    print("Days until expiration: " + str(days2expiration))
    annu_days2expiration= days2expiration/365
    print("Annualized Days until expiration: " + str(annu_days2expiration))

    # find options
    optchain = get_options_chain(ticker, expDate)
    calls = optchain.get('calls')
    puts = optchain.get('puts')

    strikeList_calls = calls.Strike.to_numpy()
    strikeList_puts = puts.Strike.to_numpy()

    currentPrice = get_live_price(ticker)
    currentPriceList[i] = currentPrice

    # find put/call price closest to current stock price
    closest_j_calls = closest(strikeList_calls, currentPrice, 0)
    closest_j_puts = closest(strikeList_puts, currentPrice, 0)
    closest_strikePrice_calls = strikeList_calls[closest_j_calls]
    closest_strikePrice_puts = strikeList_puts[closest_j_puts]

    # verify that closest strike price for put and call is the same
    # if yes, update lists with useful price and contract information
    if closest_strikePrice_calls == closest_strikePrice_puts:
        print('Strike Price: ' + str(closest_strikePrice_calls))
        callAsk = calls['Ask'][closest_j_calls]
        print("Asking Call Price: " + str(callAsk))
        putAsk = puts['Ask'][closest_j_puts]
        print("Asking Put Price: " + str(putAsk))
        callContract = calls['Contract Name'][closest_j_calls]
        putContract = puts['Contract Name'][closest_j_puts]
        strikePriceList[i] = closest_strikePrice_calls
        callAskList[i] = callAsk
        putAskList[i] = putAsk
        bestCallContracts.append(callContract)
        bestPutContracts.append(putContract)
        # use Black-Shoal's Equation to find optimal put/call prices
        blackShoalsEqn(currentPrice, closest_strikePrice_calls, annu_volatility,
                        interestRate, compoundDivYield, annu_days2expiration)

    # if call/put prices do not match add nan values to list and skip to next ticker
    else:
        warnings.warn("Call and put strike prices are not the same:\nCall = "
         + str(closest_strikePrice_calls) + "\nPut = " +
         str(closest_strikePrice_puts) + "\nskipping to next ticker...")
        strikePriceList[i] = np.nan
        callAskList[i] = np.nan
        putAskList[i] = np.nan
        bestCallContracts.append("N/A")
        bestPutContracts.append("N/A")

# Print final lists
print("\n\nTickers")
print(tickers)
print("\nCurrent Stock Price: ")
print(currentPriceList)
print("\nVolatilities: ")
print(volList)
print("\nBest Strike Prices: ")
print(strikePriceList)
print("\nBest Call Asking Prices: ")
print(callAskList)
print("\nBest Put Asking Prices: ")
print(putAskList)
print("\nBest Call Contracts: ")
print(bestCallContracts)
print("\nBest Put Contracts: ")
print(bestPutContracts)

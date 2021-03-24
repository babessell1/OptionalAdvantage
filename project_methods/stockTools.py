from yahoo_fin.options import *
from yahoo_fin.stock_info import *
import matplotlib.pyplot as plt
import pandas as pd
from pandas.plotting import register_matplotlib_converters
import numpy as np
from datetime import date, datetime, timedelta
from math import *

register_matplotlib_converters()

################################################################################
################################################################################

def closest(lst, val, k):
        # list
        # value
        # kth nearest
        lst = np.asarray(lst)
        idx = (np.abs(lst - val)).argpartition(k)[k]
        return idx # returns index of closest value in the set

def pullStockData(timeFrame, ticker, printGraph):
    if timeFrame[0] != 0:
        startDate = timeFrame[0]
        currentDate = timeFrame[1]
    else:
        numDays = timeFrame[1]
        thisday = date.today()
        currentDate = thisday.strftime("%m/%d/%Y")
        startDate = (date.today()-timedelta(numDays)).strftime("%m/%d/%Y")

    df_stock = get_data(ticker, startDate, currentDate, index_as_date = False, interval='1d')

    if printGraph == True:
        plt.plot(df_stock.date, df_stock.close, '-r');
        plt.title(ticker)
        plt.xlabel("Date [year/month/day]")
        plt.ylabel("Adjusted Close Value [dollars]")
        plt.show()

    return df_stock

def calcVolatility(df, ticker):
    returns = []
    sampleSize = len(df.adjclose)
    for i, j in df.iterrows():
        if i > 0:
            this_return = 100*(df.adjclose[i] - df.adjclose[i-1])/df.adjclose[i-1]
            returns.append(this_return)
        else:
             returns.append(np.nan)
    returns = np.array(returns)
    #print(returns[1:])
    mean = np.mean(returns[1:])
    deviation_squared = [(r - mean)**2 for r in returns]
    deviation_squared_sum = np.sum(deviation_squared[1:])
    variance = deviation_squared_sum/(sampleSize-2)
    volatility = np.sqrt(variance)
    annu_volatility = volatility*np.sqrt(252)/100
    print("\n\n" + ticker)
    print("Sum of Deviation-Squared: " + str(deviation_squared_sum))
    print("Variance: " + str(variance))
    print("Volatility: " + str(volatility))
    print("Annualized Volatility: " + str(annu_volatility))

    return volatility, annu_volatility

def findExpDate(ticker, num_of_days_threshold):
    expDateList = get_expiration_dates(ticker)
    findDate = True
    i = 0
    while findDate:
        thisExpDate = expDateList[i]
        date_time_obj = datetime.strptime(thisExpDate, '%B %d, %Y')
        date_delta = date_time_obj - datetime.now()
        days2expiration = date_delta.days + 1

        if days2expiration < num_of_days_threshold:
            i += 1
        else:
            findDate = False

    expDate = expDateList[i]

    return expDate, days2expiration

def blackShoalsEqn(stockPrice, strikePrice, annu_volatility, interestRate,
                   compoundDivYield, annu_days2expiration):
    # ln(So/X)
    d_paramA = np.log(stockPrice/strikePrice)
    # t(r-q+v^2/2)
    d_paramB = annu_days2expiration*(interestRate-compoundDivYield+(annu_volatility**2)/2)
    # v*sqrt(t)
    d_paramC = annu_volatility*np.sqrt(annu_days2expiration)

    #print("A: " + str(d_paramA))
    #print("B: " + str(d_paramB))
    #print("C: " + str(d_paramC))

    # d1 = (A+B)/C
    d1 = (d_paramA + d_paramB)/d_paramC
    #d2 = d1-C
    d2 = d1 - d_paramC

    #print("d1: " + str(d1))
    #print("d2: " + str(d2))

    # Cumulative normal standard distribution
    def cum_norm_std_dist(d):
        N = (1 + erf(d/sqrt(2))) / 2
        return N

    N_d1 = cum_norm_std_dist(d1)
    N_d2 = cum_norm_std_dist(d2)
    N_neg_d1 = cum_norm_std_dist(-d1)
    N_neg_d2 = cum_norm_std_dist(-d2)

    #print("N(d1):" + str(N_d1))
    #print("N(d2):" + str(N_d2))
    #print("N(-d1):" + str(N_neg_d1))
    #print("N(-d2):" + str(N_neg_d2))

    exp_neg_qt = np.exp(-compoundDivYield*annu_days2expiration)
    exp_neg_rt = np.exp(-interestRate*annu_days2expiration)

    #print("exp(-qt): " + str(exp_neg_qt))
    #print("exp(-rt): " + str(exp_neg_rt))

    calculated_call = (stockPrice*exp_neg_qt*N_d1)-(strikePrice*exp_neg_rt*N_d2)
    calculated_put = (strikePrice*exp_neg_rt*N_neg_d2)-(stockPrice*exp_neg_qt*N_neg_d1)

    print("Calculated Call: " + str(calculated_call))
    print("Calculated Put: " + str(calculated_put))

    return

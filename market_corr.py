


import os
path = ""
os.chdir(path)

from function import get_quandl_data, merge_dfs_on_column, get_json_data, correlation_heatmap

import numpy as np
import pandas as pd
from datetime import datetime
import matplotlib.pylab as plt
import plotly.offline as py
py.init_notebook_mode(connected=True)

#We download our data from Quandl
#=================================


exchanges = ['COINBASE','BITSTAMP', 'BITFINEX', 'KRAKEN']

exchange_data = {}

for exchange in exchanges : 
    exchange_code = 'BCHARTS/{}USD'.format(exchange)
    btc_exchange_df = get_quandl_data(exchange_code)
    exchange_data[exchange] = btc_exchange_df
    
btc_usd_datasets = merge_dfs_on_column(list(exchange_data.values()),list(exchange_data.keys()), 'Weighted Price')

btc_usd_datasets.replace(0 , np.nan, inplace= True) #We replace the null values by Nan


#We plot our datas 
#==================


plt.close('all')
fig, ax =plt.subplots(1)
ax.plot(btc_usd_datasets['KRAKEN'], 'b', lw = 1.5, label = 'KRAKEN')
ax.plot(btc_usd_datasets['COINBASE'], 'r', lw = 1.5, label = 'COINBASE')
ax.plot(btc_usd_datasets['BITSTAMP'], 'grey', lw = 1.5, label = 'BITSTAMP')
ax.plot(btc_usd_datasets['BITFINEX'], 'yellow', lw = 1.5, label = 'KRAKEN')

fig.autofmt_xdate()
plt.title('Historic of BTC price (2012 - 2018)')
plt.legend(loc=0)
plt.grid(True)
plt.ylabel('prices ($)')
plt.xlabel('dates')
plt.show()

#Calculate the mean of exchange BTC prices
#=========================================


btc_usd_datasets['average_exchange_price'] = btc_usd_datasets.mean(axis=1) 


#Plot of the average BTC price 
#=============================

plt.close('all')
fig, ax =plt.subplots(1)
ax.plot(btc_usd_datasets['average_exchange_price'], 'b', lw = 1.5, label = 'average BTC price')
fig.autofmt_xdate()
plt.title('Historic of BTC price (2012 - 2018)')
plt.legend(loc=0)
plt.grid(True)
plt.ylabel('prices ($)')
plt.xlabel('dates')
plt.savefig('avg_btc_price.pdf')
plt.show()

btc_returns_df = pd.DataFrame(index = btc_usd_datasets.index)
btc_returns_df['BTC_price'] =  btc_usd_datasets['average_exchange_price']
btc_returns_df['BTC_returns'] = btc_returns_df['BTC_price'].pct_change()

# Poloniex Helper functions 
#===========================


# This function download and cache JSON data from a provided URL
  
base_polo_url = 'https://poloniex.com/public?command=returnChartData&currencyPair={}&start={}&end={}&period={}'
start_date = datetime.strptime('2015-01-01', '%Y-%m-%d') # get data from the start of 2015
end_date = datetime.now() # up until today
pediod = 86400 # pull daily data (86,400 seconds per day)


def get_crypto_data(poloniex_pair):
    '''Retrieve cryptocurrency data from poloniex'''
    json_url = base_polo_url.format(poloniex_pair, start_date.timestamp(), end_date.timestamp(), pediod)
    data_df = get_json_data(json_url, poloniex_pair)
    data_df = data_df.set_index('date')
    return data_df


altcoins = ['ETH','LTC','XRP','ETC','STR','DASH','SC']

altcoin_data = {}
for altcoin in altcoins:
    coinpair = 'BTC_{}'.format(altcoin)
    crypto_price_df = get_crypto_data(coinpair)
    altcoin_data[altcoin] = crypto_price_df


for altcoin in altcoin_data.keys():
    altcoin_data[altcoin]['price_usd'] =  altcoin_data[altcoin]['weightedAverage'] * btc_usd_datasets['average_exchange_price']


combined_df = merge_dfs_on_column(list(altcoin_data.values()), list(altcoin_data.keys()), 
                                  'price_usd')

combined_df['Bitcoin'] = btc_usd_datasets['average_exchange_price'][btc_usd_datasets['average_exchange_price'].index.year >= 2015]

#Focus on 2016
#=============

combined_df_2016 = combined_df[combined_df.index.year == 2016]
combined_df_2016.pct_change().corr(method= 'pearson')


correlation_heatmap(combined_df_2016.pct_change(), "Cryptocurrency Correlations in 2016")

#Focus on 2017
#=============


combined_df_2017 = combined_df[combined_df.index.year == 2017]
combined_df_2017.pct_change().corr(method= 'pearson')


correlation_heatmap(combined_df_2017.pct_change(), "Cryptocurrency Correlations in 2017")

#Focus on 2018
#=============


combined_df_2018 = combined_df[combined_df.index.year == 2018]
combined_df_2018.pct_change().corr(method= 'pearson')


correlation_heatmap(combined_df_2018.pct_change(), "Cryptocurrency Correlations in 2018")

#Period 2016 - 2018
#==================

combined_df_All = combined_df[combined_df.index.year >= 2016]
combined_df_All.pct_change().corr(method = 'pearson')

correlation_heatmap(combined_df.pct_change().corr(method = 'pearson'), "Cryptocurrency Correlations on the 2016 - 2018 period")



#Plot of BTC and altcoin prices 
#=============================== 

fig, ax1 = plt.subplots()
ax2 = ax1.twinx()
ax1.plot(btc_usd_datasets['average_exchange_price'], 'r', lw = 1.5, label = 'BTC')
ax1.set_ylabel('BTC price ($)', color='firebrick')
ax1.tick_params('y', colors='firebrick')
ax2.plot(combined_df['ETH'], 'gainsboro', lw = 1.5, label = 'ETH')
ax2.plot(combined_df['LTC'], 'darkseagreen', lw = 1.5, label = 'LTC')
ax2.plot(combined_df['DASH'], 'lightblue', lw = 1.5, label = 'DASH')
ax2.set_ylabel('Altcoin price ($)', color='green')
ax2.tick_params('y', colors='green')
plt.grid(True)
plt.title('BTC and Alt prices for the period 2012 - 2018')
fig.autofmt_xdate()
fig.tight_layout()
plt.savefig("BTC_Alt prices (2012-2018)")
plt.show()


import ccxt
import pandas as pd
import numpy as np

TICKERS = []

class CryptoSignal:
	def __init__(self)
		pass

	def find_ath(self, exchange, ticker):
		data = self.get_data(exchange, ticker)[2]
		ath = data.max(axis=0)
		idx = data.idxmax(axis=0)
		date = pd.to_datetime(idx*1000000)
		
		print(ath)
		print(idx)
		print(date)
		return ath, date


	def get_data(self, exchange, ticker):
		exchange = getattr(ccxt, exchange)({'enableRateLimit': True})
		data = []
		count = 0
		since = 0
		interval = '1d'
		while True:
			d2 = exchange.fetch_ohlcv(ticker, interval, since)
			data += d2
			count += 1
			if len(d2) <= 1:
				break
			else:
				since = d2[-1][0]
		df = pd.DataFrame(data)
		df.drop_duplicates(subset=0, inplace=True)
		df.name = ticker + '_' + exchange.id + '_' + interval
		df.set_index(0, inplace=True)
		return df

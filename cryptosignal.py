import ccxt
import csv
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import pandas as pd
import smtplib
from tabulate import tabulate
import yagmail
import time


TICKERS = []

class CryptoSignal:
	def __init__(self)
		pass
	
	def set_exchange(self):
		exchange_name = input('Enter exchange name:')
		self.exchange = getattr(ccxt, exchange_name)({'enableRateLimit': True})

	def find_ath(self, ticker):
		data = self.get_data(ticker)[2]
		ath = data.max(axis=0)
		idx = data.idxmax(axis=0)
		date = pd.to_datetime(idx*1000000)
		today = datetime.datetime.today()
		delta = today - date
		
		return ath, idx, date, delta


	def get_data(self, ticker):
		data = []
		count = 0
		since = 0
		interval = '1d'
		while True:
			d2 = self.exchange.fetch_ohlcv(ticker, interval, since)
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


	@staticmethod
	def send_email(file_path = 'email_signal.csv'):
		me = ''
		password = ''
		server = 'smtp.gmail.com:587'
		you = 'salexo44@gmail.com'

		text = """
		List of cryptocurrencies, which are close to all time highs:

		{table}

		Regards."""

		html = """
		<html><body><p>List of cryptocurrencies, which are close to all time highs:</p>
		{table}
		<p>Regards.</p>
		</body></html>
		"""

		with open(file_path) as input_file:
			reader = csv.reader(input_file)
			data = list(reader)

		text = text.format(table=tabulate(data, headers="firstrow", tablefmt="grid"))
		html = html.format(table=tabulate(data, headers="firstrow", tablefmt="html"))

		message = MIMEMultipart(
			"alternative", None, [MIMEText(text), MIMEText(html, 'html')])

		message['Subject'] = "Your data"
		message['From'] = me
		message['To'] = you
		server = smtplib.SMTP(server)
		server.ehlo()
		server.starttls()
		server.login(me, password)
		server.sendmail(me, you, message.as_string())
		server.quit()
		
		
	def monitor_ticker(self, ticker, sleep_time=120):
		ath, ath_timestamp, ath_date, delta = self.find_ath(ticker)
		while True:
			data = self.exchange.fetch_ticker(ticker)
			if data['bid'] > ath and data['timestamp'] - ath_timestamp > 86400000:
				self.send_email2({'ticker': ticker, 'price': data['bid'], 'ath': ath, 'ath_date': ath_date})
				break
			else:
				time.sleep(sleep_time)
				
	def send_email2(self, data):
		today = datetime.datetime.today()
		msg = f"""
		Ticker: {data['ticker']}
		Current price: {data['price']}
		Previous ATH: {data['ath']}
		Previous ATH date: {data['ath_date']}
		Todays date: {str(today)[:-7]}
		"""

		subject = f"New high on {data['ticker']}: {data['price']}"
		for recipient in self.config['Recipients']:
			self.server.send(to=recipient, subject=subject, contents=msg)
			print(f'msg sent to {recipient}')


	def register_email(self):
		user = input('Email:')
		password = input('Password:')
		yagmail.register(user, password)

	def add_recipient(self, email):
		with open('config.cfg', 'r+') as config:
			self.config = json.load(config)
			self.config['Recipients'].append(email)
			js = json.dumps(self.config)
			config.seek(0)
			config.write(js)
			config.truncate()

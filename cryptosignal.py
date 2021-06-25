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
		today = datetime.datetime.today()
		delta = today - date
		
		print(ath)
		print(idx)
		print(date)
		print(delta)
		return ath, date, delta


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


	@staticmethod
    def send_email(file_path = 'email_signal.csv'):
        me = 'jacek.dzarnecki@gmail.com'
        password = 'Jacek11@@'
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

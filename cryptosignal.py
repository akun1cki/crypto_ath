import ccxt
import pandas as pd
import yagmail
import time
import yaml
import datetime


class CryptoSignal:
    def __init__(self, password):
        self.config = None
        self.load_config()
        self.exchange = getattr(ccxt, self.config['exchange'])({'enableRateLimit': True})
        yagmail.register(self.config['email'], password)

        self.monitor_tickers(tickers=self.config['tickers'], pct_of_ath=self.config['pct_of_ath'],
                             sleep_time=self.config['sleep_time'], reset_peroid=self.config['reset_peroid'])

    def load_config(self):
        with open('config.yaml', 'r') as config:
            self.config = yaml.safe_load(config)

    def find_ath(self, ticker):
        data = self.get_data(ticker)[2]
        ath = data.max(axis=0)
        date = data.idxmax(axis=0)
        return ath, date

    def get_data(self, ticker):
        data = []
        since = 0
        interval = '1d'
        while True:
            d2 = self.exchange.fetch_ohlcv(ticker, interval, since)
            data += d2
            if len(d2) <= 1:
                break
            else:
                since = d2[-1][0]
        df = pd.DataFrame(data)
        df.drop_duplicates(subset=0, inplace=True)
        df.name = ticker + '_' + self.exchange.id + '_' + interval
        df.set_index(0, inplace=True)
        return df

    '''
    @staticmethod
    def send_email(file_path='email_signal.csv'):
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
    '''

    def monitor_tickers(self, tickers, pct_of_ath, sleep_time, reset_peroid):
        ath_data = {}
        try:
            email_history = pd.read_csv('email_signal.csv', index_col=None)
        except:
            email_history = pd.DataFrame(columns='timestamp symbol price prev_ath prev_ath_date delta'.split())

        for ticker in tickers:
            last_msg_timestamp = max(email_history[email_history['symbol'] == ticker]['symbol']) if ticker in \
                                                                                                    email_history[
                                                                                                        'symbol'] else 0
            ath, ath_date = self.find_ath(ticker)
            ath_data[ticker] = {'ath': ath, 'ath_date': max(last_msg_timestamp, ath_date)}

        while True:
            to_send = []
            data = pd.DataFrame(self.exchange.fetch_tickers(tickers)).transpose()[['symbol', 'timestamp', 'last']]
            for ticker in tickers:
                if self.close_to_ath(ath_data[ticker]['ath'], data.loc[ticker, 'last'],
                                     pct_of_ath) and self.check_dates(data.loc[ticker, 'timestamp'],
                                                                      ath_data[ticker]['ath_date'], reset_peroid):
                    to_send.append({'symbol': ticker, 'price': data.loc[ticker, 'last'], 'ath': ath_data[ticker]['ath'],
                                    'ath_date': ath_data[ticker]['ath_date'],
                                    'delta': data.loc[ticker, 'timestamp'] - ath_data[ticker]['ath_date']})

            if to_send:
                email_history.loc[len(email_history)] = [data.loc[ticker, 'timestamp'], ticker,
                                                         data.loc[ticker, 'last'],
                                                         ath_data[ticker]['ath'], ath_data[ticker]['ath_date'],
                                                         data.loc[ticker, 'timestamp'] - ath_data[ticker]['ath_date']]

                email_history.to_csv('email_signal.csv', index=False)
                self.send_emails(to_send)

            time.sleep(sleep_time)

    @staticmethod
    def close_to_ath(ath, current_price, pct_of_ath):
        return current_price >= ath * pct_of_ath

    @staticmethod
    def check_dates(current_timestamp, last_msg_timestamp, reset_peroid):
        return current_timestamp - last_msg_timestamp > reset_peroid

    @staticmethod
    def miliseconds_to_days(time_in_ms):
        return time_in_ms / 86_400_000

    def send_emails(self, data):
        yag = yagmail.SMTP(self.config['email'])
        today = datetime.datetime.today()
        for item in data:
            subject = f"New high on {item['symbol']}: {item['price']}"
            msg = f"""
                    Ticker: {item['symbol']}.
                    Current price: {item['price']}.
                    Previous ATH: {item['ath']}.
                    Previous ATH date: {ccxt.Exchange.iso8601(item['ath_date'])[:10]} --*
                                       {self.miliseconds_to_days(item['delta'])} days ago.
                    Todays date: {str(today)[:-7]}.
                    """

            for recipient in self.config['recipients']:
                yag.send(to=recipient, subject=subject, contents=msg)
                print(f'msg sent to {recipient}')


if __name__ == "__main__":
    import sys
    sys.exit(CryptoSignal(sys.argv[1]))


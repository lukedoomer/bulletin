import pandas
import plotly.graph_objects as go
from binance import Client
from tempfile import NamedTemporaryFile
from PIL import Image

class crypto:

    @staticmethod
    def get_price(api_key, api_secret, pair):
        client = Client(api_key, api_secret)
        ticker = client.get_symbol_ticker(symbol=pair)
        return float(ticker['price'])

    @staticmethod
    def update_candles(api_key, api_secret, pairs):
        client = Client(api_key, api_secret)

        charts = dict()

        for pair in pairs:
            klines = client.get_historical_klines(pair, Client.KLINE_INTERVAL_1HOUR, "24 hours ago UTC")
            data = pandas.DataFrame(klines, columns = ['timestamp', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'quote_av', 'trades', 'tb_base_av', 'tb_quote_av', 'ignore' ])
            data = data.apply(pandas.to_numeric)

            fig = go.Figure(data=[go.Candlestick(
                x=pandas.to_datetime(data['timestamp'], unit='ms'),
                open=data['open'],
                high=data['high'],
                low=data['low'],
                close=data['close'])])

            price = crypto.get_price(api_key, api_secret, pair)
            fig.update_layout(title='<b>{}    {:.3f}</b>'.format(pair, price), titlefont_color='#FFFFFF', titlefont_size=58, title_x=0.5)
            fig.update_layout(paper_bgcolor='#000000', plot_bgcolor='#000000')
            fig.update_layout(xaxis_rangeslider_visible=False)
            fig.update_xaxes(gridcolor='rgb(160, 160, 160)', color='#FFFFFF', tickfont_size=28, gridwidth=2, tickformat='%H:%M')
            fig.update_yaxes(gridcolor='rgb(160, 160, 160)', color='#FFFFFF', tickfont_size=28, gridwidth=2)

            file = NamedTemporaryFile()
            fig.write_image(file.name, format='png')
            charts[pair] = Image.open(file.name)

        return charts
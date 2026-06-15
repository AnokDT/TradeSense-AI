import yfinance as yf

def get_btc_data():
    btc = yf.download(
        "BTC-USD",
        period="5y",
        interval="1d",
        auto_adjust=True
    )

    return btc
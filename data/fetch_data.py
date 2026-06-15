import yfinance as yf

def get_crypto_data(symbol: str, period: str = "5y", interval: str = "1d"):
    """
    Downloads historical daily price data for a given cryptocurrency symbol.
    """
    data = yf.download(
        symbol,
        period=period,
        interval=interval,
        auto_adjust=True
    )
    return data

def get_btc_data():
    return get_crypto_data("BTC-USD")
from data.fetch_data import get_btc_data

btc = get_btc_data()

print()
print("Last 5 rows:")
print(btc.tail())
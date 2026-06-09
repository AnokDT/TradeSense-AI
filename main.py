print("=" * 40)
print("         TradeSense AI")
print("=" * 40)

bull_score = 0
bear_score = 0

ema50 = 65000
ema200 = 62000

rsi = 65

volume_high = True

if ema50 > ema200:
    bull_score += 30
else:
    bear_score += 30

if rsi > 60:
    bull_score += 20

if volume_high:
    bull_score += 20

print(f"Bull Score: {bull_score}")
print(f"Bear Score: {bear_score}")

if bull_score > bear_score:
    print("Action: BUY")
elif bear_score > bull_score:
    print("Action: SELL")
else:
    print("Action: WAIT")
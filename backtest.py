import json
import time
import datetime
import pandas as pd
import scipy
import scipy.stats
import numpy as np
import matplotlib.pyplot as plt
from scipy.spatial.distance import correlation

df = pd.read_csv("Candle/candle900.csv")
csv_candle_list = df.values.tolist()


term = 4
spread = 1000
volatility_number = 1.6
start_timestamp = 1517443200
end_timestamp = 1525132800
candle_list = [k for k in csv_candle_list if start_timestamp < k[1] <= end_timestamp]

position = 0
order_state = False
candle_900_list = []
candle_7200_list = []
result_list = []
csv_list = [0]

for i in candle_list:
	candle_900_list.append(i)

	#900*8=7200 2時間
	if len(candle_900_list) == 8:
		time = candle_900_list[-1][1]
		open = candle_900_list[0][2]
		high = max([k[3] for k in candle_900_list])
		low = min([k[4] for k in candle_900_list])
		close = candle_900_list[-1][5]
		new_candle = [time, open, high, low, close]

		if len(candle_7200_list) < term:
			candle_7200_list.append(new_candle)

		elif len(candle_7200_list) == term:
			order_state = True
			candle_7200_list = candle_7200_list[1:] + [new_candle]
			volatility = sum([k[2]-k[3] for k in candle_7200_list])/term
			high_price = new_candle[-1] + volatility*volatility_number
			low_price = new_candle[-1] - volatility*volatility_number

		candle_900_list = []

	if order_state:
		#print(high_price)
		if position == 0:
			if i[3] > high_price:
				buy_price = high_price + spread
				position = 1
			elif i[4] < low_price:
				sell_price = low_price - spread
				position = -1

		elif position == 1:
			if i[4] < low_price:
				sell_price = low_price - spread
				result = sell_price - buy_price
				result_list.append([result,i[1]])
				position = -1
				csv_list.append(csv_list[-1]+result)

		elif position == -1:
			if i[3] > high_price:
				buy_price = high_price + spread
				result = sell_price - buy_price
				result_list.append([result,i[1]])
				position = 1
				csv_list.append(csv_list[-1]+result)


date_open = datetime.datetime.fromtimestamp(start_timestamp)
date_close = datetime.datetime.fromtimestamp(end_timestamp)
print("===========================================")
print(str(date_open) + " ～ " + str(date_close), end="\n\n")

result_list = [i[0] for i in result_list]
df_result = pd.DataFrame(result_list)

winTrade = sum([1 for i in result_list if i > 0])
loseTrade = sum([1 for i in result_list if i < 0])
winPer = round(winTrade/(winTrade+loseTrade)*100, 2)
winTotal = sum([i for i in result_list if i > 0])
loseTotal = sum([i for i in result_list if i < 0])

if loseTotal == 0:
	profitFactor = None
else:
	profitFactor = round(winTotal/-loseTotal, 3)
Total = winTotal+loseTotal
maxProfit = max(result_list)
maxLoss = min(result_list)
trade_number = winTrade + loseTrade

if loseTotal == 0 or winTrade == 0:
	risk_reward = None
else:
	risk_reward = round((sum([i for i in result_list if i > 0])/winTrade)/(-sum([i for i in result_list if i < 0])/loseTrade),3)

average = df_result.mean().values[0]
deviation = df_result.std().values[0]
SR = df_result.mean().values[0]/df_result.std().values[0]
skewness = df_result.skew().values[0]

print("term : {}".format(term))
print("Total pl: {}JPY".format(winTotal+loseTotal))
print("The number of Trades: {}".format(trade_number))
print("average: {}".format(average))
print("deviation: {}".format(deviation))
print("SR :{}".format(SR))
print("skewness: {}".format(skewness))
print("The Winning percentage: {}%".format(winPer))
print("The profitFactor: {}".format(profitFactor))
print("The Risk/Reward: {}".format(risk_reward))
print("The maximum Profit and Loss: {}JPY, {}JPY".format(int(maxProfit), int(maxLoss)))

result_df = pd.DataFrame(csv_list)
result_df.to_csv("Candle/result.csv")

import config, csv
import calendar
from binance.client import Client

client = Client(config.API_KEY, config.API_SECRET)

cyear = 2022
cmonth = 1
nyear = 2023
nmonth : 4

while cyear >= 2017:
    if cmonth + 3 > 12:
        nyear = cyear +1
        nmonth = 1
    else :
        nyear = cyear
        nmonth = cmonth + 3
    tm = 'BTCUSDT-'+ str(cyear) + str(cmonth) +'01-' + str(nyear) + str(nmonth)+ '01-1min.csv'
    print("csv is:",tm)
    csvfile = open('cand/'+tm, 'w', newline='')
    candlestick_writer = csv.writer(csvfile, delimiter=',')

    stDate = "01 "+calendar.month_abbr[cmonth]+", "+str(cyear)
    endDate = "01 "+calendar.month_abbr[nmonth]+", "+str(nyear)
    print("start time is:",stDate," end time is:",endDate)
    candlesticks = client.get_historical_klines("BTCUSDT", Client.KLINE_INTERVAL_1MINUTE, stDate, endDate)

    print(len(candlesticks))

    cnt = 0

    for candlestick in candlesticks:
        candlestick[0] = candlestick[0] / 1000 # divide timestamp to ignore miliseconds
        candlestick_writer.writerow(candlestick)
        cnt += 1
        if cnt % 100 == 0:
            print(str(cyear)+"'s "+str(cnt))

    csvfile.close()
    if cmonth > 1:
        cmonth -= 3
    else :
        cyear -= 1
        cmonth = 10

import backtest, csv, os 
from config import *

commission_val = 0.04 # 0.04% taker fees binance usdt futures
portofolio = 10000.0 # amount of money we start with
stake_val = 1
stdcoefMin =  0.0
stdcoefMax =  2.0

start = '2017-01-01'
end = '2020-12-31'
periodRange = range(10, 31)
plot = True

def trainParameters():
    if strategy == stList['btgh']:
        
        pass
    else:
        stdcoef = stdcoefMin 
        for period in periodRange:
            while stdcoef < stdcoefMax:
                end_val, totalwin, totalloss, pnl_net, sqn = backtest.runbacktest(
                    datapath, start, end, period, strategy,                 #
                    commission_val, portofolio, stake_val, stdcoef, plot)  #
                profit = (pnl_net / portofolio) * 100

                # view the data in the console while processing
                print('data processed: %s, %s (Period %d) --- Ending Value: %.2f --- Total win/loss %d/%d, SQN %.2f' % (datapath[5:], strategy, period, end_val, totalwin, totalloss, sqn))

                result_writer.writerow([sep[0], sep[3] , start, end, strategy, period, round(end_val,3), round(profit,3), totalwin, totalloss, sqn])

                stdcoef += 0.2


for strategy in stList.values():

    for data in os.listdir("./cand"):

        datapath = 'cand/' + data
        sep = datapath[5:-4].split(sep='-') # ignore name file 'data/' and '.csv'
        # sep[0] = pair; sep[1] = year start; sep[2] = year end; sep[3] = timeframe

        print('\n ------------ ', datapath)
        print()

        start = sep[1]
        end = sep[2]

        dataname = 'result/{}-{}-{}-{}-{}.csv'.format(strategy, sep[0], sep[1],sep[2], sep[3])
        print("dataname is",dataname)
        csvfile = open(dataname, 'w', newline='')
        result_writer = csv.writer(csvfile, delimiter=',')

        result_writer.writerow(['Pair', 'Timeframe', 'Start', 'End', 'Strategy', 'Period', 'Final value', '%', 'Total win', 'Total loss', 'SQN']) # init header


        trainParameters()

        csvfile.close()
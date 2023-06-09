import backtest, csv, os 
from config import *

commission_val = 0.04 # 0.04% taker fees binance usdt futures
portofolio = 10000.0 # amount of money we start with
stake_val = 1
leverage = 20.0

start = '2017-01-01'
end = '2020-12-31'
plot = False

class ParameterRange:
    def __init__(self, name, start, stop, step):
        self.name  = name
        self.start = start
        self.stop  = stop
        self.step  = step

    def next(self,param_curList,index):

        # add step
        param_current = param_curList[index]+self.step

        if param_current <= self.stop :
            param_curList[index] = param_current
            return True
        else :
            # return the start value
            param_curList[index] = self.start
            return False

param_ranges = [
    ParameterRange('stdcoef', 0.0, 2.0, 0.2),
    ParameterRange('inquantity', 0.05, 0.2, 0.01),
    ParameterRange('period', 10, 31, 1),
    ParameterRange('outquantity', 0.1, 0.1, 0.011),
]

def generate_nextValue(param_List,param_curList):

    for index,param in reversed(list(enumerate(param_List))):
        if param.next(param_curList,index) :
            break
        if index == 0 :
            generate_nextValue.end = True

    return param_curList

def init_values(param_List,param_curList):

    for index,value in list(enumerate(param_List)):
        param_curList[index] = value.start
    return param_curList

def findNextParameters():

    return

def trainParameters():
    if strategy == stList['btgh']:
        param_curList = [0] * len(param_ranges)
        stdcoef, inquantity, period, outquantity = init_values(param_ranges,param_curList)
        generate_nextValue.end = False
        
        while generate_nextValue.end !=  True :
            end_val, totalwin, totalloss, pnl_net, sqn = backtest.runbacktest(
                datapath, start, end, strategy,
                period, stdcoef, inquantity, outquantity,
                commission_val,leverage, portofolio, stake_val, plot)  #
            profit = (pnl_net / portofolio) * 100


            # view the data in the console while processing
            print('data processed: %s, %s (Period %d) --- Ending Value: %.2f --- Total win/loss %d/%d, SQN %.2f' % (datapath[5:], strategy, period, end_val, totalwin, totalloss, sqn))

            result_writer.writerow([sep[0], sep[3] , start, end, strategy, period, round(end_val,3), round(profit,3), totalwin, totalloss, sqn])
            stdcoef, inquantity, period,  outquantity = generate_nextValue(param_ranges,param_curList)

    else:
        pass
        

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
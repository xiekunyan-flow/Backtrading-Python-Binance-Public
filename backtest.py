from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import datetime  # For datetime objects
import backtrader as bt # Import the backtrader platfor
from config import *


# Create a indicators
class IndBreakout(bt.Indicator): 
    # Breakout indicator now it is calculate by standard deviation 
    # and range.
    lines = ('flurange','longTrade','shortTrade', ) # 最后一个 “,” 别省略
    params = (('period',90),('stdcoef',90),) # 最后一个 “,” 别省略
    
    def __init__(self):
        '''可选'''
        print("use Breakout indicator,period is ",self.p.period)
        self.addminperiod(self.params.period) # Discard the time less than period
        the_highest_period = bt.ind.Highest(self.data.high, period=self.params.period)
        the_lowest_period  = bt.ind.Lowest(self.data.low, period=self.params.period)
        the_standard_deviation_period = bt.ind.StandardDeviation(self.data, period=self.params.period)
        self.l.flurange = the_highest_period - the_lowest_period
        self.l.longTrade = the_highest_period + self.p.stdcoef * the_standard_deviation_period
        self.l.shortTrade = the_lowest_period - self.p.stdcoef * the_standard_deviation_period
        # self.plotinfo = dict(subplot=False, plotname='My Indicator', plot=True,
        #             color='blue', linestyle='dashed', linewidth=2)
        pass
    
    def next(self):
        pass
    
    
# Create a Stratey
class BTCBreakoutStrategy(bt.Strategy):

    params = (
        ('maperiod', None),
        ('stdcoef', None), #a1
        ('inquantity', None), #a2
        # ('outquantity', None), #a2
    )


    def __init__(self):
        # Keep a reference to the "close" line in the data[0] dataseries
        self.dataclose = self.datas[0].close
        # To keep track of pending orders and buy price/commission
        self.order = None
        self.buyprice = None
        self.buycomm = None
        self.amount = None
        self.direction = None

        # Add a MovingAverageSimple indicator
        self.ind = IndBreakout(self.datas[0], period=self.params.maperiod,stdcoef=self.params.stdcoef)


    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            # Buy/Sell order submitted/accepted to/by broker - Nothing to do
            return

        # Check if an order has been completed
        # Attention: broker could reject order if not enough cash
        if order.status in [order.Completed]:
            if order.isbuy():
                self.buyprice = order.executed.price
                self.buycomm = order.executed.comm

        self.order = None

    def next(self):

        # Check if an order is pending ... if yes, we cannot send a 2nd one
        if self.order:
            return

        # Check if we are in the market
        if not self.position:

            # Not yet ... we MIGHT BUY if ...
            if self.dataclose[0] > self.ind.l.longTrade :
                self.amount = (self.broker.getvalue() * self.param.inquantity / self.ind.l.flurange) / self.dataclose[0]
                self.order = self.buy(size=self.amount)
                self.direction = "L"  

            elif self.dataclose[0] < self.ind.l.shortTrade:

                # Keep track of the created order to avoid a 2nd order
                self.amount = (self.broker.getvalue() * self.param.inquantity / self.ind.l.flurange) / self.dataclose[0]
                self.order = self.sell(size=self.amount)
                self.direction = "S"
        else:
            # Already in the market ... we might sell
            if self.direction == "S" and self.dataclose[0] > self.ind.l.longTrade :
                self.order = self.buy(size=self.amount)  
                self.direction = None

            elif self.direction == "L" and self.dataclose[0] < self.ind.l.shortTrade:

                self.order = self.sell(size=self.amount)
                self.direction = None

class SMAStrategy(bt.Strategy):

    params = (
        ('maperiod', None),
        ('quantity', None)
    )


    def __init__(self):
        # Keep a reference to the "close" line in the data[0] dataseries
        self.dataclose = self.datas[0].close

        # To keep track of pending orders and buy price/commission
        self.order = None
        self.buyprice = None
        self.buycomm = None
        self.amount = None

        # Add a MovingAverageSimple indicator
        self.sma = bt.ind.SimpleMovingAverage(self.datas[0], period=self.params.maperiod)


    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            # Buy/Sell order submitted/accepted to/by broker - Nothing to do
            return

        # Check if an order has been completed
        # Attention: broker could reject order if not enough cash
        if order.status in [order.Completed]:
            if order.isbuy():
                self.buyprice = order.executed.price
                self.buycomm = order.executed.comm

        self.order = None


    def next(self):

        # Check if an order is pending ... if yes, we cannot send a 2nd one
        if self.order:
            return

        # Check if we are in the market
        if not self.position:

            # Not yet ... we MIGHT BUY if ...
            if self.dataclose[0] > self.sma[0]:

                # Keep track of the created order to avoid a 2nd order
                self.amount = (self.broker.getvalue() * self.params.quantity) / self.dataclose[0]
                self.order = self.buy(size=self.amount)
        else:
            # Already in the market ... we might sell
            if self.dataclose[0] < self.sma[0]:

                # Keep track of the created order to avoid a 2nd order
                self.order = self.sell(size=self.amount)

class RSIStrategy(bt.Strategy):

    params = (
        ('maperiod', None),
        ('quantity', None)
    )


    def __init__(self):
        # Keep a reference to the "close" line in the data[0] dataseries
        self.dataclose = self.datas[0].close

        # To keep track of pending orders and buy price/commission
        self.order = None
        self.buyprice = None
        self.buycomm = None
        self.amount = None

        # Add a MovingAverageSimple indicator
        self.rsi = bt.talib.RSI(self.datas[0], timeperiod=self.params.maperiod)


    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            # Buy/Sell order submitted/accepted to/by broker - Nothing to do
            return

        # Check if an order has been completed
        # Attention: broker could reject order if not enough cash
        if order.status in [order.Completed]:
            if order.isbuy():
                self.buyprice = order.executed.price
                self.buycomm = order.executed.comm

        self.order = None


    def next(self):

        # Check if an order is pending ... if yes, we cannot send a 2nd one
        if self.order:
            return

        # Check if we are in the market
        if not self.position:

            # Not yet ... we MIGHT BUY if ...
            if self.rsi < 30:

                # Keep track of the created order to avoid a 2nd order
                self.amount = (self.broker.getvalue() * self.params.quantity) / self.dataclose[0]
                self.order = self.buy(size=self.amount)
        else:
            # Already in the market ... we might sell
            if self.rsi > 70:

                # Keep track of the created order to avoid a 2nd order
                self.order = self.sell(size=self.amount)
                

# ______________________ End Strategy Class



def timeFrame(datapath):
    """
    Select the write compression and timeframe.
    """
    sepdatapath = datapath[5:-4].split(sep='-') # ignore name file 'data/' and '.csv'
    tf = sepdatapath[3]

    if tf == '1mth':
        compression = 1
        timeframe = bt.TimeFrame.Months
    elif tf == '12h':
        compression = 720
        timeframe = bt.TimeFrame.Minutes
    elif tf == '15m':
        compression = 15
        timeframe = bt.TimeFrame.Minutes
    elif tf == '30m':
        compression = 30
        timeframe = bt.TimeFrame.Minutes
    elif tf == '1d':
        compression = 1
        timeframe = bt.TimeFrame.Days
    elif tf == '1h':
        compression = 60
        timeframe = bt.TimeFrame.Minutes
    elif tf == '3m':
        compression = 3
        timeframe = bt.TimeFrame.Minutes
    elif tf == '2h':
        compression = 120
        timeframe = bt.TimeFrame.Minutes
    elif tf == '3d':
        compression = 3
        timeframe = bt.TimeFrame.Days
    elif tf == '1w':
        compression = 1
        timeframe = bt.TimeFrame.Weeks
    elif tf == '4h':
        compression = 240
        timeframe = bt.TimeFrame.Minutes
    elif tf == '5m':
        compression = 5
        timeframe = bt.TimeFrame.Minutes
    elif tf == '6h':
        compression = 360
        timeframe = bt.TimeFrame.Minutes
    elif tf == '8h':
        compression = 480
        timeframe = bt.TimeFrame.Minutes
    elif tf == '1min':
        compression = 1
        timeframe = bt.TimeFrame.Minutes
    else:
        print('dataframe not recognized')
        exit()
    
    return compression, timeframe


def getWinLoss(analyzer):
    return analyzer.won.total, analyzer.lost.total, analyzer.pnl.net.total


def getSQN(analyzer):
    return round(analyzer.sqn,2)



def runbacktest(datapath, start, end, strategy,
                period,stdcoef=0.5,inquantity = 1.0,outquantity = 1.0,
                commission_val=None, portofolio=10000.0, stake_val=1, plt=False):

    # Create a cerebro entity
    cerebro = bt.Cerebro()

    # Add a FixedSize sizer according to the stake
    cerebro.addsizer(bt.sizers.FixedSize, stake=stake_val) # Multiply the stake by X

    cerebro.broker.setcash(portofolio) # default : 10000.0

    if commission_val:
        cerebro.broker.setcommission(commission=commission_val/100) # divide by 100 to remove the %

    cerebro.broker.set_slippage_perc(perc=0.00005)

    # Add a strategy
    if strategy == stList['btgh']:
        cerebro.addstrategy(BTCBreakoutStrategy, maperiod=period, stdcoef=stdcoef)
    else :
        print('no strategy')
        exit()

    compression, timeframe = timeFrame(datapath)

    # Create a Data Feed
    data = bt.feeds.GenericCSVData(
        dataname = datapath,
        dtformat = 2, 
        compression = compression, 
        timeframe = timeframe,
        fromdate = datetime.datetime.strptime(start, '%Y%m%d'),
        todate = datetime.datetime.strptime(end, '%Y%m%d'),
        reverse = False)


    # Add the Data Feed to Cerebro
    cerebro.adddata(data)


    cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name="ta")
    cerebro.addanalyzer(bt.analyzers.SQN, _name="sqn")

    strat = cerebro.run()
    stratexe = strat[0]

    try:
        totalwin, totalloss, pnl_net = getWinLoss(stratexe.analyzers.ta.get_analysis())
    except KeyError:
        totalwin, totalloss, pnl_net = 0, 0, 0

    sqn = getSQN(stratexe.analyzers.sqn.get_analysis())


    if plt:
        cerebro.plot()

    return cerebro.broker.getvalue(), totalwin, totalloss, pnl_net, sqn
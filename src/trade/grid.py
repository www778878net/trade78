import os
from log78 import Logger78
from center.strategy import Strategy
from log78 import ConsoleLog78, FileLog78, Logger78, KafkaServerLog78

class StockTradeGrid(Strategy):
    def __init__(self, debug=True):
        super().__init__(debug)
        self.kind = "grid"

    def go(self, rt):
        # 实现网格交易策略的逻辑
        print("网格交易策略")
        pass

    def getPars(self):
        parlist = [60,30,90,120,180,360]
        par2list= [ 1]
        par3list= [ 1]
        par4list= [ 1]
        par5list= [ 1]
        par6list= [ 1]
        return parlist, par2list, par3list, par4list, par5list, par6list

    
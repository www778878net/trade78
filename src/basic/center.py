import json
import os
from upinfopy import UpInfo, Api78
from log78 import Logger78
import time
import pandas as pd
import queue

from basic.config78 import Config78

from center import optimizer
from center.optimizer import Optimizer
from center.task_scheduler import TaskScheduler
from trade.grid import StockTradeGrid



class Center():
    """
    Center任务中心 各种任务的入口
    """
    def __init__(self, logger=None,config=None):
        super().__init__()        
        self.logger:Logger78 = logger  
        self.config:Config78 = config
        #策略
        self.strategies = {
            'grid': StockTradeGrid
        }

        self.optimizer = Optimizer(self.strategies, self.logger,self.config)   
        self.runtask=TaskScheduler(self.strategies, self.logger,self.config)   


    async def run(self):        
        """主循环逻辑"""
        mode=os.getenv('APP_MODE', self.config.get('DEFAULT', 'APP_MODE', 'runtask')).lower()
        if(mode=="runtask"):
            await self.runtask.run()
        elif(mode=="optimizer"):
            bootstrap_servers = os.getenv('BOOTSTRAP_SERVERS', self.config.get('DEFAULT', 'bootstrap_servers', '192.168.31.181:30008')).lower()
            print(mode+bootstrap_servers)
            await self.optimizer.run()
        
        
        #await self.test()
        #await self.optimizer.run()        
        return False
  
    async def test(self):
        """测试"""
        strategy = StockTradeGrid(self.logger)
 
        stocks = await strategy.import_stocks('D:/50.code/35.git78py/trade78/src/trade/Table.txt')
        #print(stocks)
        pass
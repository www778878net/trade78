import json
from basic.module_loader import ModuleLoader
from upinfopy import UpInfo, Api78
from log78 import Logger78
import time
import pandas as pd
import queue

from basic.task_thread_pool import TaskThreadPool
from center.optimizer import Optimizer
from trade.grid import StockTradeGrid



class Center(ModuleLoader):
    """
    Center任务中心 各种任务的入口
    """
    def __init__(self, logger=None):
        super().__init__()        
        self.logger:Logger78 = logger  
        #策略
        self.strategies = {
            'grid': StockTradeGrid
        }

        self.optimizer = Optimizer(self.strategies, self.logger)   
        


    async def run(self):        
        """主循环逻辑"""
        
        return False
  
import queue
from log78 import Logger78
from basic.task_thread_pool import TaskThreadPool
from trade.grid import StockTradeGrid
import datetime

class Optimizer:
    def __init__(self, strategies, logger):
        self.strategies = strategies      
        self.logger = logger
        self.task_queue = queue.Queue()
        self.thread_pool = TaskThreadPool(self._run_task, self.task_queue, max_workers=2, logger=self.logger)
        self.dmin =   datetime.datetime.now()- datetime.timedelta(days=1)  # 默认设置启动时运行一次
        
    def run(self):
        """检查任务队列是否完成 并添加队列"""
        if (datetime.datetime.now() - self.dmin).total_seconds() < 120:  # 每2分钟运行一次
            return
        self.dmin=datetime.datetime.now()  
        if(self.thread_pool.get_queue_size()>=10):return 


    def _add_tasks(self, tasks):
        """动态添加多个任务到队列中"""
        self.thread_pool.add_tasks(tasks)

    def _is_task_done(self):
        """检查任务是否完成"""
        return self.thread_pool.get_queue_size() == 0

    def _run_task(self, task):
        try:
            strategy_name = task["strategy_name"]
            param_set = task["param_set"]
            # strategy = self.strategies[strategy_name]
            # strategy_instance = strategy(self.logger)
            # strategy_instance.go(param_set)
        except Exception as e:
            self.logger.ERROR(f"Error running task: {e}")


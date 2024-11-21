import datetime
import queue
from log78 import Logger78
from basic.config78 import Config78
from basic.task_thread_pool import TaskThreadPool
from center.strategy import Strategy
from upinfopy import UpInfo


class TaskScheduler:
    def __init__(self, strategies, logger, config, max_workers=5):
        self.strategies = strategies      
        self.logger = logger
        self.config: Config78 = config
        self.task_queue = queue.Queue()
        self.thread_pool = TaskThreadPool(self._run_task, self.task_queue, max_workers=max_workers, logger=self.logger)
        self.dmin = datetime.datetime.now() - datetime.timedelta(days=1)  # 默认设置启动时运行一次
        

    async def run(self):
        """检查任务队列是否完成，并添加任务队列"""
        current_time = datetime.datetime.now()
        
        # 每分钟运行一次优化任务
        if (current_time - self.dmin).total_seconds() < 60:
            return
        
        self.dmin = current_time  # 更新时间标记
        
        if self.thread_pool.get_queue_size() >= 10:
            return  # 如果任务队列已满，不再添加任务
        
        up = UpInfo.getMaster() 
        up.getnumber = 9999
        # dt = await up.send_back("apistock/stock/stock_trade/getByTrade")  
        # self._add_tasks(dt)

    async def test(self):
        """用于测试任务调度和参数优化"""
        up = UpInfo.getMaster() 
        up.getnumber = 10
        dt = await up.send_back("apistock/stock/stock_trade/getByTrade")  
        print(dt)
        for row in dt:
            await self._run_task(row)

    def _add_tasks(self, tasks):
        """动态添加多个任务到队列中"""
        self.thread_pool.add_tasks(tasks)

    async def _run_task(self, rt):
        """执行每个优化任务"""
        print(f"Processing task: {rt}")
        #获取每个代码算法最小日期D
        dnow=datetime.datetime.now()
        dstart=rt["dval"]
        card=rt["card"]
        kind=rt["kind"]
        strategy:Strategy = self.strategies[kind]
        strategy_instance = strategy(self.logger,debug=True)
        line=rt["line"]      
        #if rt["kind"]!="grid":                continue
        if(dstart=="0001-01-01 00:00:00"):
            yearstart=str(int(dnow.strftime('%Y'))-4)
            dstart=yearstart+"-01-01 00:00:00"
            rt["dval"]=dstart
                #获取日线
        up=UpInfo.getMaster() 
        up.getnumber=9999
        up.set_par(card,dstart)
        dt=await up.send_back("apistock/stock/stock_data_day/getByCardAll") 
        if(dt==''):   
            return
        await self.logger.INFO(f"Stock_trade _run_task do :{card}")
        for rv in dt:#日线循环
            dmin5=datetime.datetime.strptime(rv["tradedate"],'%Y-%m-%d')
            dval=datetime.datetime.strptime(rt["dval"],'%Y-%m-%d %H:%M:%S')
            if(dval>=dmin5):continue

            rt["dval"] = rv["tradedate"]+" 00:00:00"
            await strategy_instance.go(rv,rt,True,True,False)
import asyncio
import datetime
import queue
import threading
from log78 import Logger78
from basic.config78 import Config78
from center.strategy import Strategy, TradeLogEntry
from upinfopy import UpInfo
import json


class TaskScheduler:
    def __init__(self, strategies, logger:Logger78, config, max_workers=5):
        self.strategies = strategies      
        self.logger = logger.clone()
        self.config: Config78 = config
        #self.task_queue = queue.Queue()
        #self.thread_pool = TaskThreadPool(self._run_task, self.task_queue, max_workers=max_workers, logger=self.logger)
        self.dnext = datetime.datetime.now() - datetime.timedelta(days=1)  # 默认设置启动时运行一次
        

    async def run(self):
        """检查任务队列是否完成，并添加任务队列"""
        current_time = datetime.datetime.now()
        
        # 每分钟运行一次优化任务
        if (current_time - self.dnext).total_seconds() < 600:
            return
        
        self.dnext = current_time  # 更新时间标记
        # thread = threading.Thread(target=self._run_in_thread, daemon=True)
        # thread.start()
        #asyncio.create_task(self.__run())  # 通过 asyncio 调度 __run
        await self.__run()
        
        # up = UpInfo.getMaster() 
        # up.getnumber = 9999
        # dt = await up.send_back("apistock/stock/stock_trade/getByTrade")  
        # self._add_tasks(dt)
        return
    
    def _run_in_thread(self):
        """在后台运行异步任务"""
        loop = asyncio.new_event_loop()  # 创建新事件循环
        asyncio.set_event_loop(loop)    # 设置为当前线程事件循环
        try:
            loop.run_until_complete(self.__run())  # 运行协程
        finally:
            loop.close()  # 关闭事件循环

    
    
    async def __run(self):
        u"""5分钟一次实时交易""" 
        dover=datetime.datetime.now() 
        hour=int(dover.strftime('%H')  )
        if(hour<15):dover-= datetime.timedelta(days=1)
        # 判断当前日期是否为周六或周日
        if dover.weekday() == 5:  # 周六
            dover -= datetime.timedelta(days=1)  # 调整到周五
        elif dover.weekday() == 6:  # 周日
            dover -= datetime.timedelta(days=2)  # 调整到周五

        dover=dover.strftime('%Y-%m-%d 00:00:00')

        isAllok=True        
        up = UpInfo.getMaster()           
        up.order="dval"
        up.set_par(dover)
        up.getnumber = 50
        dtTrade =await up.send_back("apistock/stock/stock_trade/getByTrade", up) 
        dtTrade= json.loads(dtTrade)  # 返回JSON格式的数据
        for rt in dtTrade:#算法循环 
            self.dnext = datetime.datetime.now()
            with open('/tmp/healthy', 'w') as f:
                f.write('healthy')
            self.dnext=datetime.datetime.now() + datetime.timedelta(minutes=10)
            await self.__run_do(rt)
            #self._log.add("Stock_Trade __run go over"+rt["card"]+rt["dval"]) 
            isAllok=False
            continue
        if(isAllok):
            await self.logger.INFO("Stock_Trade __run allok")
            self.dnext=datetime.datetime.now() + datetime.timedelta(minutes=10)
        else:
            self.dnext=datetime.datetime.now() + datetime.timedelta(minutes=1)
        return

    async def __run_do(self, rt):
        """执行每个优化任务"""
        
        #获取每个代码算法最小日期D
        dnow=datetime.datetime.now()
        dstart=rt["dval"]
        card=rt["card"]
        kind=rt["kind"]
        strategy:Strategy = self.strategies[kind]
        strategy_instance = strategy(self.logger,debug=True)
        line=rt["line"]      
        #if rt["kind"]!="grid":                continue
        #if(dstart=="0001-01-01 00:00:00"  ):
        dstartUTC = (datetime.datetime.now() - datetime.timedelta(days=4*365)).replace(month=1, day=1, hour=0, minute=0, second=0).strftime("%Y-%m-%dT%H:%M:%SZ")

        await self.logger.INFO(f"Stock_trade _run_task do :{card}")
        #获取日线
        up=UpInfo.getMaster() 
        up.getnumber=9999
        up.set_par(card,dstartUTC)
        dt=await up.send_back("apistock/stock/stock_data_day/getByCardAll") 
        if(len(dt)==0 or  dt==None or dt==''):   
            return
        needsave=True
        
        for rv in dt:#日线循环
            dmin5=datetime.datetime.strptime(rv["tradedate"],'%Y-%m-%d')
            dval=datetime.datetime.strptime(rt["dval"],'%Y-%m-%d %H:%M:%S')
            if(dval>=dmin5):continue

            rt["dval"] = rv["tradedate"]+" 00:00:00"
            rt["lastval"]=rv["close"] 
            await strategy_instance.go(rv,rt,True,True,False,dt)
            continue
        ##保存算法当前状态   
        if(needsave):    
            await self.__save(rt)
    
    async def __save(self,rt):
        """保存当前算法"""
        log_entry = TradeLogEntry()
        # 使用 rt 字典来访问字段值
        log_entry.kind = rt["kind"]
        log_entry.card = rt["card"]      
        log_entry.par = rt["par"]
        log_entry.par2 = rt["par2"]
        log_entry.par3 = rt["par3"]
        log_entry.par4 = rt["par4"]
        log_entry.par5 = rt["par5"]
        log_entry.par6 = rt["par6"]
        
        # 修改字段值      
        log_entry.lastval =  rt.get("lastval", 0)
        log_entry.winval = rt["winval"]  # 算法利润
        log_entry.dval = rt["dval"]  # 日期值
        log_entry.upnum = rt["upnum"]   # 上升数量
        log_entry.upval = rt["upval"] 
        log_entry.downnum = rt["downnum"]  # 下降数量
        log_entry.downval = rt["downval"] 
        log_entry.stoptime = rt["stoptime"]  # 停止时间1
        log_entry.stoptime2 = rt["stoptime2"]  # 停止时间2
        log_entry.optimizetime = rt["optimizetime"]
        log_entry.val7 = rt["val7"]  # 策略值7
        log_entry.val8 = rt["val8"]  # 策略值8
        log_entry.val9 = rt["val9"]  # 策略值9
        log_entry.val1 = rt["val1"]  # 策略值1
        log_entry.val2 = rt["val2"]  # 策略值2
        log_entry.val3 = rt["val3"]  # 策略值3
        log_entry.val4 = rt["val4"]  # 策略值4
        log_entry.val5 = rt["val5"]  # 策略值5
        log_entry.val6 = rt["val6"]  # 策略值6        
        log_entry.allnum = rt["allnum"]  # 总数
        log_entry.winnum = rt["winnum"]  # 胜利次数
        log_entry.winsum = rt["winsum"]  # 赢利总和
        log_entry.event.event_id = log_entry.card+log_entry.kind
        tmp=await self.logger.WARN(log_entry)
        return

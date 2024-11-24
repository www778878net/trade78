import asyncio
import queue
import threading
from log78 import Logger78
from basic.config78 import Config78
from basic.task_thread_pool import TaskThreadPool
from center.strategy import Strategy, TradeLogEntry, TradeParLogEntry
from trade.grid import StockTradeGrid
import datetime
from upinfopy import UpInfo, Api78

class Optimizer:
    def __init__(self, strategies, logger:Logger78,config):
        self.strategies = strategies      
        self.logger = logger.clone()
        self.config:Config78 = config
        #self.task_queue = queue.Queue()
        #self.thread_pool = TaskThreadPool(self._run_task, self.task_queue, max_workers=2, logger=self.logger)
        self.dnext =   datetime.datetime.now()- datetime.timedelta(days=1)  # 默认设置启动时运行一次
        
    # async def Taskrun(self):
    #     """检查任务队列是否完成 并添加队列"""
    #     if (datetime.datetime.now() - self.dnext).total_seconds() < 60:  # 每2分钟运行一次
    #         return
    #     self.dnext=datetime.datetime.now()  
    #     if(self.thread_pool.get_queue_size()>=10):return 
    #     up=UpInfo.getMaster() 
    #     up.getnumber=10
    #     dt=await up.send_back("apistock/stock/stock_trade/mForOptimizetimeAll")  
    #     self._add_tasks(dt)

    #     return
    
    async def run(self):
        """检查任务队列是否完成，并添加任务队列"""
        current_time = datetime.datetime.now()
        
        # 每分钟运行一次优化任务
        if (current_time - self.dnext).total_seconds() < 600:
            return
        
        self.dnext = current_time  # 更新时间标记
            # 使用线程启动任务
        # thread = threading.Thread(target=self._run_in_thread, daemon=True)
        # thread.start()
        #asyncio.create_task(self.__run())  # 通过 asyncio 调度 __run
        await self.__run()
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
        up=UpInfo.getMaster() 
        up.getnumber=3#这里直接是调整减几天 每次只获取一个
        dt=await up.send_back("apistock/stock/stock_trade/mForOptimizetimeAll")  
        #print (dt)
        isAllok=True  
        for row in dt:
            await self._run_task(row)
            isAllok=False
            continue
        if(isAllok):
            await self.logger.INFO("Stock_Trade Optimizer allok")
            self.dnext=datetime.datetime.now() #+ datetime.timedelta(minutes=10)
        else:
            self.dnext=datetime.datetime.now() - datetime.timedelta(minutes=100)
        return

    def _add_tasks(self, tasks):
        """动态添加多个任务到队列中"""
        self.thread_pool.add_tasks(tasks)
        return
    
    async def __optimization(self,rt,strategy_instance:Strategy):
        parlist, par2list, par3list, par4list, par5list, par6list = strategy_instance.getPars()
        card = rt["card"] 
        kind= rt["kind"]
        mid=rt["id"]
        await self.logger.INFO(f"Stock_trade optimization do :{card}")
        dnow=datetime.datetime.now()
        yearstart=str(int(dnow.strftime('%Y'))-4)
        dstart=yearstart+"-01-01T00:00:00Z"
        #获取日线
        up=UpInfo.getMaster() 
        up.getnumber=9999
        up.set_par(card,dstart)
        dt=await up.send_back("apistock/stock/stock_data_day/getByCardAll")  
        if(len(dt)==0):    
            return 1,1,1,0,0,0
        bestwinval=-99999999#最好战绩
        bestpar=0#最好参数
        bestpar2=0#最好参数
        bestpar3=0#最好参数

        dstart=datetime.datetime.now()   - datetime.timedelta(days=365*3)
        dstart=datetime.datetime.strftime(dstart,'%Y-%m-%d 00:00:00')
        tmpcard=self.config.get('DEFAULT', 'optimization', '')
        if(tmpcard==card):
            tmp=self.config.get('DEFAULT', 'optimizationpar', '')     
        else:#清空
            self.config.set('DEFAULT', 'optimization', '')
            self.config.set('DEFAULT', 'optimizationpar', '')  
            tmp=""
            #清空elk原来的这个card的记录
            up=UpInfo.getMaster() 
            up.set_par(card,kind)
            await up.send_back("apistock/stock/stock_trade/mClearTradepar")  
        if(tmp==""):
            parsave=-1
            par2save=-1
            par3save=-1
            bestwinval=-99999999
        else:
            tmplist=tmp.split(",")
            parsave=float(tmplist[0])
            par2save=float(tmplist[1])
            par3save=float(tmplist[2])
            if(len(tmplist)>=4):
                bestwinval=float(tmplist[3])
            if(len(tmplist)>=7):
                bestpar=float(tmplist[4])#最好参数
                bestpar2=float(tmplist[5])#最好参数
                bestpar3=float(tmplist[6])#最好参数
        nowwinval=rt["winval"]
        for par in parlist:
            for par2 in par2list:   
                for par3 in par3list:
                    if(par<parsave ):
                        continue
                    if(par==parsave and par2<par2save):
                        continue
                    if(par==parsave and par2==par2save and par3<=par3save):
                        continue
                    with open('/tmp/healthy', 'w') as f:
                        f.write('healthy')
                    #time.sleep(0.1)
                    rt["winval"]=0                    
                    rt["par"]=par
                    rt["par2"]=par2
                    rt["par3"]=par3
                    rt["upnum"]=0
                    rt["downnum"]=0
                    rt["allnum"]=0
                    rt["winnum"]=0
                    rt["winsum"]=0
                    rt["stoptime"]='0001-01-01 00:00:00'
                    rt["stoptime2"]='0001-01-01 00:00:00'
                    rt["dval"]=dstart
                    rt["val1"]=0
                    rt["val2"]=0
                    rt["val3"] = 0
                    rt["val4"] = 0
                    rt["val5"] = 0
                    rt["val6"] = 0
                    rt["val7"] = 0
                    rt["val8"] = 0
                    rt["val9"] = 0

                    for rv in dt:#日线循环 
                        try:
                            tradedate = datetime.datetime.strptime(rv["tradedate"], "%Y-%m-%d")  # 转为 date 对象
                            dval = datetime.datetime.strptime(rt["dval"], "%Y-%m-%d %H:%M:%S")  # 转为 datetime 对象
                        except Exception as e:
                            # 打印异常信息和 rv, rt 的值（所有内容在一行）
                            print(f"Exception occurred: {e}, rv['tradedate']: {repr(rv)}, dt: {repr(dt)}")
                            continue
                        
                             
                        if(tradedate<dval ):
                            continue
                        rt["dval"] = rv["tradedate"]+" 00:00:00" 
                        rt["lastval"] = rv["close"] 
                        await strategy_instance.go(rv,rt,True,False,False,dt)
                        continue
                    tmp=rt["winval"]
                    #加上当前的收益
                    tmp+=(rt["lastval"] - rt["upval"]) * rt["upnum"] 
                    log_entry = TradeParLogEntry()
                    log_entry.kind = rt["kind"]
                    log_entry.card = rt["card"]
                    log_entry.par = rt["par"]
                    log_entry.par2 =  rt["par2"]
                    log_entry.par3 =  rt["par3"]
                    log_entry.par4 =  rt["par4"]
                    log_entry.par5 =  rt["par5"]
                    log_entry.par6 =  rt["par6"]
                    log_entry.winval =  tmp
                    log_entry.allnum = rt["allnum"]
                    log_entry.winnum = rt["winnum"]
                    log_entry.winsum = rt["winsum"]
                    log_entry.event.event_id = log_entry.card + "_" + str(log_entry.par) + "_" + str(log_entry.par2) + "_" + str(log_entry.par3) + "_" + str(log_entry.par4) + "_" + str(log_entry.par5)
                    await self.logger.WARN(log_entry)
                    # up=UpInfo.getMaster() 
                    # up.set_par(rt["kind"],rt["line"],rt["card"],tmp,rt["par"],rt["par2"],rt["par3"],rt["par4"],rt["par5"],rt["par6"]) 
                    #mtradepar= self.api.get("apinet/stock/stock_tradepar/mAdd", up) 
                    if(tmp>bestwinval or bestwinval==-99999999 ):
                        bestwinval=tmp
                        bestpar=par
                        bestpar2=par2
                        bestpar3=par3
                        #if(tmp>nowwinval):
                            #up=UpInfo.getMaster() 
                            #up.mid=rt["id"]
                            #up.set_par(bestpar,bestpar2,bestpar3,0,0,0,rt["card"],rt["kind"],rt["line"])
                            #这里可能造成计算中途被删除了 就没有历史记录了
                            #tmp= self.api.get("apinet/stock/stock2_trade/mInit", up)
                    self.config.set('DEFAULT', 'optimization', card)
                    self.config.set('DEFAULT', 'optimizationpar',str(par)+","+str(par2)+","+str(par3)+","+str(bestwinval)+","+str(bestpar)+","+str(bestpar2)+","+str(bestpar3))
                    # self._log.add("stocktrade__optimization once:"+rt["kind"]+card+" "+str(par)+" "+str(par2)+" "+str(par3)+","+str(bestwinval))
                        #return bestpar,bestpar2,bestpar3
                    continue
                continue
            continue
        self.config.set('DEFAULT',"optimization","")
        return bestpar,bestpar2,bestpar3,0,0,0
        


    async def _run_task(self, task):
        #print (task)
        kind = task["kind"]
        strategy:Strategy = self.strategies[kind]
        strategy_instance = strategy(self.logger,debug=True)            
        bestpar,bestpar2,bestpar3,bestpar4,bestpar5,bestpar6 =await self.__optimization(task,strategy_instance)
        #保存算法当前最优状态
        log_entry = TradeLogEntry()
        log_entry.kind = kind
        log_entry.card = task["card"]      
        log_entry.par = bestpar
        log_entry.par2 = bestpar2
        log_entry.par3 = bestpar3
        log_entry.par4 = bestpar4
        log_entry.par5 = bestpar5
        log_entry.par6 = bestpar6
        # 时区简单点处理了算
        log_entry.optimizetime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')   # 优化时间
        log_entry.winval = 0                            # 算法利润
        log_entry.upnum = 0                             # 上升数量
        log_entry.downnum = 0                           # 下降数量
        log_entry.stoptime = '1911-01-01 00:00:00'               # 停止时间1
        log_entry.stoptime2 = '0001-01-01 00:00:00'              # 停止时间2
        log_entry.dval = '1910-01-01 00:00:00'                   # 日期值
        log_entry.val7 = 0                              # 策略值7
        log_entry.val8 = 0                              # 策略值8
        log_entry.val9 = 0                              # 策略值9
        log_entry.val1 = 0                              # 策略值1
        log_entry.val2 = 0                              # 策略值2
        log_entry.val3 = 0                              # 策略值3
        log_entry.val4 = 0                              # 策略值4
        log_entry.val5 = 0                              # 策略值5
        log_entry.val6 = 0                              # 策略值6
        log_entry.worker = ''                           # 分布式用户名（优化参数的）
        log_entry.allnum = 0                            # 总数
        log_entry.winnum = 0                            # 胜利次数
        log_entry.winsum = 0                            # 赢利总和
        log_entry.event.event_id = log_entry.card+kind
        tmp=await self.logger.WARN(log_entry)
        return
     
    


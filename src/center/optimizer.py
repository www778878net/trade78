import queue
from log78 import Logger78
from basic.config78 import Config78
from basic.task_thread_pool import TaskThreadPool
from center.strategy import Strategy
from trade.grid import StockTradeGrid
import datetime
from upinfopy import UpInfo, Api78

class Optimizer:
    def __init__(self, strategies, logger,config):
        self.strategies = strategies      
        self.logger = logger
        self.config:Config78 = config
        self.task_queue = queue.Queue()
        self.thread_pool = TaskThreadPool(self._run_task, self.task_queue, max_workers=2, logger=self.logger)
        self.dmin =   datetime.datetime.now()- datetime.timedelta(days=1)  # 默认设置启动时运行一次
        
    async def run(self):
        """检查任务队列是否完成 并添加队列"""
        if (datetime.datetime.now() - self.dmin).total_seconds() < 60:  # 每2分钟运行一次
            return
        self.dmin=datetime.datetime.now()  
        if(self.thread_pool.get_queue_size()>=10):return 
        up=UpInfo.getMaster() 
        up.getnumber=10
        dt=await up.send_back("apistock/stock/stock_trade/mForOptimizetimeAll")  
        self._add_tasks(dt)

        return
    
    async def test(self):
        up=UpInfo.getMaster() 
        up.getnumber=10
        dt=await up.send_back("apistock/stock/stock_trade/mForOptimizetimeAll")  
        for row in dt:
            await self._run_task(row)
            continue
        return

    def _add_tasks(self, tasks):
        """动态添加多个任务到队列中"""
        self.thread_pool.add_tasks(tasks)
        return
    
    async def __optimization(self,rt,strategy_instance:Strategy):
        parlist, par2list, par3list, par4list, par5list, par6list = strategy_instance.getPars()
        card = rt["card"] 
        mid=rt["id"]
        await self.logger.INFO(f"Stock_trade optimization do :{card}")
        dnow=datetime.datetime.now()
        yearstart=str(int(dnow.strftime('%Y'))-4)
        dstart=yearstart+"-01-01 00:00:00"
        #获取日线
        up=UpInfo.getMaster() 
        up.getnumber=9999
        up.setPars(card,dstart)
        dt=await up.send_back("apistock/stock/stock_data_day/getByCardAll")  
        if(dt==""):    
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
        else:
            self.config.set('DEFAULT', 'optimization', '')
            self.config.set('DEFAULT', 'optimizationpar', '')  
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
                    #time.sleep(0.1)
                    rt["winval"]=0
                    rt["imain"]=0
                    rt["par"]=par
                    rt["par2"]=par2
                    rt["par3"]=par3
                    rt["upnum"]=0
                    rt["downnum"]=0
                    rt["stoptime"]='0001-01-01 00:00:00'
                    rt["stoptime2"]='0001-01-01 00:00:00'
                    rt["dval"]=dstart
                    rt["val1"]=0
                    rt["val2"]=0

                    for rv in dt:#日线循环             
                        if(rv["ddate"]<rt["dval"]):
                            continue
                        rt["dval"] = rv["ddate"]+" 00:00:00" 
                        await strategy_instance.go(rv,rt,True,False,False,dt)
                        continue
                    tmp=rt["winval"]
                    #加上当前的收益
                    tmp+=(rt["lastval"] - rt["upval"]) * rt["upnum"] 
                    up=UpInfo.getMaster() 
                    up.setPars(rt["kind"],rt["line"],rt["card"],tmp,rt["par"],rt["par2"],rt["par3"],rt["par4"],rt["par5"],rt["par6"]) 
                    #mtradepar= self.api.get("apinet/stock/stock2_group_tradepar/mAdd", up) 
                    if(tmp>bestwinval or bestwinval==-99999999 ):
                        bestwinval=tmp
                        bestpar=par
                        bestpar2=par2
                        bestpar3=par3
                        #if(tmp>nowwinval):
                            #up=UpInfo.getMaster() 
                            #up.mid=rt["id"]
                            #up.setPars(bestpar,bestpar2,bestpar3,0,0,0,rt["card"],rt["kind"],rt["line"])
                            #这里可能造成计算中途被删除了 就没有历史记录了
                            #tmp= self.api.get("apinet/stock/stock2_trade/mInit", up)
                    self.config.set('DEFAULT', 'optimizationpar',str(par)+","+str(par2)+","+str(par3)+","+str(bestwinval)+","+str(bestpar)+","+str(bestpar2)+","+str(bestpar3))
                    # self._log.add("stocktrade__optimization once:"+rt["kind"]+card+" "+str(par)+" "+str(par2)+" "+str(par3)+","+str(bestwinval))
                        #return bestpar,bestpar2,bestpar3
                    continue
                continue
            continue
        self.config.set('DEFAULT',"optimization","")
        return bestpar,bestpar2,bestpar3,0,0,0
        


    async def _run_task(self, task):
        try:
             
            kind = task["kind"]
            strategy:Strategy = self.strategies[kind]
            strategy_instance = strategy(self.logger,Debug=True)            
            bestpar,bestpar2,bestpar3,bestpar4,bestpar5,bestpar6 =await self.__optimization(task,strategy_instance)
            #保存算法当前状态  
           
        except Exception as e:
            self.logger.ERROR(f"Error running task: {e}")
        return
    


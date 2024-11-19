import datetime
import os
import time
from center.strategy import HistoryLogEntry, Strategy
from log78 import ConsoleLog78, FileLog78, Logger78, KafkaServerLog78

class StockTradeGrid(Strategy):
    u""""N日最高最低区间分为10格 每格交易10万
    val1 val2区间高低点 val3当前持仓区间
    """
    def __init__(self, debug=True):
        super().__init__(debug)
        self.kind = "grid"

    async def go(self, rv,rt,isclose,issave,isclosewarn=False,dt=None):
        u"""三次判断"""
        #rv价格表 rt算法参数表
        #isclose是否收盘价 有的必须收盘才交易
        #issave是否保存交易
        #isclosewarn是否接近报警
        #dt所有的日线数据
        if self.iswait:time.sleep(0.02)
        card=rt["card"]#代码      
        dval = rt["dval"]#算法计算到哪了
        upnum = rt["upnum"]#算法参数        
        upval = rt["upval"]
        winval= rt["winval"]

        vclose=rv["close"]  
        tmp=self.refgrid(rt,dt)   
        if(tmp["val1"]==None):return   

        val1 = tmp["val1"]  # 高点
        val2 = tmp["val2"]  # 低点
        grid_size = (val1 - val2) / 10  # 每格的价格区间
        # 计算当前价格所在的网格
        grid_index = int((vclose - val2) / grid_size)
        # 当前持仓量 1~10
        areadef=10-grid_index
        areagrid=tmp["val3"]        
        
        if(areagrid==areadef):return

        opennum=int(100000/vclose)  # 向下取整
        openval=vclose
        rt["todayclose"]=openval
        if(areagrid<areadef):            
            doubel=areadef-areagrid
            reason='开仓'+str(doubel)+'份'
            rt["upval"]=(upval*upnum+opennum*openval)/(upnum+opennum)
            rt["upnum"]=upnum+opennum
            remark=str(vclose)+"达到条件开仓数" +str(upnum)   
            if( isclosewarn  ):    
                rt["todayopen"]=True#今天开仓
            if(issave):
                log_entry = HistoryLogEntry()
                log_entry.card = card
                log_entry.kind = self.kind
                log_entry.dtime = dval
                log_entry.price = openval
                log_entry.num = opennum
                log_entry.reason = reason
                log_entry.winval = winval
                log_entry.remark = remark
                await self.logger.WARN(log_entry)
            return
        
        #平仓
        doubel=areagrid-areadef
        reason='平仓'+str(doubel)+'份'
        if(areadef==0):#全平
            opennum=upnum
        winval=(openval - upval)*opennum-openval*opennum *0.002 ;   
        if(openval>=upval):
            rt["winsum"]+=winval#赢利总和(不计亏损)算凯利公式
            rt["winnum"]+=1
        rt["upnum"]=rt["upnum"]-opennum
        rt["winval"]+=winval
        if(issave):
            log_entry = HistoryLogEntry()
            log_entry.card = card
            log_entry.kind = self.kind
            log_entry.dtime = dval
            log_entry.price = openval
            log_entry.num = rt["upnum"]
            log_entry.reason = reason
            log_entry.winval = rt["winval"]
            log_entry.remark = str(vclose)+" 平仓" +str(upnum) 
            await self.logger.WARN(log_entry)    
            
        pass

    def refgrid(self,rt,dt):
        u"""重置区间不用每天算"""  
        card=rt["card"]#代码
        dval=rt["dval"]
        par = rt["par"]#算法参数 N天
        dend=datetime.datetime.strptime(dval,'%Y-%m-%d %H:%M:%S') 
        dstart = dend - datetime.timedelta(days=par)

         # 获取 par 天的最高和最低价格
        highest_price = float('-inf')
        lowest_price = float('inf')
        for day_data in dt:
            date = datetime.datetime.strptime(day_data['date'], '%Y-%m-%d')
            if date > dend:
                break
            if date >= dstart:
                highest_price = max(highest_price, day_data['high'])
                lowest_price = min(lowest_price, day_data['low'])

        return {
            "val1": highest_price if highest_price != float('-inf') else None,
            "val2": lowest_price if lowest_price != float('inf') else None,
            #"c": (highest_price + lowest_price) / 2 if highest_price != float('-inf') and lowest_price != float('inf') else None
        }

    def getPars(self):
        parlist = [60,30,90,120,180,360]
        par2list= [ 1]
        par3list= [ 1]
        par4list= [ 1]
        par5list= [ 1]
        par6list= [ 1]
        return parlist, par2list, par3list, par4list, par5list, par6list

    
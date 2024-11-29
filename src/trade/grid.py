import datetime
import os
import time
from center.strategy import HistoryLogEntry, Strategy
from log78 import ConsoleLog78, FileLog78, Logger78, KafkaServerLog78

class StockTradeGrid(Strategy):
    u""""N日最高最低区间分为10格 每格交易10万
    val1 val2区间高低点 val3当前持仓区间
    """
    def __init__(self, logger, debug=True):   
        super().__init__(logger,debug)
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

        val1 = rt["val1"]  # 高点
        val2 = rt["val2"]  # 低点
        grid_size = (val1 - val2) / 10  # 每格的价格区间
        if(grid_size==0):return
        # 如果格子小于val1的10%，调整格子大小为原来的1/5
        if grid_size < val1 * 0.01:
            grid_size /= 5

            # 如果格子仍然小于10%且调整后的格子大小依然很小，则退出
            if grid_size < val1 * 0.01:
                return  # 格子过小，退出
        
        # 计算当前价格所在的网格
        grid_index = int((vclose - val2) / grid_size)
          # 定义增仓和减仓的区间0-9
        buy_index = 10 - grid_index-1  # 增仓区间
       
        # 当前持仓量 1~10
        sell_index=10-grid_index  # 减仓区间
        areagrid=rt["val3"]        
        
        if(areagrid==sell_index):return

        #opennum=int(100000/vclose)  # 向下取整
        #openval=vclose
        
        if(areagrid<buy_index ):            
            # 逐步增仓直到买入区间
            for idx in range(areagrid + 1, buy_index + 1):
                # 计算该网格的开仓价格
                # 假设网格的价格为 val2 + (idx + 1) * grid_size
                openval = val1 - idx * grid_size               
                reason = f'开仓  第 {idx} 区，开仓价格 {openval}'

                opennum = int(100000/openval)  
                # 更新加权平均开仓价
                rt["upval"] = (rt["upval"] * rt["upnum"] + opennum * openval) / (rt["upnum"] + opennum)
                rt["upnum"] += opennum
                rt["val3"] = idx  # 更新当前持仓区间
                remark = f"{vclose} 达到条件开仓数 {rt['upnum']} 价{rt["upval"] }，开仓价格 {openval}"

                if isclosewarn:
                    rt["todayopen"] = True  # 今天开仓
                if issave:
                    log_entry = HistoryLogEntry()
                    log_entry.card = card
                    log_entry.kind = self.kind
                    log_entry.dtime = dval
                    log_entry.price = openval
                    log_entry.num = rt["upnum"]
                    log_entry.reason = reason
                    log_entry.winval = winval
                    log_entry.remark = remark
                    await self.logger.WARN(log_entry)
            return
        
        if(areagrid<=sell_index):return
         # 逐步减仓直到卖出区间
        for idx in range(areagrid - 1, sell_index - 1, -1):  # 从当前区间向下逐步平仓
            # 计算该网格的平仓价格
            # 假设网格的价格为 val2 + (idx + 1) * grid_size
            closeval = val1 - idx  * grid_size            
            reason = f'平仓 第 {idx+1} 区，平仓价格 {closeval}'

            opennum = int(100000/closeval)  
            # 更新加权平均开仓价（减仓时可以更新平仓的金额和数量）
            rt["winval"] += (closeval - upval) * opennum - closeval * opennum * 0.002  # 计算平仓盈亏
            rt["upnum"] -= opennum  # 更新持仓数量
            rt["val3"] = idx  # 更新当前持仓区间
            remark = f"{vclose} 达到条件平仓 数 {rt['upnum']} 价{rt["upval"] }，平仓价格 {closeval}"

            if isclosewarn:
                rt["todayclose"] = True  # 今天平仓

            if issave:
                log_entry = HistoryLogEntry()
                log_entry.card = card
                log_entry.kind = self.kind
                log_entry.dtime = dval
                log_entry.price = closeval
                log_entry.num = rt["upnum"]
                log_entry.reason = reason
                log_entry.winval = rt["winval"]
                log_entry.remark = remark
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
            date = datetime.datetime.strptime(day_data['tradedate'], '%Y-%m-%d')
            if date > dend:
                break
            if date >= dstart:
                highest_price = max(highest_price, day_data['high'])
                lowest_price = min(lowest_price, day_data['low'])

        rt["val1"] = highest_price
        rt["val2"] = lowest_price
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

    
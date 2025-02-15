import os
from log78 import LogEntry,Logger78


class Strategy:
    def __init__(self, logger, debug=True):     
        self.iswait=False#CPU紧张时设置为TRUE 每次等0.2秒
        self.logger:Logger78 = logger   
        self.debug = debug
        self.uid = None
        self.kind = None
        self.line = None
        self.card = None
        self.par = 8.00
        self.par2 = 0.00
        self.par3 = 0.00
        self.par4 = 0.00
        self.par5 = 0.00
        self.par6 = 0.00
        self.winval = 0.00
        self.dval = '0001-01-01 00:00:00'
        self.val1 = 0.00
        self.val2 = 0.00
        self.val3 = 0.00
        self.val4 = 0.00
        self.val5 = 0.00
        self.val6 = 0.00
        self.val7 = 0.00
        self.val8 = 0.00
        self.val9 = 0.00
        self.stoptime = '1900-01-01 00:00:00'
        self.stoptime2 = '1900-01-01 00:00:00'
        self.upval = 0.00
        self.upnum = 0
        self.downnum = 0
        self.downval = 0.00
        self.status = ''
        self.worker = ''
        self.optimizetime = '0001-01-01 00:00:00'
        self.iswarnwx = 0
        self.winnum = 0
        self.allnum = 0
        self.winsum = 0.00
        self.todayopen = False
        self.douser = ''
        self.upby = ''        
        self.id = ''


    async def go(self, rv,rt,isclose,issave,isclosewarn=False,dt=None):
        u"""三次判断"""
        #rv价格表 rt算法参数表
        #isclose是否收盘价 有的必须收盘才交易
        #issave是否保存交易
        #isclosewarn是否接近报警
        raise NotImplementedError("Strategy.go() must be overridden.")
    
    def getPars(self):
        parlist = [1]
        par2list= [ 1]
        par3list= [ 1]
        par4list= [ 1]
        par5list= [ 1]
        par6list= [ 1]
        return parlist, par2list, par3list, par4list, par5list, par6list
    
    async def import_stocks(self, filepath):
        """导入自选股列表并去除前两位字符"""
        stocks = []
        print("当前工作目录:", os.getcwd())
        with open(filepath, 'r', encoding='utf-8') as file:
            for line in file:
                stock = line.strip()
                if stock:
                    if( len(stock)>6):
                        stock=stock[2:]  # 去除前两位字符
                    log_entry = TradeLogEntry()
                    log_entry.kind = self.kind
                    log_entry.card = stock
                    parlist, par2list, par3list, par4list, par5list, par6list = self.getPars()
                    log_entry.par = parlist[0]
                    log_entry.par2 = par2list[0]
                    log_entry.par3 = par3list[0]
                    log_entry.par4 = par4list[0]
                    log_entry.par5 = par5list[0]
                    log_entry.par6 = par6list[0]
                    log_entry.event.event_id = log_entry.card+self.kind
                    log_entry.douser="syslocalserver"
                    log_entry.worker="syslocalserver"
                    log_entry.basic.log_index = "stock_trade-main"# "backtest-main" #"stock_trade-main"

                    log_entry.optimizetime="2021-01-01T00:00:00Z"
                    log_entry.stoptime="2021-01-01T00:00:00Z"
                    log_entry.stoptime2="2021-01-01T00:00:00Z"
                    log_entry.dval="2021-01-01 00:00:00"
                   
                    await self.logger.WARN(log_entry)
                    continue
        return stocks   

class TradeParLogEntry(LogEntry):
    def __init__(self):
        super().__init__() 
        # 初始化属性
        self.cid = None        # 用户 (User ID)
        self.kind = None       # 算法类型 (Algorithm type)
        self.line = 'd'        # 日线 (默认日线，可能为周线或小时线)
        self.card = None       # 交易代码 (Stock or asset code)
        self.par = None        # 参数 1 (Parameter 1)
        self.par2 = None       # 参数 2 (Parameter 2)
        self.par3 = None       # 参数 3 (Parameter 3)
        self.par4 = None       # 参数 4 (Parameter 4)
        self.par5 = None       # 参数 5 (Parameter 5)
        self.par6 = None       # 参数 6 (Parameter 6)        
        self.winval = None     # 备注 (Remark)     
        self.allnum=0
        self.winnum =0
        self.winsum = 0
        self.basic.log_index = "stock_tradepar-main"  # Elasticsearch索引名称

class HistoryLogEntry(LogEntry):
    def __init__(self):
        super().__init__()     
        self.cid = None       # 用户 (User ID)
        self.kind = None      # 算法类型 (Algorithm type)
        self.line = 'd'       # 日线 (Default to daily line, could be week or hour)
        self.card = None      # 交易代码 (Stock or asset code)
        self.dtime = None     # 交易时间 (Trade timestamp)
        self.price = None     # 交易价格 (Trade price)
        self.num = None       # 交易数量 (Quantity of the trade)
        self.reason = None    # 交易原因 (Reason for the trade)
        self.winval = None    # 赢利 (Profit value)
        self.remark = None    # 备注 (Remark)
        self.basic.log_index = "stock_history-main" 

class TradeLogEntry(LogEntry):
    def __init__(self):
        super().__init__()        
        self.cid = None#用户
        self.kind = None#算法
        self.line = 'd'#日线 （后面可加上周线 或小时线）
        self.card = None
        self.lastval=0.00
        self.par = 8.00
        self.par2 = 0.00
        self.par3 = 0.00
        self.par4 = 0.00
        self.par5 = 0.00
        self.par6 = 0.00#支持6个参数的调整 
        self.winval = 0.00#算法利润
        self.dval = '0001-01-01 00:00:00'#跑到哪天了
        self.val1 = 0.00
        self.val2 = 0.00
        self.val3 = 0.00
        self.val4 = 0.00
        self.val5 = 0.00
        self.val6 = 0.00
        self.val7 = 0.00
        self.val8 = 0.00
        self.val9 = 0.00#支持9个策略暂存值
        self.stoptime = '1900-01-01 00:00:00'#2个多空停止交易时间
        self.stoptime2 = '1900-01-01 00:00:00'#算法可能在本日或N个周期内不考虑平仓
        self.upval = 0.00
        self.upnum = 0
        self.downnum = 0
        self.downval = 0.00#持仓多空价格
        self.status = ''#当前状态好象没用
        self.douser = ''#分布式用户名 这个是算算法的
        self.worker = ''#分布式用户名(这个是算优化参数的)  
        self.optimizetime = '1900-01-01 00:00:00'#优化时间
        self.iswarnwx = 0#达到算法条件是否微信告警
        self.winnum = 0
        self.allnum = 0
        self.winsum = 0.00#总平仓数 胜平仓数 赢利总和(不计亏损)算凯利公式
        self.todayopen = False#今天是否有开仓 用于实盘跟踪            
        self.upby = ''
    

        #self.event.event_id = self.card+self.kind
        self.basic.log_index = "stock_trade-main"
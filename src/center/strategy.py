class Strategy:
    def __init__(self, s78, debug=True):
        self.s78 = s78
        self.debug = debug
        self.cid = None
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
        self.todayopen = 0
        self.douser = ''
        self.upby = ''
        self.uptime = None
        self.id = ''


    def go(self, rv, rt, *args):
        raise NotImplementedError("Strategy.go() must be overridden.")
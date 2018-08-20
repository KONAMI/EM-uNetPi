class dstat_plugin(dstat):
    """
    Example "Hello world!" output plugin for aspiring Dstat developers.
    """

    def __init__(self):
        self.name = 'tc param'
        self.nick = ('delayUP','lossUP','delayDW','lossDW')
        self.vars = ('delayUPValue','lossUPValue','delayDWValue','lossDWValue')
        self.type = 's'
        self.width = 8
        self.scale = 0

    def Update(self):
        import commands
        import re

        current  = commands.getoutput("tc qdisc show dev eth0")

        pattern  = re.compile(r'delay.*?ms')
        matchObj = pattern.search(current)
        if matchObj:
            	param = matchObj.group().split()
		self.val['delayUPValue'] = param[1] 
        else:
		self.val['delayUPValue'] = '0.0ms'
        pattern  = re.compile(r'loss.*?\%')
        matchObj = pattern.search(current)
        if matchObj:
		param = matchObj.group().split()
		self.val['lossUPValue'] = param[1] 
        else:
		self.val['lossUPValue'] = '0%'

	current  = commands.getoutput("tc qdisc show dev wlan0")

        pattern  = re.compile(r'delay.*?ms')
        matchObj = pattern.search(current)
        if matchObj:
            	param = matchObj.group().split()
		self.val['delayDWValue'] = param[1] 
        else:
		self.val['delayDWValue'] = '0.0ms'
        pattern  = re.compile(r'loss.*?\%')
        matchObj = pattern.search(current)
        if matchObj:
		param = matchObj.group().split()
		self.val['lossDWValue'] = param[1] 
        else:
		self.val['lossDWValue'] = '0%'

    def extract(self):
        self.Update()


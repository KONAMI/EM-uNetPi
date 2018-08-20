class dstat_plugin(dstat):

	def __init__(self):
		self.name = 'temp'
		self.nick = ('cpu',)
		self.vars = ('cpuTempValue',)
		self.type = 's'
		self.width = 8
		self.scale = 0

	def Update(self):
		import commands
		import re

		current  = commands.getoutput("vcgencmd measure_temp")

		pattern  = re.compile(r'temp=.*')
		matchObj = pattern.search(current)
		if matchObj:
			param = matchObj.group().split("=")[1].split("'")
			self.val['cpuTempValue'] = param[0] 
		else:
			self.val['cpuTempValue'] = '0.0'

	def extract(self):
		self.Update()


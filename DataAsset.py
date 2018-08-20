class CTX:

	def __init__(self):
		#
		# Local Context
		#
		self.tick                 = 0
		self.current              = 0		
		self.debug                = False
		self.currentReplayData    = ""		

		#
		# Local Config
		#
		self.replayDataPath       = "/usr/local/wanem/dat"
		self.connectivityCheckUrl = "https://github.com"
		self.infoApiUrl           = "https://raw.githubusercontent.com/KONAMI/EM-uNetPi/master/misc/api/ApiInfo.json"
		self.copyright            = "Powered by Sato_Motohiko"
		self.revision             = "PLA-A-2018082001"
		
		#
		# Local Config ( Runtime Writeable )
		#
		self.LAN_MODE_WLAN   = 1
		self.LAN_MODE_HYBRID = 2
		self.lanMode         = self.LAN_MODE_WLAN
		#self.lanMode         = self.LAN_MODE_HYBRID
		self.wifiDongleExist = False

		#
		# Remote Config ( from InfoApi )
		#
		self.apiStatus              = 2
		self.activityReportApiUrl   = ""
		self.activityReportApiKey   = ""
		self.dhcpClientReportApiUrl = ""
		self.dhcpClientReportApiKey = ""

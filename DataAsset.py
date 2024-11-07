class CTX:
    def __init__(self):
        #
        # Local Context
        #
        self.tick = 0
        self.current = 0
        self.debug = False
        self.currentReplayData = ""
        self.httpsProxy = ""
        #
        # Local Config
        #
        self.replayDataPath = "/usr/local/wanem/dat"
        self.connectivityCheckUrl = "https://raw.githubusercontent.com/KONAMI/EM-uNetPi/master/misc/api/ApiInfo.json"
        self.infoApiUrl = "https://raw.githubusercontent.com/KONAMI/EM-uNetPi/master/misc/api/ApiInfo.json"
        self.copyright = "Powered by Sato_Motohiko"
        self.revision = "PLA-A-2024110701"
        self.lanV6Addr = "fd00:c0a8:1401::1"
        self.wlanV6Addr = "fd00:c0a8:1501::1"
        
        #
        # Local Config ( Runtime Writeable )
        #
        self.LAN_MODE_WLAN = 1
        self.LAN_MODE_HYBRID = 2
        self.lanMode = self.LAN_MODE_HYBRID
        #self.lanMode         = self.LAN_MODE_HYBRID
        self.wifiDongleExist = False
        self.v6Available = False
        self.eth1Exist = False
        self.eth2Exist = False
        
        #
        # Remote Config ( from InfoApi )
        #
        self.apiStatus = 2
        self.activityReportApiUrl = ""
        self.activityReportApiKey = ""
        self.dhcpClientReportApiUrl = ""
        self.dhcpClientReportApiKey = ""

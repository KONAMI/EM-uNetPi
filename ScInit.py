import sys, getopt, struct, time, termios, fcntl, sys, os, colorsys, threading, datetime, subprocess, json
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/fbtft')
from RenderManager import RenderManager
from WanemManager import WanemManager
from HttpUtil import HttpUtil
from LogReporter import LogReporter
from ScBase import ScBase
from gfx import Rect
from DataAsset import CTX
from pprint import pprint
from V6Util import V6Util

class ScInit(ScBase):
    def __init__(self, pCTX, pRender, pWanem):
        super(ScInit, self).__init__(pCTX, pRender, pWanem)
        self.tickCnt = 0
        self.tickDuration = 3
        self.prevTickCnt = -1
        self.stepLabel = [".", "..", "...", "OK", "ERR", "N/A"]
        self.worker = None
        self.workerRet = 0

        self.STATE_CHK_NETWORK = 1
        self.STATE_GET_INFO = 2
        self.STATE_CHK_EMULATE_DAT = 3
        self.STATE_CHK_WIFI_DONGLE = 4
        self.STATE_SETUP_AP = 5
        self.STATE_CHK_LAN_INTERFACE = 6
        self.STATE_CHK_V6_ENV = 7
        self.STATE_CRASH = 8

    def CheckHttpConnectivity(self):
        print("-------------------------------")
        while HttpUtil.CheckConnectivity(self.pCTX.connectivityCheckUrl, 1,
                                         self.pCTX.httpsProxy) == False:
            time.sleep(1)
        self.workerRet = 3
        print("-------------------------------")
        return

    def GetApiInfo(self):
        apiUrl = self.pCTX.infoApiUrl
        savePath = "/tmp/WanemApiInfo.json"
        print("-------------------------------")
        while HttpUtil.Get(apiUrl, savePath, 1, self.pCTX.httpsProxy) == False:
            time.sleep(1)
        file = open(savePath)
        dat = json.load(file)
        file.close()
        #pprint(dat)
        self.pCTX.apiStatus = dat["status"]["maintStatus"]
        self.workerRet = 3
        print("-------------------------------")
        return

    def CheckWanemDat(self):
        print("-------------------------------")
        cmd = "php /home/pi/EM-uNetPi/scripts/php/SyncDat.php"
        print(cmd)
        ret = False

        try:
            subprocess.check_call(cmd.strip().split(" "))
            ret = True
            self.workerRet = 3
        except subprocess.CalledProcessError:
            ret = False
            self.workerRet = 4

        print(str(ret))
        print("-------------------------------")
        return

    def SetupAP(self):
        print("-------------------------------")
        cmd = "php /home/pi/EM-uNetPi/scripts/php/UpdateNetworkManagerConf.php wanem-" + self.GetSelfId()
        print(cmd)
        ret = False

        try:
            subprocess.check_call(cmd.strip().split(" "))
            ret = True
            self.workerRet = 3
        except subprocess.CalledProcessError:
            ret = False
            self.workerRet = 4

        print(str(ret))
        print("-------------------------------")
        return

    def CheckLanInterface(self):
        print("-------------------------------")
        cmd = "ifconfig eth1"
        try:
            subprocess.check_call(cmd.strip().split(" "))
            self.workerRet = 3
            self.pCTX.eth1Exist = True
        except subprocess.CalledProcessError:
            self.workerRet = 4
            return
        
        cmd = "ifconfig eth2"
        try:
            subprocess.check_call(cmd.strip().split(" "))
            self.workerRet = 3
            self.pCTX.eth2Exist = True
        except subprocess.CalledProcessError:
            self.workerRet = 4
            
        print("-------------------------------")
        return

    def CheckV6Env(self):
        print("-------------------------------")
        if V6Util.IsV6Enabled() == True:
            addrList = V6Util.GetGua()
            if len(addrList) > 0:
                print("GUA Nr " + str(len(addrList)))
                for addr in addrList:
                    print("GUA >> " + addr)
                self.workerRet = 3
                self.pCTX.v6Available = True
            else:
                self.workerRet = 5
                self.pCTX.v6Available = False
        else :
            self.workerRet = 5
            self.pCTX.v6Available = False

        print("-------------------------------")
        return
    
    def CheckWifiDongle(self):
        print("-------------------------------")

        # Dummy Boot for Recognize WiFi Dongle
        cmd = "php /home/pi/EM-uNetPi/scripts/php/UpdateNetworkManagerConf.php wanem-" + self.GetSelfId()
        try:
            subprocess.check_call(cmd.strip().split(" "))
            ret = True
        except subprocess.CalledProcessError:
            ret = False

        retryLimit = 10
        retryCnt = 0

        while retryCnt < retryLimit:
            
            cmd = "lsusb -d 35bc:0108"
            ret = False

            try:
                subprocess.check_call(cmd.strip().split(" "))
                self.pCTX.wifiDongleExist = True
                break
            except subprocess.CalledProcessError:
                self.pCTX.wifiDongleExist = False

            retryCnt += 1
            time.sleep(5)

        print("WifiDongle Exist : " + str(self.pCTX.wifiDongleExist))
            
        if self.pCTX.wifiDongleExist == True:
            self.workerRet = 3
        else:
            self.workerRet = 4

        cmd = "cat /etc/wanem/apmode.prop"
        try:
            currentApMode = int(
                subprocess.check_output(cmd.strip().split(" ")).decode().replace(
                    '\n', ''))
        except subprocess.CalledProcessError:
            currentApMode = 0

        print("-------------------------------")
        return

    def Start(self):
        super(ScInit, self).Start()

        ##[ INIT STATE ]################################################################

        self.state = self.STATE_TERM
        self.nextScene = "Menu"
        #self.nextScene = "ManualEx"
        self.state = self.STATE_CHK_NETWORK
        #self.state = self.STATE_CHK_EMULATE_DAT
        #self.workerRet = 0
        self.worker = threading.Thread(target=self.CheckHttpConnectivity,
                                       args=())
        #self.worker = threading.Thread(target=self.CheckWanemDat, args=())
        self.worker.start()

        ##[ RENDER ]################################################################

        self.pRender.UpdateTitle("Boot - rev : " + self.pCTX.revision)

        c = yellow = self.pRender.fb.rgb(255, 255, 0)
        self.pRender.fb.draw.rect(c, Rect(0, 54, self.pRender.xres, 1), 0)

        label = "%-18s [     ]" % "CHK NETWORK"
        self.pRender.fb.putstr(20, 74 + 32 * 0, label, self.pRender.W, 2)
        label = "%-18s [     ]" % "GET API INFO"
        self.pRender.fb.putstr(20, 74 + 32 * 1, label, self.pRender.W, 2)
        label = "%-18s [     ]" % "IPv6 ENV CHECK"
        self.pRender.fb.putstr(20, 74 + 32 * 2, label, self.pRender.W, 2)
        label = "%-18s [     ]" % "CHK WIFI DONGLE"
        self.pRender.fb.putstr(20, 74 + 32 * 3, label, self.pRender.W, 2)
        label = "%-18s [     ]" % "SETUP AP"
        self.pRender.fb.putstr(20, 74 + 32 * 4, label, self.pRender.W, 2)
        label = "%-18s [     ]" % "CHK LAN INTERFACE"
        self.pRender.fb.putstr(20, 74 + 32 * 5, label, self.pRender.W, 2)

        self.pRender.fb.putstr(273, 74 + 32 * 0, " - ", self.pRender.W, 2)
        self.pRender.fb.putstr(273, 74 + 32 * 1, " - ", self.pRender.W, 2)
        self.pRender.fb.putstr(273, 74 + 32 * 2, " - ", self.pRender.W, 2)
        self.pRender.fb.putstr(273, 74 + 32 * 3, " - ", self.pRender.W, 2)
        self.pRender.fb.putstr(273, 74 + 32 * 4, " - ", self.pRender.W, 2)
        self.pRender.fb.putstr(273, 74 + 32 * 5, " - ", self.pRender.W, 2)
        #self.pRender.fb.draw.rect(self.pRender.W, Rect(271, 74, 40, 16), 0)
        
        return

    def ShowFailMessage(self, msg):
        self.pRender.fb.putstr(
            48, 294 - 16,
            msg,
            self.pRender.R, 2)
    
    def Update(self):
        if self.pCTX.tick == 1:
            self.tickCnt = (self.tickCnt + 1) % self.tickDuration

        if self.state == self.STATE_CHK_NETWORK:
            if self.worker.is_alive() == False:
                self.worker.join()
                self.UpdateProgress(0, self.workerRet)
                self.state = self.STATE_GET_INFO
                self.worker = None
                self.workerRet = 0
                self.worker = threading.Thread(target=self.GetApiInfo, args=())
                self.worker.start()
            else:
                if self.tickCnt != self.prevTickCnt:
                    self.UpdateProgress(0, self.tickCnt)

        elif self.state == self.STATE_GET_INFO:
            if self.worker.is_alive() == False:
                self.worker.join()
                self.UpdateProgress(1, self.workerRet)
                self.state = self.STATE_CHK_V6_ENV
                self.worker = None
                self.workerRet = 0
                self.worker = threading.Thread(target=self.CheckV6Env,
                                               args=())
                self.worker.start()
            else:
                if self.tickCnt != self.prevTickCnt:
                    self.UpdateProgress(1, self.tickCnt)

        elif self.state == self.STATE_CHK_V6_ENV:
            if self.worker.is_alive() == False:
                self.worker.join()
                self.UpdateProgress(2, self.workerRet)
                self.state = self.STATE_CHK_WIFI_DONGLE
                self.worker = None
                self.workerRet = 0
                self.worker = threading.Thread(target=self.CheckWifiDongle,
                                               args=())
                self.worker.start()
            else:
                if self.tickCnt != self.prevTickCnt:
                    self.UpdateProgress(2, self.tickCnt)
                    
        elif self.state == self.STATE_CHK_WIFI_DONGLE:
            if self.worker.is_alive() == False:
                self.worker.join()
                self.UpdateProgress(3, self.workerRet)
                if self.pCTX.wifiDongleExist == True:
                    self.state = self.STATE_SETUP_AP
                    self.worker = None
                    self.workerRet = 0
                    self.worker = threading.Thread(target=self.SetupAP, args=())
                    self.worker.start()
                else: 
                    self.ShowFailMessage("Boot Fail >> WiFi Dongle Error.")                   
            else:
                if self.tickCnt != self.prevTickCnt:
                    self.UpdateProgress(3, self.tickCnt)

        elif self.state == self.STATE_SETUP_AP:
            if self.worker.is_alive() == False:
                self.worker.join()
                self.UpdateProgress(4, self.workerRet)
                self.state = self.STATE_CHK_LAN_INTERFACE
                self.worker = None
                self.workerRet = 0
                self.worker = threading.Thread(target=self.CheckLanInterface,
                                               args=())
                self.worker.start()
            else:
                if self.tickCnt != self.prevTickCnt:
                    self.UpdateProgress(4, self.tickCnt)

        elif self.state == self.STATE_CHK_LAN_INTERFACE:
            if self.worker.is_alive() == False:
                self.worker.join()
                self.UpdateProgress(5, self.workerRet)

                if self.pCTX.eth1Exist == False:
                    self.ShowFailMessage("Boot Fail >> LAN Adapter 1 Error.")
                elif self.pCTX.eth2Exist == False:
                    self.ShowFailMessage("Boot Fail >> LAN Adapter 2 Error.")
                else:
                    # init v6
                    if self.pCTX.v6Available == True:
                        self.LaunchV6Service()
                    else:
                        self.ForceOverwriteV4OnlySetting()                
                
                    if self.pCTX.apiStatus == 0:
                        LogReporter.SendLog(self.pCTX, 1, "StartUp")
                    
                    self.state = self.STATE_TERM
                    self.worker = None
            else:
                if self.tickCnt != self.prevTickCnt:
                    self.UpdateProgress(5, self.tickCnt)
                    
        self.prevTickCnt = self.tickCnt

        return

    def LaunchV6Service(self):

        cmd = "cat /etc/iptables.ipv6.nat"        
        try:
            ip6tablesConf = subprocess.Popen(cmd.strip().split(" "),
                                             stdout=subprocess.PIPE)
            print("Read ip6tables conf Success")
        except subprocess.CalledProcessError:
            print("Read ip6tables conf Fail")

        try:            
            subprocess.Popen("ip6tables-restore",shell=True,
                             stdin=ip6tablesConf.stdout)
            print("Apply ip6tables Conf Success")
        except subprocess.CalledProcessError:
            print("Apply ip6tables Conf Fail")

        cmd = "systemctl start radvd"
        try:
            subprocess.check_call(cmd.strip().split(" "))
            print("Launch radvd Success")
        except subprocess.CalledProcessError:
            print("Launch radvd Fail")

    def ForceOverwriteV4OnlySetting(self):
        print("Force Overwrite V4Only Setting")
        
        cmd = "cp /etc/iptables.ipv6.nat.type0 /etc/iptables.ipv6.nat"
        cmd2 = "php /home/pi/EM-uNetPi/scripts/php/IPv6Switcher.php 1"
        
        try:
            subprocess.check_call(cmd.strip().split(" "))
            print("Update V6 NAPT Mode Success")
        except subprocess.CalledProcessError:
            print("Update V6 NAPT Mode Fail")

        try:
            subprocess.check_call(cmd2.strip().split(" "))
            print("Update V6 Mode Success")
        except subprocess.CalledProcessError:
            print("Update V6 Mode Fail")
        
    def UpdateProgress(self, target, step):
        if step == 3:
            c = self.pRender.G
        elif step == 4 or step == 5:
            c = self.pRender.R
        else:
            c = self.pRender.W
        self.pRender.fb.draw.rect(self.pRender.N,
                                  Rect(271, 74 + 32 * target, 40, 16), 0)
        self.pRender.fb.putstr(273, 74 + 32 * target, self.stepLabel[step], c,
                               2)

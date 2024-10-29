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


class ScInit(ScBase):
    def __init__(self, pCTX, pRender, pWanem):
        super(ScInit, self).__init__(pCTX, pRender, pWanem)
        self.tickCnt = 0
        self.tickDuration = 3
        self.prevTickCnt = -1
        self.stepLabel = [".", "..", "...", "OK", "ERR"]
        self.worker = None
        self.workerRet = 0

        self.STATE_CHK_NETWORK = 1
        self.STATE_GET_INFO = 2
        self.STATE_CHK_EMULATE_DAT = 3
        self.STATE_CHK_WIFI_DONGLE = 4
        self.STATE_SETUP_AP = 5
        self.STATE_CHK_LAN_INTERFACE = 6

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
        ret = False

        try:
            subprocess.check_call(cmd.strip().split(" "))
            self.pCTX.lanMode = self.pCTX.LAN_MODE_HYBRID
            ret = True
            self.workerRet = 3
        except subprocess.CalledProcessError:
            self.pCTX.lanMode = self.pCTX.LAN_MODE_WLAN
            ret = True
            self.workerRet = 3

        print(str(ret))
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

        cmd = "lsusb -d 35bc:0108"
        ret = False

        try:
            subprocess.check_call(cmd.strip().split(" "))
            self.pCTX.wifiDongleExist = True
            ret = True
            self.workerRet = 3
        except subprocess.CalledProcessError:
            self.pCTX.wifiDongleExist = False
            ret = True
            self.workerRet = 3

        cmd = "cat /etc/wanem/apmode.prop"
        try:
            currentApMode = int(
                subprocess.check_output(cmd.strip().split(" ")).decode().replace(
                    '\n', ''))
        except subprocess.CalledProcessError:
            currentApMode = 0

        print("WifiDongle Exist : " + str(self.pCTX.wifiDongleExist))
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
        label = "%-18s [     ]" % "CHK WIFI DONGLE"
        self.pRender.fb.putstr(20, 74 + 32 * 2, label, self.pRender.W, 2)
        label = "%-18s [     ]" % "SETUP AP"
        self.pRender.fb.putstr(20, 74 + 32 * 3, label, self.pRender.W, 2)
        label = "%-18s [     ]" % "CHK LAN INTERFACE"
        self.pRender.fb.putstr(20, 74 + 32 * 4, label, self.pRender.W, 2)

        self.pRender.fb.putstr(273, 74 + 32 * 0, " - ", self.pRender.W, 2)
        self.pRender.fb.putstr(273, 74 + 32 * 1, " - ", self.pRender.W, 2)
        self.pRender.fb.putstr(273, 74 + 32 * 2, " - ", self.pRender.W, 2)
        self.pRender.fb.putstr(273, 74 + 32 * 3, " - ", self.pRender.W, 2)
        self.pRender.fb.putstr(273, 74 + 32 * 4, " - ", self.pRender.W, 2)
        #self.pRender.fb.draw.rect(self.pRender.W, Rect(271, 74, 40, 16), 0)

        return

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
                self.state = self.STATE_CHK_WIFI_DONGLE
                self.worker = None
                self.workerRet = 0
                self.worker = threading.Thread(target=self.CheckWifiDongle,
                                               args=())
                self.worker.start()
            else:
                if self.tickCnt != self.prevTickCnt:
                    self.UpdateProgress(1, self.tickCnt)

        elif self.state == self.STATE_CHK_WIFI_DONGLE:
            if self.worker.is_alive() == False:
                self.worker.join()
                self.UpdateProgress(2, self.workerRet)
                self.state = self.STATE_SETUP_AP
                self.worker = None
                self.workerRet = 0
                self.worker = threading.Thread(target=self.SetupAP, args=())
                self.worker.start()
            else:
                if self.tickCnt != self.prevTickCnt:
                    self.UpdateProgress(2, self.tickCnt)

        elif self.state == self.STATE_SETUP_AP:
            if self.worker.is_alive() == False:
                self.worker.join()
                self.UpdateProgress(3, self.workerRet)
                self.state = self.STATE_CHK_LAN_INTERFACE
                self.worker = None
                self.workerRet = 0
                self.worker = threading.Thread(target=self.CheckLanInterface,
                                               args=())
                self.worker.start()
            else:
                if self.tickCnt != self.prevTickCnt:
                    self.UpdateProgress(3, self.tickCnt)

        elif self.state == self.STATE_CHK_LAN_INTERFACE:
            if self.worker.is_alive() == False:
                self.worker.join()
                self.UpdateProgress(4, self.workerRet)

                if self.pCTX.apiStatus == 0:
                    LogReporter.SendLog(self.pCTX, 1, "StartUp")

                self.state = self.STATE_TERM
                self.worker = None
                print(self.pCTX.lanMode)
            else:
                if self.tickCnt != self.prevTickCnt:
                    self.UpdateProgress(4, self.tickCnt)

        self.prevTickCnt = self.tickCnt

        return

    def UpdateProgress(self, target, step):
        if step == 3:
            c = self.pRender.G
        elif step == 4:
            c = self.pRender.R
        else:
            c = self.pRender.W
        self.pRender.fb.draw.rect(self.pRender.N,
                                  Rect(271, 74 + 32 * target, 40, 16), 0)
        self.pRender.fb.putstr(273, 74 + 32 * target, self.stepLabel[step], c,
                               2)

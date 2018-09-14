import sys, getopt, struct, time, termios, fcntl, sys, os, colorsys, threading, time, datetime, subprocess, socket, errno, select, json
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/fbtft')
from RenderManager import RenderManager
from WanemManager import WanemManager
from ScBase import ScBase
from gfx import Rect
from DataAsset import CTX
from fcntl import ioctl


class ScRemoteApi(ScBase):
    def __init__(self, pCTX, pRender, pWanem):
        super(ScRemoteApi, self).__init__(pCTX, pRender, pWanem)
        self.ptDef.insert(
            0, self.CreateTocuhDef("BtMenu", 468, 29, 62, 42, self.BtHandler))

    def BtHandler(self, key):
        print "BtHandler" + key
        if key == "BtMenu":
            self.pWanem.Clear()
            self.nextScene = "Menu"
            self.state = self.STATE_TERM
            self.DestroyApiSocket()

    def CreateApiSocket(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind(("", 10393))
        self.sock.setblocking(0)
        self.socklist = []
        self.socklist.append(self.sock)

    def DestroyApiSocket(self):
        self.sock.close()

    def Update(self):
        if self.state == self.STATE_INIT:
            read_sockets, write_sockets, error_sockets = select.select(
                self.socklist, [], [], 0)
            for s in read_sockets:
                if s == self.sock:
                    try:
                        rBuf, peer = self.sock.recvfrom(self.rBufSize)
                        self.ApplyApiCall(rBuf.decode().strip())
                        #self.pRender.UpdateSubTitle(rBuf.decode().strip())
                        resp = '{"status":"E_OK"}'.encode('utf-8')
                        self.sock.sendto(resp, peer)
                    except socket.error, v:
                        errorcode = v[0]
                        print("socket recv error. >> " + errorcode)
        return

    def ApplyApiCall(self, query):
        isUpdateBand = 0
        isUpdateDelay = 0
        isUpdateLoss = 0
        isUpdateDiscon = 0

        #todo aplly diff Update
        #print ("ApplyApiCall >> " + query)
        req = json.loads(query)
        self.upBand = req["bandUp"]
        self.dwBand = req["bandDw"]
        self.upDelay = req["delayUp"]
        self.dwDelay = req["delayDw"]
        self.upLoss = req["lossUp"]
        self.dwLoss = req["lossDw"]
        self.upDiscon = req["disconnUp"]
        self.dwDiscon = req["disconnDw"]

        upLoss = self.upLoss
        dwLoss = self.dwLoss

        if self.upDiscon != 0:
            upLoss = 100
        if self.dwDiscon != 0:
            dwLoss = 100

        self.pWanem.DirectUpdateEx2(self.upBand, self.dwBand, self.upDelay,
                                    self.dwDelay, upLoss, dwLoss)
        self.RenderParamOnly(0, 0, self.upBand, self.dwBand)
        self.RenderParamOnly(1, 0, self.upDelay, self.dwDelay)
        self.RenderParamOnly(2, 0, self.upLoss, self.dwLoss)
        self.RenderParamOnly(3, 1, self.upDiscon, self.dwDiscon)

    def Start(self):
        super(ScRemoteApi, self).Start()

        ##[ PARAM ]################################################################

        self.upBand = 8096
        self.dwBand = 8096
        self.upDelay = 0
        self.dwDelay = 0
        self.upLoss = 0
        self.dwLoss = 0
        self.upDiscon = 0
        self.dwDiscon = 0

        self.rBufSize = 4096
        self.bindPort = 10393

        ##[ RENDER ]################################################################

        self.pRender.UpdateTitle("WAN Emulation - API Control")
        self.pRender.UpdateSubTitle("")

        c = yellow = self.pRender.fb.rgb(255, 255, 0)
        self.pRender.fb.draw.rect(c, Rect(0, 54, self.pRender.xres, 1), 0)
        self.pRender.fb.draw.rect(c, Rect(0, 74, self.pRender.xres, 1), 0)
        self.pRender.fb.draw.rect(c, Rect(0, 54, 10 + 60, 20), 0)
        self.pRender.fb.draw.rect(c, Rect(480 - 10, 54, 10, 20), 0)
        self.pRender.fb.draw.rect(c, Rect(342, 74, 1, self.pRender.yres - 74),
                                  0)
        self.pRender.fb.putstr(26, 54 + 7, ">>>", self.pRender.N, 1)

        self.RenderBackBt(True)

        self.CreateApiSocket()
        ifreq = struct.pack('16s16x', 'eth1')
        SIOCGIFADDR = 0x8915  # oh... not defined... orz
        ifaddr = ioctl(self.sock.fileno(), SIOCGIFADDR, ifreq)
        _, sa_family, port, in_addr = struct.unpack('16sHH4s8x', ifaddr)
        #print socket.inet_ntoa(in_addr)
        self.pRender.UpdateSubTitle("API Endpoint >> " +
                                    socket.inet_ntoa(in_addr) + ":" +
                                    str(self.bindPort))

        self.RenderParamBar(0, 0, "Band", self.upBand, self.dwBand, "kbps")
        self.RenderParamBar(1, 0, "Delay", self.upDelay, self.dwDelay, "msec")
        self.RenderParamBar(2, 0, "Loss", self.upLoss, self.upLoss, "   %")
        self.RenderParamBar(3, 1, "Discon")
        #self.RenderParamOnly(0, 0, 1024, 1024)
        #self.RenderParamOnly(1, 0, 100,   300)
        #self.RenderParamOnly(2, 0,   5,     5)
        #c = self.pRender.ConvRgb(0.32,0.4,0.2)
        #self.pRender.fb.putstr(80, 96, "    Coinfig Param List    ", c, 2)

        self.pWanem.ClearEx2()
        self.pWanem.DirectApplyEx2(self.upBand, self.dwBand, self.upDelay,
                                   self.dwDelay, self.upLoss, self.dwLoss)

        return

    def RenderParamOnly(self, idx, isToggle, up, down):
        if isToggle == 0:
            c = self.pRender.ConvRgb(0.32, 0.1, 1)
            self.pRender.fb.draw.rect(
                c, Rect(20 + 102 + 106 + 12, 86 + 22 + idx * 58, 50, 16), 0)
            self.pRender.fb.draw.rect(
                c, Rect(20 + 102 + 12, 86 + 22 + idx * 58, 50, 16), 0)
            c = self.pRender.ConvRgb(0.32, 0.4, 0.4)
            self.pRender.fb.putstr(20 + 102 + 12, 86 + 22 + idx * 58,
                                   "%04d" % up, c, 2)
            self.pRender.fb.putstr(20 + 102 + 106 + 12, 86 + 22 + idx * 58,
                                   "%04d" % down, c, 2)
        else:
            if up == 0:
                c = self.pRender.ConvRgb(0.32, 0.1, 1)
            else:
                c = self.pRender.ConvRgb(0.92, 0.8, 1)
            self.pRender.fb.draw.rect(
                c, Rect(20 + 102 + 12, 86 + 22 + idx * 58, 50, 16), 0)

            if down == 0:
                c = self.pRender.ConvRgb(0.32, 0.1, 1)
            else:
                c = self.pRender.ConvRgb(0.92, 0.8, 1)
            self.pRender.fb.draw.rect(
                c, Rect(20 + 102 + 106 + 12, 86 + 22 + idx * 58, 50, 16), 0)

        return

    def RenderParamBar(self, idx, isToggle, label, up=0, down=0, unit=""):
        c = self.pRender.ConvRgb(0.32, 0.4, 0.8)
        self.pRender.fb.draw.rect(c, Rect(12, 86 + idx * 58, 320, 48), 0)
        c = self.pRender.ConvRgb(0.32, 0.1, 1)
        self.pRender.fb.draw.rect(c, Rect(20 + 102, 86 + 12 + idx * 58, 100,
                                          32), 0)
        self.pRender.fb.draw.rect(
            c, Rect(20 + 102 + 106, 86 + 12 + idx * 58, 100, 32), 0)
        self.pRender.fb.putstr(20 + 102, 86 + 2 + idx * 58, "UP", c, 1)
        self.pRender.fb.putstr(20 + 102 + 106, 86 + 2 + idx * 58, "DOWN", c, 1)
        self.pRender.fb.putstr(20 + 2, 86 + 22 + idx * 58, label + "> ", c, 2)

        c = self.pRender.ConvRgb(0.32, 0.3, 1)
        self.pRender.fb.draw.rect(c, Rect(20 + 2, 86 + 7 + idx * 58, 84, 6), 0)

        if isToggle == 0:
            c = self.pRender.ConvRgb(0.32, 0.4, 0.4)
            self.pRender.fb.putstr(20 + 102 + 70, 86 + 30 + idx * 58, unit, c,
                                   1)
            self.pRender.fb.putstr(20 + 102 + 12, 86 + 22 + idx * 58,
                                   "%04d" % up, c, 2)
            self.pRender.fb.putstr(20 + 102 + 106 + 70, 86 + 30 + idx * 58,
                                   unit, c, 1)
            self.pRender.fb.putstr(20 + 102 + 106 + 12, 86 + 22 + idx * 58,
                                   "%04d" % down, c, 2)

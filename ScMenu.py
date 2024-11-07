import sys, getopt, struct, time, termios, fcntl, sys, os, colorsys, threading, time, datetime, subprocess
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/fbtft')
from RenderManager import RenderManager
from WanemManager import WanemManager
from ScBase import ScBase
from gfx import Rect
from DataAsset import CTX


class ScMenu(ScBase):
    def __init__(self, pCTX, pRender, pWanem):
        super(ScMenu, self).__init__(pCTX, pRender, pWanem)
        #self.ptDef.insert(0, self.CreateTocuhDef("BtManual", 434,      132, 180, 132, self.BtHandler))
        self.ptDef.insert(
            0, self.CreateTocuhDef("BtPreset", 429, 210, 81, 81,
                                   self.BtHandler))
        self.ptDef.insert(
            1, self.CreateTocuhDef("BtDirect", 348, 210, 81, 81,
                                   self.BtHandler))
        #self.ptDef.insert(2, self.CreateTocuhDef("BtReplay", 434-204,  95, 180, 132, self.BtHandler))
        if self.pCTX.apiStatus == 0:
            self.ptDef.insert(
                2,
                self.CreateTocuhDef("BtReplay", 434 - 204, 95, 180, 50,
                                    self.BtHandler))
        self.ptDef.insert(
            3, self.CreateTocuhDef("BtInit", 468, 29, 62, 42, self.BtHandler))
        self.ptDef.insert(
            4,
            self.CreateTocuhDef("BtSetting", 434 - 204, 233, 180, 50,
                                self.BtHandler))
        self.ptDef.insert(
            5,
            self.CreateTocuhDef("BtRemote", 434 - 204, 164, 180, 50,
                                self.BtHandler))

    def BtHandler(self, key):
        #print "BtHandler" + key
        if key == "BtManual":
            self.nextScene = "Manual"
            self.state = self.STATE_TERM
        elif key == "BtPreset":
            self.nextScene = "Manual"
            self.state = self.STATE_TERM
        elif key == "BtDirect":
            self.nextScene = "ManualEx2"
            self.state = self.STATE_TERM
        elif key == "BtReplay":
            self.nextScene = "Replay"
            self.state = self.STATE_TERM
        elif key == "BtSetting":
            self.nextScene = "Setting"
            self.state = self.STATE_TERM
        #elif key == "BtInit":
            #self.nextScene = "Init"
            #self.state = self.STATE_TERM
        elif key == "BtRemote":
            self.nextScene = "RemoteApi"
            self.state = self.STATE_TERM

    def Start(self):
        super(ScMenu, self).Start()

        ##[ RENDER ]################################################################

        self.pRender.UpdateTitle("Mode Select")

        c = yellow = self.pRender.fb.rgb(255, 255, 0)
        self.pRender.fb.draw.rect(c, Rect(0, 54, self.pRender.xres, 1), 0)

        #self.RenderBackBt(True)

        c = self.pRender.ConvRgb(0.62, 0.4, 1.0)
        self.pRender.fb.draw.rect(c, Rect(48, 90, 180, 200), 0)
        c = self.pRender.ConvRgb(0.62, 0.4, 0.4)
        self.pRender.fb.draw.rect(c, Rect(48 + 10, 120 + 70 - 50, 160, 40), 0)
        self.pRender.fb.putstr(48 + 22, 120 + 26 - 40, "Manual Mode", c, 2)
        self.pRender.fb.putstr(133, 120 + 26 + 36, "v", c, 2)
        c = self.pRender.ConvRgb(0.62, 0.2, 1.0)
        self.pRender.fb.putstr(48 + 22 + 5, 120 + 80 - 50,
                               "WAN Emulate by manual", c, 1)
        self.pRender.fb.putstr(48 + 22 + 5, 120 + 92 - 50, "operation", c, 1)

        c = self.pRender.ConvRgb(0.62, 0.8, 0.8)
        self.pRender.fb.draw.rect(c, Rect(54, 90 + 112, 81, 76), 0)
        self.pRender.fb.draw.rect(c, Rect(54 + 87, 90 + 112, 81, 76), 0)
        c = self.pRender.ConvRgb(0.62, 0.8, 0.2)
        self.pRender.fb.draw.rect(c, Rect(54, 90 + 112 + 76, 81, 6), 0)
        self.pRender.fb.draw.rect(c, Rect(54 + 87, 90 + 112 + 76, 81, 6), 0)
        c = self.pRender.ConvRgb(0.62, 0.4, 0.4)
        self.pRender.fb.putstr(59, 222, "Preset", c, 2)
        self.pRender.fb.putstr(59, 242, " Mode ", c, 2)
        self.pRender.fb.putstr(59 + 87, 222, "Direct", c, 2)
        self.pRender.fb.putstr(59 + 87, 242, " Mode ", c, 2)

        baseX = 48 + 204
        baseY = 120 - 30
        if self.pCTX.apiStatus == 0:
            disabledDiff = 0
            menuLabel = "Replay Mode"
            menuLabelPosXOffset = 0
        else:
            disabledDiff = 0.5
            menuLabel = "N/A"
            menuLabelPosXOffset = 48

        c = self.pRender.ConvRgb(0.92, 0.8, 0.8 - disabledDiff)
        self.pRender.fb.draw.rect(c, Rect(baseX, baseY, 180, 50), 0)
        c = self.pRender.ConvRgb(0.92, 0.4, 0.4 - disabledDiff / 2)
        self.pRender.fb.draw.rect(c, Rect(baseX + 10, baseY + 29, 160, 16), 0)
        c = self.pRender.ConvRgb(0.92, 0.8, 0.2)
        self.pRender.fb.draw.rect(c, Rect(baseX, baseY + 50, 180, 10), 0)
        self.pRender.fb.putstr(baseX + 22 + menuLabelPosXOffset, baseY + 7,
                               menuLabel, c, 2)
        c = self.pRender.ConvRgb(0.92, 0.2, 1.0 - disabledDiff)
        self.pRender.fb.putstr(baseX + 22 + 3 - 10, baseY + 34,
                               "Reproduce by recorded DAT", c, 1)

        baseX = 48 + 204
        baseY = 120 - 30 + 70
        baseC = 0.12
        c = self.pRender.ConvRgb(baseC, 0.8, 0.8)
        self.pRender.fb.draw.rect(c, Rect(baseX, baseY, 180, 50), 0)
        c = self.pRender.ConvRgb(baseC, 0.4, 0.4)
        self.pRender.fb.draw.rect(c, Rect(baseX + 10, baseY + 29, 160, 16), 0)
        c = self.pRender.ConvRgb(baseC, 0.8, 0.2)
        self.pRender.fb.draw.rect(c, Rect(baseX, baseY + 50, 180, 10), 0)
        self.pRender.fb.putstr(baseX + 22 + 20, baseY + 7, "API Mode", c, 2)
        c = self.pRender.ConvRgb(baseC, 0.2, 1.0)
        self.pRender.fb.putstr(baseX + 22 + 3 - 10 + 5, baseY + 34,
                               "Contorl from Remote CLI", c, 1)

        c = self.pRender.ConvRgb(0.32, 0.4, 0.8)
        self.pRender.fb.draw.rect(c, Rect(48 + 204, 120 + 110, 180, 50), 0)
        c = self.pRender.ConvRgb(0.32, 0.4, 0.4)
        self.pRender.fb.draw.rect(
            c, Rect(48 + 10 + 204, 120 + 20 + 115 + 4, 160, 16), 0)
        c = self.pRender.ConvRgb(0.32, 0.4, 0.2)
        self.pRender.fb.draw.rect(c,
                                  Rect(48 + 204, 120 + 20 + 115 + 25, 180, 10),
                                  0)
        self.pRender.fb.putstr(48 + 22 + 204, 120 + 26 - 3 + 110 - 16,
                               "  Setting  ", c, 2)
        c = self.pRender.ConvRgb(0.32, 0.2, 1.0)
        self.pRender.fb.putstr(48 + 22 + 3 + 204 + 10, 120 + 80 + 64,
                               "Check Wanem Config", c, 1)

        return

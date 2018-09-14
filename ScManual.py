import sys, getopt, struct, time, termios, fcntl, sys, os, colorsys, threading, time, datetime, subprocess
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/fbtft')
from RenderManager import RenderManager
from WanemManager import WanemManager
from ScBase import ScBase
from gfx import Rect
from DataAsset import CTX


class ScManual(ScBase):
    def __init__(self, pCTX, pRender, pWanem):
        super(ScManual, self).__init__(pCTX, pRender, pWanem)
        self.ptDef.insert(
            0, self.CreateTocuhDef("BtMenu", 468, 29, 62, 42, self.BtHandler))
        self.ptDef.insert(
            1,
            self.CreateTocuhDef("BtConnL", 208 - 90 * 0, 100 + 80 * 0, 80, 48,
                                self.BtHandler))
        self.ptDef.insert(
            2,
            self.CreateTocuhDef("BtConnR", 208 - 90 * 1, 100 + 80 * 0, 80, 48,
                                self.BtHandler))
        self.ptDef.insert(
            3,
            self.CreateTocuhDef("BtSpeedL", 208 - 90 * 0, 100 + 80 * 1, 80, 48,
                                self.BtHandler))
        self.ptDef.insert(
            4,
            self.CreateTocuhDef("BtSpeedR", 208 - 90 * 1, 100 + 80 * 1, 80, 48,
                                self.BtHandler))
        self.ptDef.insert(
            5,
            self.CreateTocuhDef("BtDelayL", 208 - 90 * 0, 100 + 80 * 2, 80, 48,
                                self.BtHandler))
        self.ptDef.insert(
            6,
            self.CreateTocuhDef("BtDelayR", 208 - 90 * 1, 100 + 80 * 2, 80, 48,
                                self.BtHandler))

    def BtHandler(self, key):
        print "BtHandler" + key
        if key == "BtMenu":
            self.pWanem.InitSingle()
            self.pWanem.Clear()
            self.nextScene = "Menu"
            self.state = self.STATE_TERM
        elif key == "BtConnL":
            self.pWanem.EmuDisconnToggle()
        elif key == "BtConnR":
            self.pWanem.EmuDisconnPush()
        elif key == "BtSpeedL":
            self.pWanem.EmuSpeedChange(-1)
        elif key == "BtSpeedR":
            self.pWanem.EmuSpeedChange(1)
        elif key == "BtDelayL":
            self.pWanem.EmuDelayChange(-1)
        elif key == "BtDelayR":
            self.pWanem.EmuDelayChange(1)

    def TouchUpHandler(self, x, y):
        #print "TouchUpHandler Pos >> " + str(x) + " : " + str(y)
        # for Human Err, All Up to DisconnRelease Call
        self.pWanem.EmuDisconnRelease()
        return

    def Start(self):
        super(ScManual, self).Start()

        ##[ RENDER ]################################################################

        self.pRender.UpdateTitle("WAN Emulation - Manual Preset")
        self.pRender.UpdateSubTitle("speed:nolimit, delay:nolimit")

        c = yellow = self.pRender.fb.rgb(255, 255, 0)
        self.pRender.fb.draw.rect(c, Rect(0, 54, self.pRender.xres, 1), 0)
        self.pRender.fb.draw.rect(c, Rect(0, 74, self.pRender.xres, 1), 0)
        self.pRender.fb.draw.rect(c, Rect(0, 54, 10 + 60, 20), 0)
        self.pRender.fb.draw.rect(c, Rect(480 - 10, 54, 10, 20), 0)
        self.pRender.fb.putstr(26, 54 + 7, ">>>", self.pRender.N, 1)

        c = self.pRender.ConvRgb(0.16, 1, 0.6)
        self.pRender.fb.draw.rect(c, Rect(1, 160, self.pRender.xres - 2, 1), 0)
        self.pRender.fb.draw.rect(c, Rect(1, 240, self.pRender.xres - 2, 1), 0)

        self.RenderBackBt(True)

        c = self.pRender.ConvRgb(0.56, 0.6, 0.6)
        self.pRender.fb.draw.rect(c, Rect(286, 80 * 3 + 8, 80, 44), 0)
        self.pRender.fb.draw.rect(c, Rect(380, 80 * 3 + 8, 80, 44), 0)
        self.pRender.fb.putstr(286, 80 * 3 + 64, "Delay/Loss Setting", c, 1)
        c = self.pRender.ConvRgb(0.56, 0.3, 0.3)
        self.pRender.fb.draw.rect(c, Rect(286, 80 * 3 + 8 + 44, 80, 4), 0)
        self.pRender.fb.draw.rect(c, Rect(380, 80 * 3 + 8 + 44, 80, 4), 0)
        self.pRender.fb.putstr(286 + 20, 80 * 3 + 12, '<', 0, 5)
        self.pRender.fb.putstr(386 + 20, 80 * 3 + 12, '>', 0, 5)

        c = self.pRender.ConvRgb(0.36, 0.6, 0.6)
        self.pRender.fb.draw.rect(c, Rect(286, 80 * 2 + 8, 80, 44), 0)
        self.pRender.fb.draw.rect(c, Rect(380, 80 * 2 + 8, 80, 44), 0)
        self.pRender.fb.putstr(286, 80 * 2 + 64, "Speed Setting", c, 1)
        c = self.pRender.ConvRgb(0.36, 0.3, 0.3)
        self.pRender.fb.draw.rect(c, Rect(286, 80 * 2 + 8 + 44, 80, 4), 0)
        self.pRender.fb.draw.rect(c, Rect(380, 80 * 2 + 8 + 44, 80, 4), 0)
        self.pRender.fb.putstr(286 + 20, 80 * 2 + 12, '<', 0, 5)
        self.pRender.fb.putstr(386 + 20, 80 * 2 + 12, '>', 0, 5)

        c = self.pRender.ConvRgb(0.98, 0.6, 0.6)
        self.pRender.fb.draw.rect(c, Rect(286, 80 * 1 + 8, 80, 44), 0)
        self.pRender.fb.draw.rect(c, Rect(380, 80 * 1 + 8, 80, 44), 0)
        self.pRender.fb.putstr(286, 80 * 1 + 64, "Disconnect Emulation", c, 1)
        c = self.pRender.ConvRgb(0.98, 0.3, 0.3)
        self.pRender.fb.draw.rect(c, Rect(286, 80 * 1 + 8 + 44, 80, 4), 0)
        self.pRender.fb.draw.rect(c, Rect(380, 80 * 1 + 8 + 44, 80, 4), 0)
        self.pRender.fb.putstr(286 + 5, 80 * 1 + 22, "Toggle", 0, 2)
        self.pRender.fb.putstr(386 + 11, 80 * 1 + 22, 'Push', 0, 2)

        self.pRender.RenderDot(0, 5)
        self.pRender.RenderDot(1, 7)
        self.pRender.RenderDot(2, 7)

        self.pWanem.InitSingle()
        #self.pWanem.InitDual(0)
        #self.pWanem.EmuSpeedChange(1)
        #self.pWanem.EmuSpeedChange(-1)

        return

import sys, getopt, struct, time, termios, fcntl, sys, os, colorsys, threading, time, datetime, subprocess
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/fbtft')
from RenderManager import RenderManager
from WanemManager import WanemManager
from ScBase import ScBase
from gfx import Rect
from DataAsset import CTX


class ScManualEx(ScBase):
    def __init__(self, pCTX, pRender, pWanem):
        super(ScManualEx, self).__init__(pCTX, pRender, pWanem)
        self.ptDef.insert(
            0, self.CreateTocuhDef("BtMenu", 468, 29, 62, 42, self.BtHandler))
        self.ptDef.insert(
            1, self.CreateTocuhDef("BtApply", 149, 255, 110, 48,
                                   self.BtHandler))
        self.ptDef.insert(
            2, self.CreateTocuhDef("BtConnL", 346, 255, 80, 48,
                                   self.BtHandler))
        self.ptDef.insert(
            3, self.CreateTocuhDef("BtConnR", 258, 255, 80, 48,
                                   self.BtHandler))
        self.ptDef.insert(
            4,
            self.CreateTocuhDef("BtUpBand1L", 477, 158, 40, 26,
                                self.BtHandler))
        self.ptDef.insert(
            5,
            self.CreateTocuhDef("BtUpBand1R", 405, 158, 40, 26,
                                self.BtHandler))
        self.ptDef.insert(
            6,
            self.CreateTocuhDef("BtUpBand10L", 477, 158 + 30 * 1, 40, 26,
                                self.BtHandler))
        self.ptDef.insert(
            7,
            self.CreateTocuhDef("BtUpBand10R", 405, 158 + 30 * 1, 40, 26,
                                self.BtHandler))
        self.ptDef.insert(
            8,
            self.CreateTocuhDef("BtUpBand100L", 477, 158 + 30 * 2, 40, 26,
                                self.BtHandler))
        self.ptDef.insert(
            9,
            self.CreateTocuhDef("BtUpBand100R", 405, 158 + 30 * 2, 40, 26,
                                self.BtHandler))
        self.ptDef.insert(
            10,
            self.CreateTocuhDef("BtDwBand1L", 368, 158, 40, 26,
                                self.BtHandler))
        self.ptDef.insert(
            11,
            self.CreateTocuhDef("BtDwBand1R", 368 - 72, 158, 40, 26,
                                self.BtHandler))
        self.ptDef.insert(
            12,
            self.CreateTocuhDef("BtDwBand10L", 368, 158 + 30 * 1, 40, 26,
                                self.BtHandler))
        self.ptDef.insert(
            13,
            self.CreateTocuhDef("BtDwBand10R", 368 - 72, 158 + 30 * 1, 40, 26,
                                self.BtHandler))
        self.ptDef.insert(
            14,
            self.CreateTocuhDef("BtDwBand100L", 368, 158 + 30 * 2, 40, 26,
                                self.BtHandler))
        self.ptDef.insert(
            15,
            self.CreateTocuhDef("BtDwBand100R", 368 - 72, 158 + 30 * 2, 40, 26,
                                self.BtHandler))
        self.ptDef.insert(
            16,
            self.CreateTocuhDef("BtUpDelay1L", 258, 158, 40, 26,
                                self.BtHandler))
        self.ptDef.insert(
            17,
            self.CreateTocuhDef("BtUpDelay1R", 258 - 72, 158, 40, 26,
                                self.BtHandler))
        self.ptDef.insert(
            18,
            self.CreateTocuhDef("BtUpDelay10L", 258, 158 + 30 * 1, 40, 26,
                                self.BtHandler))
        self.ptDef.insert(
            19,
            self.CreateTocuhDef("BtUpDelay10R", 258 - 72, 158 + 30 * 1, 40, 26,
                                self.BtHandler))
        self.ptDef.insert(
            20,
            self.CreateTocuhDef("BtUpDelay100L", 258, 158 + 30 * 2, 40, 26,
                                self.BtHandler))
        self.ptDef.insert(
            21,
            self.CreateTocuhDef("BtUpDelay100R", 258 - 72, 158 + 30 * 2, 40,
                                26, self.BtHandler))
        self.ptDef.insert(
            22,
            self.CreateTocuhDef("BtDwDelay1L", 144, 158, 40, 26,
                                self.BtHandler))
        self.ptDef.insert(
            23,
            self.CreateTocuhDef("BtDwDelay1R", 144 - 72, 158, 40, 26,
                                self.BtHandler))
        self.ptDef.insert(
            24,
            self.CreateTocuhDef("BtDwDelay10L", 144, 158 + 30 * 1, 40, 26,
                                self.BtHandler))
        self.ptDef.insert(
            25,
            self.CreateTocuhDef("BtDwDelay10R", 144 - 72, 158 + 30 * 1, 40, 26,
                                self.BtHandler))
        self.ptDef.insert(
            26,
            self.CreateTocuhDef("BtDwDelay100L", 144, 158 + 30 * 2, 40, 26,
                                self.BtHandler))
        self.ptDef.insert(
            27,
            self.CreateTocuhDef("BtDwDelay100R", 144 - 72, 158 + 30 * 2, 40,
                                26, self.BtHandler))

    def BtHandler(self, key):
        print("BtHandler" + key)
        if key == "BtMenu":
            self.pWanem.ClearEx()
            self.nextScene = "Menu"
            self.state = self.STATE_TERM
        elif key == "BtConnL":
            if self.isApply != 0:
                self.pWanem.EmuDisconnToggleMini(self.upBand, self.dwBand,
                                                 self.upDelay, self.dwDelay)
        elif key == "BtConnR":
            if self.isApply != 0:
                self.pWanem.EmuDisconnPushMini(self.upBand, self.dwBand,
                                               self.upDelay, self.dwDelay)
        elif key == "BtApply":
            self.isApply = (self.isApply + 1) % 2
            self.RenderApplyBt()
            if self.isApply == 0:
                self.ReleaseDirectParam()
                self.pRender.UpdateSubTitle(
                    "Set Param Manually - Status : Non Active")
            else:
                self.ApplyDirectParam()
                self.pRender.UpdateSubTitle(
                    "Set Param Manually - Status : Active")
        elif key == "BtUpBand1L":
            self.UpdateUpBandParam(-1)
        elif key == "BtUpBand1R":
            self.UpdateUpBandParam(1)
        elif key == "BtUpBand10L":
            self.UpdateUpBandParam(-10)
        elif key == "BtUpBand10R":
            self.UpdateUpBandParam(10)
        elif key == "BtUpBand100L":
            self.UpdateUpBandParam(-100)
        elif key == "BtUpBand100R":
            self.UpdateUpBandParam(100)
        elif key == "BtDwBand1L":
            self.UpdateDwBandParam(-1)
        elif key == "BtDwBand1R":
            self.UpdateDwBandParam(1)
        elif key == "BtDwBand10L":
            self.UpdateDwBandParam(-10)
        elif key == "BtDwBand10R":
            self.UpdateDwBandParam(10)
        elif key == "BtDwBand100L":
            self.UpdateDwBandParam(-100)
        elif key == "BtDwBand100R":
            self.UpdateDwBandParam(100)
        elif key == "BtUpDelay1L":
            self.UpdateUpDelayParam(-1)
        elif key == "BtUpDelay1R":
            self.UpdateUpDelayParam(1)
        elif key == "BtUpDelay10L":
            self.UpdateUpDelayParam(-10)
        elif key == "BtUpDelay10R":
            self.UpdateUpDelayParam(10)
        elif key == "BtUpDelay100L":
            self.UpdateUpDelayParam(-100)
        elif key == "BtUpDelay100R":
            self.UpdateUpDelayParam(100)
        elif key == "BtDwDelay1L":
            self.UpdateDwDelayParam(-1)
        elif key == "BtDwDelay1R":
            self.UpdateDwDelayParam(1)
        elif key == "BtDwDelay10L":
            self.UpdateDwDelayParam(-10)
        elif key == "BtDwDelay10R":
            self.UpdateDwDelayParam(10)
        elif key == "BtDwDelay100L":
            self.UpdateDwDelayParam(-100)
        elif key == "BtDwDelay100R":
            self.UpdateDwDelayParam(100)

    def TouchUpHandler(self, x, y):
        #print "TouchUpHandler Pos >> " + str(x) + " : " + str(y)
        # for Human Err, All Up to DisconnRelease Call
        if self.isApply != 0:
            self.pWanem.EmuDisconnReleaseMini(self.upBand, self.dwBand,
                                              self.upDelay, self.dwDelay)
        return

    def ApplyDirectParam(self):
        self.pRender.fb.draw.rect(self.pRender.N,
                                  Rect(116 * 0 + 20, 112, 60, 18), 0)
        self.pRender.fb.draw.rect(self.pRender.N,
                                  Rect(116 * 1 + 20, 112, 60, 18), 0)
        self.pRender.fb.draw.rect(self.pRender.N,
                                  Rect(116 * 2 + 20, 112, 60, 18), 0)
        self.pRender.fb.draw.rect(self.pRender.N,
                                  Rect(116 * 3 + 20, 112, 60, 18), 0)
        self.pRender.fb.putstr(116 * 0 + 16 * 1 + 10, 114,
                               "%04d" % self.upBand, self.pRender.W, 2)
        self.pRender.fb.putstr(116 * 1 + 16 * 1 + 10, 114,
                               "%04d" % self.dwBand, self.pRender.W, 2)
        self.pRender.fb.putstr(116 * 2 + 16 * 1 + 10, 114,
                               "%04d" % self.upDelay, self.pRender.W, 2)
        self.pRender.fb.putstr(116 * 3 + 16 * 1 + 10, 114,
                               "%04d" % self.dwDelay, self.pRender.W, 2)
        self.pWanem.DirectApplyEx(self.upBand, self.dwBand, self.upDelay,
                                  self.dwDelay)

    def ReleaseDirectParam(self):
        c = self.pRender.ConvRgb(0.94, 0.8, 0.9)
        self.pRender.fb.draw.rect(self.pRender.N,
                                  Rect(116 * 0 + 20, 112, 60, 18), 0)
        self.pRender.fb.draw.rect(self.pRender.N,
                                  Rect(116 * 1 + 20, 112, 60, 18), 0)
        self.pRender.fb.draw.rect(self.pRender.N,
                                  Rect(116 * 2 + 20, 112, 60, 18), 0)
        self.pRender.fb.draw.rect(self.pRender.N,
                                  Rect(116 * 3 + 20, 112, 60, 18), 0)
        self.pRender.fb.putstr(116 * 0 + 16 * 1 + 10, 114,
                               "%04d" % self.upBand, c, 2)
        self.pRender.fb.putstr(116 * 1 + 16 * 1 + 10, 114,
                               "%04d" % self.dwBand, c, 2)
        self.pRender.fb.putstr(116 * 2 + 16 * 1 + 10, 114,
                               "%04d" % self.upDelay, c, 2)
        self.pRender.fb.putstr(116 * 3 + 16 * 1 + 10, 114,
                               "%04d" % self.dwDelay, c, 2)
        self.pWanem.ClearEx()

    def UpdateUpBandParam(self, delta):
        if self.isApply != 0:
            return
        self.upBand = self.upBand + delta
        if self.upBand > 9999:
            self.upBand = 9999
        if self.upBand < 16:
            self.upBand = 16
        self.RenderParamForm(0, "", "%04d" % self.upBand, "", True)

    def UpdateDwBandParam(self, delta):
        if self.isApply != 0:
            return
        self.dwBand = self.dwBand + delta
        if self.dwBand > 9999:
            self.dwBand = 9999
        if self.dwBand < 16:
            self.dwBand = 16
        self.RenderParamForm(1, "", "%04d" % self.dwBand, "", True)

    def UpdateUpDelayParam(self, delta):
        if self.isApply != 0:
            return
        self.upDelay = self.upDelay + delta
        if self.upDelay > 9999:
            self.upDelay = 9999
        if self.upDelay < 0:
            self.upDelay = 0
        self.RenderParamForm(2, "", "%04d" % self.upDelay, "", True)

    def UpdateDwDelayParam(self, delta):
        if self.isApply != 0:
            return
        self.dwDelay = self.dwDelay + delta
        if self.dwDelay > 9999:
            self.dwDelay = 9999
        if self.dwDelay < 0:
            self.dwDelay = 0
        self.RenderParamForm(3, "", "%04d" % self.dwDelay, "", True)

    def RenderParamForm(self, idx, label, value, unit, isParamOnly=False):

        if isParamOnly == True:
            self.pRender.fb.draw.rect(self.pRender.N,
                                      Rect(116 * idx + 20, 112, 60, 18), 0)

        c = self.pRender.ConvRgb(0.94, 0.8, 0.9)
        self.pRender.fb.putstr(116 * idx + 16 * 1 + 10, 114, value, c, 2)

        if isParamOnly == True:
            return

        c = self.pRender.ConvRgb(0.44, 0.3, 0.9)
        self.pRender.fb.putstr(116 * idx + 16 * 1, 85, label, c, 2)
        self.pRender.fb.putstr(116 * idx + 16 * 1 + 10 + 58, 120, unit,
                               self.pRender.W, 1)

        c = self.pRender.ConvRgb(0.4, 0.6, 0.4)
        self.pRender.fb.draw.rect(c, Rect(116 * idx + 16 * 1, 100, 100, 2), 0)
        self.pRender.fb.draw.rect(c, Rect(116 * idx + 16 * 1, 100 + 40, 100,
                                          2), 0)
        self.pRender.fb.draw.rect(c, Rect(116 * idx + 16 * 1, 100, 2, 40), 0)
        self.pRender.fb.draw.rect(c, Rect(116 * idx + 16 * 1 + 100, 100, 2,
                                          42), 0)

        c = self.pRender.W
        self.pRender.fb.putstr(116 * idx + 16 * 1 + 33, 152 + 30 * 0, " 1", c,
                               2)
        self.pRender.fb.putstr(116 * idx + 16 * 1 + 33 + 6, 152 + 30 + 1, "10",
                               c, 2)
        self.pRender.fb.putstr(116 * idx + 16 * 1 + 33, 152 + 30 * 2, "100", c,
                               2)

        c = self.pRender.ConvRgb(0.44, 0.9, 0.7)
        self.pRender.fb.draw.rect(
            c, Rect(116 * idx + 16 * 1, 146 + 30 * 0, 30, 26), 0)
        self.pRender.fb.draw.rect(
            c, Rect(116 * idx + 16 * 1 + 72, 146 + 30 * 0, 30, 26), 0)
        self.pRender.fb.draw.rect(
            c, Rect(116 * idx + 16 * 1, 146 + 30 * 1, 30, 26), 0)
        self.pRender.fb.draw.rect(
            c, Rect(116 * idx + 16 * 1 + 72, 146 + 30 * 1, 30, 26), 0)
        self.pRender.fb.draw.rect(
            c, Rect(116 * idx + 16 * 1, 146 + 30 * 2, 30, 26), 0)
        self.pRender.fb.draw.rect(
            c, Rect(116 * idx + 16 * 1 + 72, 146 + 30 * 2, 30, 26), 0)

        c = self.pRender.ConvRgb(0.44, 0.1, 1)
        self.pRender.fb.putstr(116 * idx + 16 * 1 + 5, 145 + 30 * 0, "-", c, 4)
        self.pRender.fb.putstr(116 * idx + 16 * 1 + 77, 145 + 30 * 0, "+", c,
                               4)
        self.pRender.fb.putstr(116 * idx + 16 * 1 + 5, 145 + 30 * 1, "-", c, 4)
        self.pRender.fb.putstr(116 * idx + 16 * 1 + 77, 145 + 30 * 1, "+", c,
                               4)
        self.pRender.fb.putstr(116 * idx + 16 * 1 + 5, 145 + 30 * 2, "-", c, 4)
        self.pRender.fb.putstr(116 * idx + 16 * 1 + 77, 145 + 30 * 2, "+", c,
                               4)

    def Start(self):
        super(ScManualEx, self).Start()

        ##[ PARAM ]################################################################

        self.upBand = 512
        self.dwBand = 512
        self.upDelay = 0
        self.dwDelay = 0
        self.isApply = 0

        ##[ RENDER ]################################################################

        self.pRender.UpdateTitle("WAN Emulation - Manual Direct")
        self.pRender.UpdateSubTitle("Set Param Manually - Status : Non Active")

        c = yellow = self.pRender.fb.rgb(255, 255, 0)
        self.pRender.fb.draw.rect(c, Rect(0, 54, self.pRender.xres, 1), 0)
        self.pRender.fb.draw.rect(c, Rect(0, 74, self.pRender.xres, 1), 0)
        self.pRender.fb.draw.rect(c, Rect(0, 54, 10 + 60, 20), 0)
        self.pRender.fb.draw.rect(c, Rect(480 - 10, 54, 10, 20), 0)
        self.pRender.fb.putstr(26, 54 + 7, ">>>", self.pRender.N, 1)

        c = self.pRender.ConvRgb(0.16, 1, 0.6)
        #self.pRender.fb.draw.rect(c, Rect(1,      160, self.pRender.xres-2, 1), 0)
        self.pRender.fb.draw.rect(c,
                                  Rect(1, 240, self.pRender.xres - 2 - 150, 1),
                                  0)
        self.pRender.fb.draw.rect(
            c, Rect(self.pRender.xres - 150 - 1, 240, 1, 79), 0)

        self.RenderBackBt(True)

        self.RenderParamForm(0, "Up Band", "%04d" % self.upBand, "kbps")
        self.RenderParamForm(1, "Dw Band", "%04d" % self.dwBand, "kbps")
        self.RenderParamForm(2, "Up Delay", "%04d" % self.upDelay, "msec")
        self.RenderParamForm(3, "Dw Delay", "%04d" % self.dwDelay, "msec")
        #c = self.pRender.ConvRgb(0.56,0.6,0.6)
        #self.pRender.fb.draw.rect(c, Rect(286, 80*3 + 8, 80, 44), 0)
        #self.pRender.fb.draw.rect(c, Rect(380, 80*3 + 8, 80, 44), 0)
        #self.pRender.fb.putstr(286, 80*3+64, "Delay Setting", c, 1)
        #c = self.pRender.ConvRgb(0.56,0.3,0.3)
        #self.pRender.fb.draw.rect(c, Rect(286, 80*3 + 8 + 44, 80, 4), 0)
        #self.pRender.fb.draw.rect(c, Rect(380, 80*3 + 8 + 44, 80, 4), 0)
        #self.pRender.fb.putstr(286 + 20, 80*3 + 12, '<', 0, 5)
        #self.pRender.fb.putstr(386 + 20, 80*3 + 12, '>', 0, 5)

        #c = self.pRender.ConvRgb(0.36,0.6,0.6)
        #self.pRender.fb.draw.rect(c, Rect(286, 80*2 + 8, 80, 44), 0)
        #self.pRender.fb.draw.rect(c, Rect(380, 80*2 + 8, 80, 44), 0)
        #self.pRender.fb.putstr(286, 80*2+64, "Speed Setting", c, 1)
        #c = self.pRender.ConvRgb(0.36,0.3,0.3)
        #self.pRender.fb.draw.rect(c, Rect(286, 80*2 + 8 + 44, 80, 4), 0)
        #self.pRender.fb.draw.rect(c, Rect(380, 80*2 + 8 + 44, 80, 4), 0)
        #self.pRender.fb.putstr(286 + 20, 80*2 + 12, '<', 0, 5)
        #self.pRender.fb.putstr(386 + 20, 80*2 + 12, '>', 0, 5)

        c = self.pRender.ConvRgb(0.98, 0.6, 0.6)
        self.pRender.fb.draw.rect(c, Rect(286 - 140, 80 * 3 + 8, 80, 44), 0)
        self.pRender.fb.draw.rect(c, Rect(380 - 140, 80 * 3 + 8, 80, 44), 0)
        self.pRender.fb.putstr(286 - 140, 80 * 3 + 64, "Disconnect Emulation",
                               c, 1)
        c = self.pRender.ConvRgb(0.98, 0.3, 0.3)
        self.pRender.fb.draw.rect(c, Rect(286 - 140, 80 * 3 + 8 + 44, 80, 4),
                                  0)
        self.pRender.fb.draw.rect(c, Rect(380 - 140, 80 * 3 + 8 + 44, 80, 4),
                                  0)
        self.pRender.fb.putstr(286 - 140 + 5, 80 * 3 + 22, "Toggle", 0, 2)
        self.pRender.fb.putstr(386 - 140 + 11, 80 * 3 + 22, 'Push', 0, 2)

        self.pRender.RenderDotMini(2, 5)

        self.RenderApplyBt()
        self.pWanem.ClearEx()

        return

    def RenderApplyBt(self):
        c = self.pRender.ConvRgb(0.18, 0.6, 0.6)
        self.pRender.fb.draw.rect(c, Rect(350, 80 * 3 + 8, 110, 44), 0)
        self.pRender.fb.putstr(350, 80 * 3 + 64, "Wan Setting", c, 1)
        c = self.pRender.ConvRgb(0.18, 0.3, 0.3)
        self.pRender.fb.draw.rect(c, Rect(350, 80 * 3 + 8 + 44, 110, 4), 0)
        if self.isApply == 0:
            self.pRender.fb.putstr(350 + 24, 80 * 3 + 22, "Apply", 0, 2)
        else:
            self.pRender.fb.putstr(350 + 12, 80 * 3 + 22, "Release", 0, 2)

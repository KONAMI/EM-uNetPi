import sys, getopt, struct, time, termios, fcntl, sys, os, colorsys, threading, time, datetime, subprocess
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/fbtft')
from RenderManager import RenderManager
from WanemManager import WanemManager
from ScBase import ScBase
from gfx import Rect
from DataAsset import CTX


class ScManualEx2(ScBase):
    def __init__(self, pCTX, pRender, pWanem):
        super(ScManualEx2, self).__init__(pCTX, pRender, pWanem)
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
            self.CreateTocuhDef("BtUp1L", 477 + 6, 158, 40, 26,
                                self.BtHandler))
        self.ptDef.insert(
            5,
            self.CreateTocuhDef("BtUp1R", 405 + 6, 158, 40, 26,
                                self.BtHandler))
        self.ptDef.insert(
            6,
            self.CreateTocuhDef("BtUp10L", 477 + 6, 158 + 30 * 1, 40, 26,
                                self.BtHandler))
        self.ptDef.insert(
            7,
            self.CreateTocuhDef("BtUp10R", 405 + 6, 158 + 30 * 1, 40, 26,
                                self.BtHandler))
        self.ptDef.insert(
            8,
            self.CreateTocuhDef("BtUp100L", 477 + 6, 158 + 30 * 2, 40, 26,
                                self.BtHandler))
        self.ptDef.insert(
            9,
            self.CreateTocuhDef("BtUp100R", 405 + 6, 158 + 30 * 2, 40, 26,
                                self.BtHandler))
        self.ptDef.insert(
            10,
            self.CreateTocuhDef("BtDw1L", 368 + 6, 158, 40, 26,
                                self.BtHandler))
        self.ptDef.insert(
            11,
            self.CreateTocuhDef("BtDw1R", 368 - 72 + 6, 158, 40, 26,
                                self.BtHandler))
        self.ptDef.insert(
            12,
            self.CreateTocuhDef("BtDw10L", 368 + 6, 158 + 30 * 1, 40, 26,
                                self.BtHandler))
        self.ptDef.insert(
            13,
            self.CreateTocuhDef("BtDw10R", 368 - 72 + 6, 158 + 30 * 1, 40, 26,
                                self.BtHandler))
        self.ptDef.insert(
            14,
            self.CreateTocuhDef("BtDw100L", 368 + 6, 158 + 30 * 2, 40, 26,
                                self.BtHandler))
        self.ptDef.insert(
            15,
            self.CreateTocuhDef("BtDw100R", 368 - 72 + 6, 158 + 30 * 2, 40, 26,
                                self.BtHandler))

        self.ptDef.insert(
            16,
            self.CreateTocuhDef("BtEditBand", 248, 98, 52, 39, self.BtHandler))
        self.ptDef.insert(
            17,
            self.CreateTocuhDef("BtEditDelay", 248, 147, 52, 39,
                                self.BtHandler))
        self.ptDef.insert(
            18,
            self.CreateTocuhDef("BtEditLoss", 248, 196, 52, 39,
                                self.BtHandler))

    def BtHandler(self, key):
        print "BtHandler" + key
        if key == "BtMenu":
            self.pWanem.ClearEx()
            self.nextScene = "Menu"
            self.state = self.STATE_TERM
        elif key == "BtConnL":
            if self.isApply != 0:
                self.pWanem.EmuDisconnToggleMini(self.upBand, self.dwBand,
                                                 self.upDelay, self.dwDelay,
                                                 self.upLoss, self.dwLoss)
        elif key == "BtConnR":
            if self.isApply != 0:
                self.pWanem.EmuDisconnPushMini(self.upBand, self.dwBand,
                                               self.upDelay, self.dwDelay,
                                               self.upLoss, self.dwLoss)
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
        elif key == "BtUp1L":
            self.UpdateUpParam(-1)
        elif key == "BtUp1R":
            self.UpdateUpParam(1)
        elif key == "BtUp10L":
            self.UpdateUpParam(-10)
        elif key == "BtUp10R":
            self.UpdateUpParam(10)
        elif key == "BtUp100L":
            self.UpdateUpParam(-100)
        elif key == "BtUp100R":
            self.UpdateUpParam(100)
        elif key == "BtDw1L":
            self.UpdateDwParam(-1)
        elif key == "BtDw1R":
            self.UpdateDwParam(1)
        elif key == "BtDw10L":
            self.UpdateDwParam(-10)
        elif key == "BtDw10R":
            self.UpdateDwParam(10)
        elif key == "BtDw100L":
            self.UpdateDwParam(-100)
        elif key == "BtDw100R":
            self.UpdateDwParam(100)
        elif key == "BtEditBand":
            self.SwitchLink(0)
        elif key == "BtEditDelay":
            self.SwitchLink(1)
        elif key == "BtEditLoss":
            self.SwitchLink(2)

    def TouchUpHandler(self, x, y):
        # print "TouchUpHandler Pos >> " + str(x) + " : " + str(y)
        # for Human Err, All Up to DisconnRelease Call
        if self.isApply != 0:
            self.pWanem.EmuDisconnReleaseMini(self.upBand, self.dwBand,
                                              self.upDelay, self.dwDelay,
                                              self.upLoss, self.dwLoss)
        return

    def ApplyDirectParam(self):
        self.RenderWire(True)
        self.pWanem.DirectApplyEx(self.upBand, self.dwBand, self.upDelay,
                                  self.dwDelay, self.upLoss, self.dwLoss)

    def ReleaseDirectParam(self):
        self.RenderWire(False)
        self.pWanem.ClearEx()

    def UpdateUpParam(self, delta):
        if self.isApply != 0:
            return
        if self.currentEdit == 0:
            self.upBand = self.upBand + delta
            if self.upBand > 9999:
                self.upBand = 9999
            if self.upBand < 32:
                self.upBand = 32
            self.RenderParamForm(0, "Up Band", "%04d" % self.upBand, "kbps",
                                 True)
            self.RenderUpdateParamRow(0, "%04d" % self.upBand, True)
        elif self.currentEdit == 1:
            self.upDelay = self.upDelay + delta
            if self.upDelay > 9999:
                self.upDelay = 9999
            if self.upDelay < 0:
                self.upDelay = 0
            self.RenderParamForm(0, "Up Delay", "%04d" % self.upDelay, "msec",
                                 True)
            self.RenderUpdateParamRow(1, "%04d" % self.upDelay, True)
        elif self.currentEdit == 2:
            self.upLoss = self.upLoss + delta
            if self.upLoss > 100:
                self.upLoss = 100
            if self.upLoss < 0:
                self.upLoss = 0
            self.RenderParamForm(0, "Up Loss", "%4d" % self.upLoss, "%", True)
            self.RenderUpdateParamRow(2, "%4d" % self.upLoss, True)

    def UpdateDwParam(self, delta):
        if self.isApply != 0:
            return
        if self.currentEdit == 0:
            self.dwBand = self.dwBand + delta
            if self.dwBand > 9999:
                self.dwBand = 9999
            if self.dwBand < 32:
                self.dwBand = 32
            self.RenderParamForm(1, "Dw Band", "%04d" % self.dwBand, "kbps",
                                 True)
            self.RenderUpdateParamRow(0, "%04d" % self.dwBand, False)
        elif self.currentEdit == 1:
            self.dwDelay = self.dwDelay + delta
            if self.dwDelay > 9999:
                self.dwDelay = 9999
            if self.dwDelay < 0:
                self.dwDelay = 0
            self.RenderParamForm(1, "Dw Delay", "%04d" % self.dwDelay, "msec",
                                 True)
            self.RenderUpdateParamRow(1, "%04d" % self.dwDelay, False)
        elif self.currentEdit == 2:
            self.dwLoss = self.dwLoss + delta
            if self.dwLoss > 100:
                self.dwLoss = 100
            if self.dwLoss < 0:
                self.dwLoss = 0
            self.RenderParamForm(1, "Dw Loss", "%4d" % self.dwLoss, "%", True)
            self.RenderUpdateParamRow(2, "%4d" % self.dwLoss, False)

    def RenderParamRowBt(self, idx, isActive=False):

        if isActive == False:
            c = self.pRender.ConvRgb(0.14, 0.8, 0.7)
            #self.pRender.fb.draw.rect(c, Rect(238 + 2 , 84 + 50 * idx + 2,  60, 43), 0)
            self.pRender.fb.draw.rect(c, Rect(238 + 3, 84 + 50 * idx + 4, 2,
                                              40), 0)
            self.pRender.fb.draw.rect(
                c, Rect(238 + 2 + 55, 84 + 50 * idx + 4, 2, 40), 0)
            self.pRender.fb.draw.rect(
                c, Rect(238 + 3, 84 + 50 * idx + 4 + 38, 56, 2), 0)

        if isActive == True:
            c = self.pRender.ConvRgb(0.9, 1.0, 1.0)
            self.pRender.fb.draw.rect(c, Rect(241, 88 + 50 * idx, 56, 2), 0)
            self.pRender.fb.draw.rect(c, Rect(241, 88 + 50 * idx + 38, 56, 2),
                                      0)
            self.pRender.fb.draw.rect(c, Rect(241, 88 + 50 * idx, 2, 40), 0)
            self.pRender.fb.draw.rect(c, Rect(241 + 54, 88 + 50 * idx, 2, 40),
                                      0)

        c = self.pRender.ConvRgb(0.51, 0.3, 0.2)
        self.pRender.fb.draw.rect(c, Rect(243, 90 + 50 * idx + 32, 52, 4), 0)

        c = self.pRender.ConvRgb(0.51, 0.6, 0.79)
        if isActive == True:
            self.pRender.fb.draw.rect(c, Rect(243, 90 + 50 * idx, 52, 35), 0)
            self.pRender.fb.putstr(243 + 3, 90 + 50 * idx + 11, "LINK",
                                   self.pRender.N, 2)
        else:
            self.pRender.fb.draw.rect(c, Rect(243, 90 + 50 * idx - 2, 52, 35),
                                      0)
            self.pRender.fb.putstr(243 + 3, 90 + 50 * idx + 11 - 2, "EDIT",
                                   self.pRender.N, 2)

    def RenderUpdateParamRow(self, idx, value, isUp=True):
        #c = self.pRender.ConvRgb(0.44,0.4,0.7);
        if isUp == True:
            c = self.pRender.N
            self.pRender.fb.draw.rect(c, Rect(306, 110 + 50 * idx, 46, 14), 0)
            c = self.pRender.ConvRgb(0.44, 0.3, 0.9)
            self.pRender.fb.putstr(306, 110 + 50 * idx, value, c, 2)
        else:
            c = self.pRender.N
            self.pRender.fb.draw.rect(c, Rect(386, 110 + 50 * idx, 46, 14), 0)
            c = self.pRender.ConvRgb(0.44, 0.3, 0.9)
            self.pRender.fb.putstr(306 + 80, 110 + 50 * idx, value, c, 2)

    def RenderParamRow(self,
                       idx,
                       UpLabel,
                       UpValue,
                       UpUnit,
                       DwLabel,
                       DwValue,
                       DwUnit,
                       isActive,
                       opt=""):

        c = self.pRender.ConvRgb(0.44, 0.3, 0.9)
        self.pRender.fb.putstr(306, 110 + 50 * idx, UpValue, c, 2)
        self.pRender.fb.putstr(306 + 80, 110 + 50 * idx, DwValue, c, 2)

        c = self.pRender.ConvRgb(0.14, 0.8, 0.7)
        self.pRender.fb.draw.rect(c, Rect(238, 84 + 50 * idx, 229, 2), 0)
        self.pRender.fb.draw.rect(c, Rect(238, 84 + 50 * idx + 45, 229, 2), 0)
        self.pRender.fb.draw.rect(c, Rect(238, 84 + 50 * idx, 2, 47), 0)
        self.pRender.fb.draw.rect(c, Rect(238 + 207 + 20, 84 + 50 * idx, 2,
                                          47), 0)
        self.pRender.fb.draw.rect(c, Rect(238 + 2, 84 + 50 * idx + 2, 60, 43),
                                  0)

        if opt != "":
            c = self.pRender.ConvRgb(0.96, 0.9, 0.7)
            self.pRender.fb.draw.rect(c, Rect(446, 87 + 50 * idx, 18, 12), 0)
            c = self.pRender.ConvRgb(0, 0, 0.5)
            self.pRender.fb.putstr(452, 86 + 50 * idx + 4, opt, self.pRender.W,
                                   1)

        self.pRender.fb.putstr(306 + 50, 116 + 50 * idx, UpUnit,
                               self.pRender.W, 1)
        self.pRender.fb.putstr(306 + 130, 116 + 50 * idx, DwUnit,
                               self.pRender.W, 1)

        c = self.pRender.ConvRgb(0, 0, 0.5)
        self.pRender.fb.draw.rect(c, Rect(304, 102 + 50 * idx, 157, 1), 0)

        self.pRender.fb.putstr(306, 88 + 50 * idx + 4, UpLabel, self.pRender.W,
                               1)
        self.pRender.fb.putstr(306 + 80, 88 + 50 * idx + 4, DwLabel,
                               self.pRender.W, 1)

        self.RenderParamRowBt(idx, isActive)

        return

    def RenderParamUI(self, idx):
        c = self.pRender.W
        self.pRender.fb.putstr(116 * idx + 8 + 33, 152 + 30 * 0, " 1", c, 2)
        self.pRender.fb.putstr(116 * idx + 8 + 33 + 6, 152 + 30 + 1, "10", c,
                               2)
        self.pRender.fb.putstr(116 * idx + 8 + 33, 152 + 30 * 2, "100", c, 2)

        c = self.pRender.ConvRgb(0.44, 0.9, 0.7)
        self.pRender.fb.draw.rect(c, Rect(116 * idx + 8, 146 + 30 * 0, 30, 26),
                                  0)
        self.pRender.fb.draw.rect(
            c, Rect(116 * idx + 8 + 72, 146 + 30 * 0, 30, 26), 0)
        self.pRender.fb.draw.rect(c, Rect(116 * idx + 8, 146 + 30 * 1, 30, 26),
                                  0)
        self.pRender.fb.draw.rect(
            c, Rect(116 * idx + 8 + 72, 146 + 30 * 1, 30, 26), 0)
        self.pRender.fb.draw.rect(c, Rect(116 * idx + 8, 146 + 30 * 2, 30, 26),
                                  0)
        self.pRender.fb.draw.rect(
            c, Rect(116 * idx + 8 + 72, 146 + 30 * 2, 30, 26), 0)

        c = self.pRender.ConvRgb(0.44, 0.1, 1)
        self.pRender.fb.putstr(116 * idx + 8 + 5, 145 + 30 * 0, "-", c, 4)
        self.pRender.fb.putstr(116 * idx + 8 + 77, 145 + 30 * 0, "+", c, 4)
        self.pRender.fb.putstr(116 * idx + 8 + 5, 145 + 30 * 1, "-", c, 4)
        self.pRender.fb.putstr(116 * idx + 8 + 77, 145 + 30 * 1, "+", c, 4)
        self.pRender.fb.putstr(116 * idx + 8 + 5, 145 + 30 * 2, "-", c, 4)
        self.pRender.fb.putstr(116 * idx + 8 + 77, 145 + 30 * 2, "+", c, 4)

    def SwitchLink(self, idx):
        # @todo if same idx, skip.
        if idx == 0:
            self.RenderParamForm(0, "Up Band", "%04d" % self.upBand, "kbps")
            self.RenderParamForm(1, "Dw Band", "%04d" % self.dwBand, "kbps")
        elif idx == 1:
            self.RenderParamForm(0, "Up Delay", "%04d" % self.upDelay, "msec")
            self.RenderParamForm(1, "Dw Delay", "%04d" % self.dwDelay, "msec")
        elif idx == 2:
            self.RenderParamForm(0, "Up Loss", "%4d" % self.upLoss, "%")
            self.RenderParamForm(1, "Dw Loss", "%4d" % self.dwLoss, "%")
        else:
            return
        if self.currentEdit != idx:
            self.RenderParamRowBt(idx, True)
            self.RenderParamRowBt(self.currentEdit, False)
            self.currentEdit = idx

    def RenderParamForm(self, idx, label, value, unit, isParamOnly=False):

        if isParamOnly == True:
            self.pRender.fb.draw.rect(self.pRender.N,
                                      Rect(116 * idx + 12, 112, 60, 18), 0)
        else:
            #self.pRender.fb.draw.rect(self.pRender.N, Rect(116*idx+8,  84, 102, 150), 0)
            #self.pRender.fb.draw.rect(self.pRender.W, Rect(116*idx+8,  84, 102, 58), 0)
            self.pRender.fb.draw.rect(self.pRender.N,
                                      Rect(116 * idx + 8 + 34, 84, 62, 16), 0)
            self.pRender.fb.draw.rect(self.pRender.N,
                                      Rect(116 * idx + 18, 114, 82, 16), 0)

        c = self.pRender.ConvRgb(0.94, 0.8, 0.9)
        self.pRender.fb.putstr(116 * idx + 8 + 10, 114, value, c, 2)

        if isParamOnly == True:
            return

        c = self.pRender.ConvRgb(0.44, 0.3, 0.9)
        self.pRender.fb.putstr(116 * idx + 8, 85, label, c, 2)
        self.pRender.fb.putstr(116 * idx + 8 + 10 + 58, 120, unit,
                               self.pRender.W, 1)

        c = self.pRender.ConvRgb(0.4, 0.6, 0.4)
        self.pRender.fb.draw.rect(c, Rect(116 * idx + 8, 100, 100, 2), 0)
        self.pRender.fb.draw.rect(c, Rect(116 * idx + 8, 100 + 40, 100, 2), 0)
        self.pRender.fb.draw.rect(c, Rect(116 * idx + 8, 100, 2, 40), 0)
        self.pRender.fb.draw.rect(c, Rect(116 * idx + 8 + 100, 100, 2, 42), 0)

    def RenderWire(self, isActive):
        if isActive == True:
            #c = self.pRender.ConvRgb(0.18,0.6,0.6)
            c = self.pRender.ConvRgb(0.18, 1.0, 1.0)
        else:
            c = self.pRender.ConvRgb(0.44, 0.0, 0.7)
        self.pRender.fb.draw.rect(c, Rect(234, 80, 238, 1), 0)
        self.pRender.fb.draw.rect(c, Rect(234, 80 + 154, 238, 1), 0)
        self.pRender.fb.draw.rect(c, Rect(234, 80, 1, 154), 0)
        self.pRender.fb.draw.rect(c, Rect(234 + 237, 80, 1, 154), 0)
        self.pRender.fb.draw.rect(c, Rect(248 + 150, 80 + 154 + 1, 2, 2), 0)
        self.pRender.fb.draw.rect(c, Rect(248 + 152, 80 + 154 + 1, 2, 4), 0)
        self.pRender.fb.draw.rect(c, Rect(248 + 154, 80 + 154 + 1, 2, 6), 0)
        self.pRender.fb.draw.rect(c, Rect(248 + 156, 80 + 154 + 1, 2, 4), 0)
        self.pRender.fb.draw.rect(c, Rect(248 + 158, 80 + 154 + 1, 2, 2), 0)

    def Start(self):
        super(ScManualEx2, self).Start()

        ##[ PARAM ]################################################################

        self.upBand = 1024
        self.dwBand = 1024
        self.upDelay = 0
        self.dwDelay = 0
        self.upLoss = 0
        self.dwLoss = 0
        self.isApply = 0
        self.currentEdit = 0

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

        self.RenderWire(False)

        if self.pWanem.wanemMode == 0:
            wanemModeLabel = "P"
        else:
            wanemModeLabel = "S"

        self.RenderParamRow(0, "Up Band", "%04d" % self.upBand, "kbps",
                            "Dw Band", "%04d" % self.dwBand, "kbps", True,
                            wanemModeLabel)
        self.RenderParamRow(1, "Up Delay", "%04d" % self.upDelay, "msec",
                            "Dw Delay", "%04d" % self.dwDelay, "msec", False)
        self.RenderParamRow(2, "Up Loss", "%4d" % self.upLoss, "%", "Dw Loss",
                            "%4d" % self.dwLoss, "%", False)

        self.RenderParamForm(0, "Up Band", "%04d" % self.upBand, "kbps")
        self.RenderParamUI(0)
        self.RenderParamForm(1, "Dw Band", "%04d" % self.dwBand, "kbps")
        self.RenderParamUI(1)

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
        if self.isApply == 0:
            c = self.pRender.ConvRgb(0.18, 0.6, 0.6)
        else:
            c = self.pRender.ConvRgb(0.18, 1.0, 1.0)
        self.pRender.fb.draw.rect(c, Rect(350, 80 * 3 + 8, 110, 44), 0)
        self.pRender.fb.putstr(350, 80 * 3 + 64, "Wan Setting", c, 1)
        c = self.pRender.ConvRgb(0.18, 0.3, 0.3)
        self.pRender.fb.draw.rect(c, Rect(350, 80 * 3 + 8 + 44, 110, 4), 0)
        if self.isApply == 0:
            self.pRender.fb.putstr(350 + 24, 80 * 3 + 22, "Apply", 0, 2)
        else:
            self.pRender.fb.putstr(350 + 12, 80 * 3 + 22, "Release", 0, 2)

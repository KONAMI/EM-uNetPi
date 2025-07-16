import sys, getopt, struct, time, termios, fcntl, sys, os, colorsys, threading, time, datetime, subprocess, random, string
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/fbtft')
from RenderManager import RenderManager
from WanemManager import WanemManager
from ScBase import ScBase
from gfx import Rect
from DataAsset import CTX
from MetricsCollector import MetricsCollector
from MetricsGraph import MetricsGraph
from CaptureTool import CaptureTool
from V6Util import V6Util

class ScMetricsMon(ScBase):
    def __init__(self, pCTX, pRender, pWanem):
        super(ScMetricsMon, self).__init__(pCTX, pRender, pWanem)
        self.ptDef.insert(
            0, self.CreateTocuhDef("BtMenu", 468, 29, 62, 42, self.BtHandler))
        # magic number 20
        self.ptDef.insert(
            1, self.CreateTocuhDef("BtApply", 88+20, 248, 80, 66,
                                   self.BtHandler))
        self.ptDef.insert(
            2, self.CreateTocuhDef("BtConnV6", 88+20+54, 248, 48, 30,
                                   self.BtHandler))
        self.ptDef.insert(
            3, self.CreateTocuhDef("BtConnV4", 88+20+54, 284, 48, 30,
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
            self.CreateTocuhDef("BtDw1L", 368 + 6 - 80, 158, 40, 26,
                                self.BtHandler))
        self.ptDef.insert(
            11,
            self.CreateTocuhDef("BtDw1R", 368 - 72 + 6 - 80, 158, 40, 26,
                                self.BtHandler))
        self.ptDef.insert(
            12,
            self.CreateTocuhDef("BtDw10L", 368 + 6 - 80, 158 + 30 * 1, 40, 26,
                                self.BtHandler))
        self.ptDef.insert(
            13,
            self.CreateTocuhDef("BtDw10R", 368 - 72 + 6 - 80, 158 + 30 * 1, 40, 26,
                                self.BtHandler))
        self.ptDef.insert(
            14,
            self.CreateTocuhDef("BtDw100L", 368 + 6 - 80, 158 + 30 * 2, 40, 26,
                                self.BtHandler))
        self.ptDef.insert(
            15,
            self.CreateTocuhDef("BtDw100R", 368 - 72 + 6 - 80, 158 + 30 * 2, 40, 26,
                                self.BtHandler))
        self.ptDef.insert(
            16,
            self.CreateTocuhDef("BtEditSampling", 248-80, 98, 52, 39, self.BtHandler))
        self.ptDef.insert(
            17,
            self.CreateTocuhDef("BtEditPps", 248-80, 147, 52, 39,
                                self.BtHandler))
        self.ptDef.insert(
            18,
            self.CreateTocuhDef("BtEditSize", 248-80, 196, 52, 39,
                                self.BtHandler))
        self.ptDef.insert(
            19,
            self.CreateTocuhDef("ToggleGraphAf", 465, 269, 60, 24,
                                self.BtHandler))
        self.ptDef.insert(
            20,
            self.CreateTocuhDef("Capture", 128, 29, 94, 42,
                                self.BtHandler))        
        
    def TestAddressFamilyControl(self, v4Enabled, v6Enabled):
        if self.isApply != 0:
            return            
        
        _v4Enabled = v4Enabled
        _v6Enabled = v6Enabled
        
        if (_v4Enabled == False) and (_v6Enabled == False):
            _v4Enabled = True

        self.testV4Enabled = _v4Enabled
        self.testV6Enabled = _v6Enabled

        self.RenderV4TestSwitch()
        self.RenderV6TestSwitch()

        if (_v4Enabled == False) or (_v6Enabled == False):
            if _v4Enabled == True:
                self.metricsGraph.SwitchRenderAf(0)
            elif _v6Enabled == True:
                self.metricsGraph.SwitchRenderAf(1)
        
    def BtHandler(self, key):
        print("BtHandler" + key)
        if key == "BtMenu":
            self.StopProbe()
            self.nextScene = "Menu"
            self.state = self.STATE_TERM
        elif key == "BtConnV6":
            if V6Util.IsV6Enabled() == True:
                if self.testV6Enabled == True:
                    _v6Enabled = False
                else:
                    _v6Enabled = True                    
                self.TestAddressFamilyControl(self.testV4Enabled, _v6Enabled)
        elif key == "BtConnV4":
            if self.testV4Enabled == True:
                _v4Enabled = False
            else:
                _v4Enabled = True
            self.TestAddressFamilyControl(_v4Enabled, self.testV6Enabled)
        elif key == "BtApply":
            self.isApply = (self.isApply + 1) % 2
            self.RenderApplyBt()
            if self.isApply == 0:
                self.StopProbe()
                self.pRender.UpdateSubTitle(
                    "Monitoring Status : Stop")
            else:
                self.StartProbe()
                self.pRender.UpdateSubTitle(
                    "Monitoring Status : Monitoring")
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
        elif key == "BtEditSampling":
            self.SwitchLink(0)
        elif key == "BtEditPps":
            self.SwitchLink(1)
        elif key == "BtEditSize":
            self.SwitchLink(2)
        elif key == "ToggleGraphAf":
            if (self.testV4Enabled == True) and (self.testV6Enabled == True):
                self.metricsGraph.ToggleGraphAf()
        elif key == "Capture":
            self.captureTool.BtHandler()
            
    def UpdateDwParam(self, delta):
        if self.isApply != 0:
            return
        if self.currentEdit == 0:
            self.sampling = self.sampling + delta
            if self.sampling > 999:
                self.sampling = 999
            if self.sampling < 30:
                self.sampling = 30
            self.RenderParamForm(1, "Param", "%04d" % self.sampling, "pkt", True) # Sampling                        
            self.RenderUpdateParamRow(0, "%04d" % self.sampling, False)
        elif self.currentEdit == 1:
            self.pps = self.pps + delta
            if self.pps > 60:
                self.pps = 60
            if self.pps < 1:
                self.pps = 1
            self.RenderParamForm(1, "Param", "%04d" % self.pps, "pps", True) # PPS            
            self.RenderUpdateParamRow(1, "%04d" % self.pps, False)
        elif self.currentEdit == 2:
            self.packetSize = self.packetSize + delta
            if self.packetSize > 1280:
                self.packetSize = 1280
            if self.packetSize < 64:
                self.packetSize = 64
            self.RenderParamForm(1, "Param", "%04d" % self.packetSize, "byte", True) # Size
            self.RenderUpdateParamRow(2, "%4d" % self.packetSize, False)

    def RenderParamRowBt(self, idx, isActive=False):

        if isActive == False:
            c = self.pRender.ConvRgb(0.14, 0.8, 0.7)
            self.pRender.fb.draw.rect(c, Rect(238 + 3 + 80, 84 + 50 * idx + 4, 2,
                                              40), 0)
            self.pRender.fb.draw.rect(
                c, Rect(238 + 2 + 55 + 80, 84 + 50 * idx + 4, 2, 40), 0)
            self.pRender.fb.draw.rect(
                c, Rect(238 + 3 + 80, 84 + 50 * idx + 4 + 38, 56, 2), 0)

        if isActive == True:
            c = self.pRender.ConvRgb(0.9, 1.0, 1.0)
            self.pRender.fb.draw.rect(c, Rect(241 + 80, 88 + 50 * idx, 56, 2), 0)
            self.pRender.fb.draw.rect(c, Rect(241 + 80, 88 + 50 * idx + 38, 56, 2),
                                      0)
            self.pRender.fb.draw.rect(c, Rect(241 + 80, 88 + 50 * idx, 2, 40), 0)
            self.pRender.fb.draw.rect(c, Rect(241 + 54 + 80, 88 + 50 * idx, 2, 40),
                                      0)

        c = self.pRender.ConvRgb(0.51, 0.3, 0.2)
        self.pRender.fb.draw.rect(c, Rect(243 + 80, 90 + 50 * idx + 32, 52, 4), 0)

        c = self.pRender.ConvRgb(0.51, 0.6, 0.79)
        if isActive == True:
            self.pRender.fb.draw.rect(c, Rect(243 + 80, 90 + 50 * idx, 52, 35), 0)
            self.pRender.fb.putstr(243 + 3 + 80, 90 + 50 * idx + 11, "LINK",
                                   self.pRender.N, 2)
        else:
            self.pRender.fb.draw.rect(c, Rect(243 + 80, 90 + 50 * idx - 2, 52, 35),
                                      0)
            self.pRender.fb.putstr(243 + 3 + 80, 90 + 50 * idx + 11 - 2, "EDIT",
                                   self.pRender.N, 2)

    def RenderUpdateParamRow(self, idx, value, isUp=True):
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
                       isActive):

        c = self.pRender.ConvRgb(0.44, 0.3, 0.9)
        self.pRender.fb.putstr(306 + 80, 110 + 50 * idx, DwValue, c, 2)

        c = self.pRender.ConvRgb(0.14, 0.8, 0.7)
        self.pRender.fb.draw.rect(c, Rect(238 + 80, 84 + 50 * idx, 229-80, 2), 0)
        self.pRender.fb.draw.rect(c, Rect(238 + 80, 84 + 50 * idx + 45, 229-80, 2), 0)
        self.pRender.fb.draw.rect(c, Rect(238 + 80, 84 + 50 * idx, 2, 47), 0)
        self.pRender.fb.draw.rect(c, Rect(238 + 207 + 20, 84 + 50 * idx, 2,
                                          47), 0)
        self.pRender.fb.draw.rect(c, Rect(238 + 2 + 80, 84 + 50 * idx + 2, 60, 43),
                                  0)
        self.pRender.fb.putstr(306 + 130, 116 + 50 * idx, DwUnit,
                               self.pRender.W, 1)
        
        c = self.pRender.ConvRgb(0, 0, 0.5)
        self.pRender.fb.draw.rect(c, Rect(304 + 80, 102 + 50 * idx, 157 - 80, 1), 0)
        self.pRender.fb.putstr(306 + 80, 88 + 50 * idx + 4, DwLabel,
                               self.pRender.W, 1)

        self.RenderParamRowBt(idx, isActive)

        return

    def RenderParamUI(self, idx):
        c = self.pRender.W
        self.pRender.fb.putstr(116 * idx + 8 + 33 + 80, 152 + 30 * 0, " 1", c, 2)
        self.pRender.fb.putstr(116 * idx + 8 + 33 + 6 + 80, 152 + 30 + 1, "10", c,
                               2)
        self.pRender.fb.putstr(116 * idx + 8 + 33 + 80, 152 + 30 * 2, "100", c, 2)

        c = self.pRender.ConvRgb(0.44, 0.9, 0.7)
        self.pRender.fb.draw.rect(c, Rect(116 * idx + 8 + 80, 146 + 30 * 0, 30, 26),
                                  0)
        self.pRender.fb.draw.rect(
            c, Rect(116 * idx + 8 + 72 + 80, 146 + 30 * 0, 30, 26), 0)
        self.pRender.fb.draw.rect(c, Rect(116 * idx + 8 + 80, 146 + 30 * 1, 30, 26),
                                  0)
        self.pRender.fb.draw.rect(
            c, Rect(116 * idx + 8 + 72 + 80, 146 + 30 * 1, 30, 26), 0)
        self.pRender.fb.draw.rect(c, Rect(116 * idx + 8 + 80, 146 + 30 * 2, 30, 26),
                                  0)
        self.pRender.fb.draw.rect(
            c, Rect(116 * idx + 8 + 72 + 80, 146 + 30 * 2, 30, 26), 0)

        c = self.pRender.ConvRgb(0.44, 0.1, 1)
        self.pRender.fb.putstr(116 * idx + 8 + 5 + 80, 145 + 30 * 0, "-", c, 4)
        self.pRender.fb.putstr(116 * idx + 8 + 77 + 80, 145 + 30 * 0, "+", c, 4)
        self.pRender.fb.putstr(116 * idx + 8 + 5 + 80, 145 + 30 * 1, "-", c, 4)
        self.pRender.fb.putstr(116 * idx + 8 + 77 + 80, 145 + 30 * 1, "+", c, 4)
        self.pRender.fb.putstr(116 * idx + 8 + 5 + 80, 145 + 30 * 2, "-", c, 4)
        self.pRender.fb.putstr(116 * idx + 8 + 77 + 80, 145 + 30 * 2, "+", c, 4)

    def SwitchLink(self, idx):
        # @todo if same idx, skip.
        if idx == 0:
            self.RenderParamForm(1, "Param", "%04d" % self.sampling, "pkt") # Sampling
        elif idx == 1:
            self.RenderParamForm(1, "Param", "%04d" % self.pps, "pps") # PPS
        elif idx == 2:
            self.RenderParamForm(1, "Param", "%04d" % self.packetSize, "byte") # Size
        else:
            return
        if self.currentEdit != idx:
            self.RenderParamRowBt(idx, True)
            self.RenderParamRowBt(self.currentEdit, False)
            self.currentEdit = idx

    def RenderParamForm(self, idx, label, value, unit, isParamOnly=False):

        if isParamOnly == True:
            self.pRender.fb.draw.rect(self.pRender.N,
                                      Rect(116 * idx + 12 + 80, 112, 60, 18), 0)
        else:
            self.pRender.fb.draw.rect(self.pRender.N,
                                      Rect(116 * idx + 8 + 34 + 80, 84, 62, 16), 0)
            self.pRender.fb.draw.rect(self.pRender.N,
                                      Rect(116 * idx + 18 + 80, 114, 82, 16), 0)

        c = self.pRender.ConvRgb(0.94, 0.8, 0.9)
        self.pRender.fb.putstr(116 * idx + 8 + 10 + 80, 114, value, c, 2)

        if isParamOnly == True:
            return

        c = self.pRender.ConvRgb(0.44, 0.3, 0.9)
        self.pRender.fb.putstr(116 * idx + 8 + 80, 85, label, c, 2)
        self.pRender.fb.putstr(116 * idx + 8 + 10 + 58 + 80, 120, unit,
                               self.pRender.W, 1)

        c = self.pRender.ConvRgb(0.4, 0.6, 0.4)
        self.pRender.fb.draw.rect(c, Rect(116 * idx + 8 + 80, 100, 100, 2), 0)
        self.pRender.fb.draw.rect(c, Rect(116 * idx + 8 + 80, 100 + 40, 100, 2), 0)
        self.pRender.fb.draw.rect(c, Rect(116 * idx + 8 + 80, 100, 2, 40), 0)
        self.pRender.fb.draw.rect(c, Rect(116 * idx + 8 + 100 + 80, 100, 2, 42), 0)

    def RenderWire(self, isActive):
        if isActive == True:
            c = self.pRender.ConvRgb(0.18, 1.0, 1.0)
        else:
            c = self.pRender.ConvRgb(0.44, 0.0, 0.7)
        self.pRender.fb.draw.rect(c, Rect(234 + 80, 80, 238 - 80, 1), 0)
        self.pRender.fb.draw.rect(c, Rect(234 + 80, 80 + 154, 238 - 80, 1), 0)
        self.pRender.fb.draw.rect(c, Rect(234 + 80, 80, 1, 154), 0)
        self.pRender.fb.draw.rect(c, Rect(234 + 237, 80, 1, 154), 0)
        self.pRender.fb.draw.rect(c, Rect(248 + 150, 80 + 154 + 1, 2, 2), 0)
        self.pRender.fb.draw.rect(c, Rect(248 + 152, 80 + 154 + 1, 2, 4), 0)
        self.pRender.fb.draw.rect(c, Rect(248 + 154, 80 + 154 + 1, 2, 6), 0)
        self.pRender.fb.draw.rect(c, Rect(248 + 156, 80 + 154 + 1, 2, 4), 0)
        self.pRender.fb.draw.rect(c, Rect(248 + 158, 80 + 154 + 1, 2, 2), 0)

    def RenderMetricsSummary(self):
        
        c = self.pRender.ConvRgb(0.4, 0.6, 0.4)
        #c = self.pRender.ConvRgb(0.18, 1.0, 1.0)
        self.pRender.fb.draw.rect(c, Rect(8, 100, 186, 2), 0)
        
        c = self.pRender.ConvRgb(0.44, 0.3, 0.9)
        #c = self.pRender.ConvRgb(0.18, 0.8, 0.8)
        self.pRender.fb.putstr(16, 85, "Metrics v6|v4", c, 2)

        c = self.pRender.W
        self.pRender.fb.putstr(8, 112 + 16 * 0, "> RTT (AVG)", c, 1)
        self.pRender.fb.putstr(8, 112 + 16 * 1, "> RTT (MDN)", c, 1)
        self.pRender.fb.putstr(8, 112 + 16 * 2, "> RTT (MAX)", c, 1)
        self.pRender.fb.putstr(8, 112 + 16 * 3, "> RTT (MIN)", c, 1)
        self.pRender.fb.putstr(8, 112 + 16 * 4, "> Pkt Loss", c, 1)
        self.pRender.fb.putstr(8, 112 + 16 * 5, "> Send Cnt", c, 1)
        self.pRender.fb.putstr(8, 112 + 16 * 6, "> Recv Cnt", c, 1)
        self.pRender.fb.putstr(8, 112 + 16 * 7, "> Drop Cnt", c, 1)

        # v4 Metrics
        self.pRender.fb.putstr(24 + 114, 112 + 16 * 0, "%5d msec" % 0, c, 1)
        self.pRender.fb.putstr(24 + 114, 112 + 16 * 1, "%5d msec" % 0, c, 1)
        self.pRender.fb.putstr(24 + 114, 112 + 16 * 2, "%5d msec" % 0, c, 1)
        self.pRender.fb.putstr(24 + 114, 112 + 16 * 3, "%5d msec" % 0, c, 1)
        self.pRender.fb.putstr(24 + 114 - 6, 112 + 16 * 4, "%6.2f" % 0.00 + " %", c, 1)
        self.pRender.fb.putstr(24 + 114, 112 + 16 * 5, "%5d pkt" % 0, c, 1)
        self.pRender.fb.putstr(24 + 114, 112 + 16 * 6, "%5d pkt" % 0, c, 1)
        self.pRender.fb.putstr(24 + 114, 112 + 16 * 7, "%5d pkt" % 0, c, 1)

        # v6 Metrics
        self.pRender.fb.putstr(24 + 64, 112 + 16 * 0, "%5d |" % 0, c, 1)
        self.pRender.fb.putstr(24 + 64, 112 + 16 * 1, "%5d |" % 0, c, 1)
        self.pRender.fb.putstr(24 + 64, 112 + 16 * 2, "%5d |" % 0, c, 1)
        self.pRender.fb.putstr(24 + 64, 112 + 16 * 3, "%5d |" % 0, c, 1)
        self.pRender.fb.putstr(24 + 64 - 6, 112 + 16 * 4, "%6.2f |" % 0.00, c, 1)
        self.pRender.fb.putstr(24 + 64, 112 + 16 * 5, "%5d |" % 0, c, 1)
        self.pRender.fb.putstr(24 + 64, 112 + 16 * 6, "%5d |" % 0, c, 1)
        self.pRender.fb.putstr(24 + 64, 112 + 16 * 7, "%5d |" % 0, c, 1)
        
    def RenderMetrics4(self, rttavg, rttmdn, rttmax, rttmin, lossRate, sendNr, recvNr, dropNr):

        # ClearArea
        self.pRender.fb.draw.rect(self.pRender.N,
                                  Rect(78 + 50, 108, 88 - 50 + 4, 16 * 8), 0)

        c = self.pRender.W
        self.pRender.fb.putstr(24 + 114, 112 + 16 * 0, "%5d msec" % rttavg, c, 1)
        self.pRender.fb.putstr(24 + 114, 112 + 16 * 1, "%5d msec" % rttmdn, c, 1)
        self.pRender.fb.putstr(24 + 114, 112 + 16 * 2, "%5d msec" % rttmax, c, 1)
        self.pRender.fb.putstr(24 + 114, 112 + 16 * 3, "%5d msec" % rttmin, c, 1)
        self.pRender.fb.putstr(24 + 114 - 6, 112 + 16 * 4, "%6.2f" % lossRate + " %", c, 1)
        self.pRender.fb.putstr(24 + 114, 112 + 16 * 5, "%5d pkt" % sendNr, c, 1)
        self.pRender.fb.putstr(24 + 114, 112 + 16 * 6, "%5d pkt" % recvNr, c, 1)
        self.pRender.fb.putstr(24 + 114, 112 + 16 * 7, "%5d pkt" % dropNr, c, 1)
        
    def RenderMetrics6(self, rttavg, rttmdn, rttmax, rttmin, lossRate, sendNr, recvNr, dropNr):

        # ClearArea
        self.pRender.fb.draw.rect(self.pRender.N,
                                  Rect(74, 108, 45, 16 * 8), 0)
        
        c = self.pRender.W
        self.pRender.fb.putstr(24 + 64, 112 + 16 * 0, "%5d" % rttavg, c, 1)
        self.pRender.fb.putstr(24 + 64, 112 + 16 * 1, "%5d" % rttmdn, c, 1)
        self.pRender.fb.putstr(24 + 64, 112 + 16 * 2, "%5d" % rttmax, c, 1)
        self.pRender.fb.putstr(24 + 64, 112 + 16 * 3, "%5d" % rttmin, c, 1)
        self.pRender.fb.putstr(24 + 64 - 6, 112 + 16 * 4, "%6.2f" % lossRate, c, 1)
        self.pRender.fb.putstr(24 + 64, 112 + 16 * 5, "%5d" % sendNr, c, 1)
        self.pRender.fb.putstr(24 + 64, 112 + 16 * 6, "%5d" % recvNr, c, 1)
        self.pRender.fb.putstr(24 + 64, 112 + 16 * 7, "%5d" % dropNr, c, 1)
        
    def RenderGraphBar(self, idx, time, rate):
        if rate >= 37:
            c = self.pRender.R
        elif rate >= 25:
            c = self.pRender.O
        elif rate >= 13:
            c = self.pRender.Y
        elif rate >= 2:
            c = self.pRender.B
        else :
            c = self.pRender.W
            
        self.pRender.fb.draw.rect(self.pRender.N, Rect(85 + time, 241 + idx * 40, 1, 37), 0)
        self.pRender.fb.draw.rect(c, Rect(85 + time, 241+(37-rate) + idx * 40, 1, rate), 0)

    def GenerateSessionId(self, n = 8):
        randlst = [random.choice(string.ascii_letters + string.digits) for i in range(n)]
        return ''.join(randlst)
    
    def Start(self):
        super(ScMetricsMon, self).Start()

        ##[ PARAM ]################################################################

        self.upBand = 300
        self.dwBand = 300
        self.upDelay = 60
        self.dwDelay = 60
        self.upLoss = 128
        self.dwLoss = 128
        self.isApply = 0
        self.currentEdit = 0

        self.sampling   = 300
        self.pps        = 30
        self.packetSize = 128
        
        ##[ RENDER ]################################################################

        self.pRender.UpdateTitle("Realtime Metrics Monitor")
        self.pRender.UpdateSubTitle("Monitoring Status : Monitoring")

        c = yellow = self.pRender.fb.rgb(255, 255, 0)
        self.pRender.fb.draw.rect(c, Rect(0, 54, self.pRender.xres, 1), 0)
        self.pRender.fb.draw.rect(c, Rect(0, 74, self.pRender.xres, 1), 0)
        self.pRender.fb.draw.rect(c, Rect(0, 54, 10 + 60, 20), 0)
        self.pRender.fb.draw.rect(c, Rect(480 - 10, 54, 10, 20), 0)
        self.pRender.fb.putstr(26, 54 + 7, ">>>", self.pRender.N, 1)
        
        self.RenderBackBt(True)
        self.RenderWire(False)

        self.RenderParamRow(0, "Up Band", "%04d" % self.upBand, "kbps",
                            "Sampling", "%04d" % self.sampling, "pkt", True)
        self.RenderParamRow(1, "Up Delay", "%04d" % self.upDelay, "msec",
                            "PPS", "%04d" % self.pps, "pps", False)
        self.RenderParamRow(2, "Up Loss", "%4d" % self.upLoss, "%",
                            "Packet Size", "%04d" % self.packetSize, "byte", False)

        self.RenderParamForm(1, "Param", "%04d" % self.dwBand, "pkt")
        self.RenderParamUI(1)

        self.RenderMetricsSummary()

        self.testV4Enabled = True
        if V6Util.IsV6Enabled() == True:
            self.testV6Enabled = True
        else:
            self.testV6Enabled = False

        self.v4SessionId = self.GenerateSessionId()
        self.v6SessionId = self.GenerateSessionId()

        print("v4 sess: " + self.v4SessionId)
        print("v6 sess: " + self.v6SessionId) 
       
        self.collector = MetricsCollector(self.v4SessionId, self.v6SessionId, '0.0.0.0')
        self.proc4 = None
        self.proc6 = None
        
        self.graphSeek = 0
        self.graphLen = 240
        self.graphAf = 0
        
        self.RenderApplyBt()

        self.metricsGraph = MetricsGraph(self.pRender, self.graphLen)
        self.metricsGraph.RenderGraphBase()

        self.captureTool = CaptureTool(self.pRender, 0, 0)
        self.captureTool.RenderBt()
        
        return

    def UpdateMetrics4(self):
        # Render
        metrics = self.collector.GetLastMetrics4()
        self.RenderMetrics4(
            metrics.RttAvg()
            ,metrics.RttMdn()
            ,metrics.RttMax()
            ,metrics.RttMin()
            ,metrics.LossRate()
            ,metrics.sendSum
            ,metrics.recvSum
            ,metrics.dropSum
        )

        self.metricsGraph.AddGraphValue(0, metrics.LossRate(), metrics.RttMax())
        
        return
    
        if self.graphAf == 0:
            rttRate = int(metrics.RttMax() / 10)
            if rttRate > 37:
                rttRate = 37
            elif rttRate < 1:
                rttRate = 1                
            self.RenderGraphBar(1, self.graphSeek, rttRate)

            lossRate = int(round(metrics.LossRate() * 5))
            if lossRate > 37:
                lossRate = 37
            self.RenderGraphBar(0, self.graphSeek, lossRate)
            
            self.graphSeek = (self.graphSeek + 1) % self.graphLen
            
    def UpdateMetrics6(self):
        # Render
        metrics = self.collector.GetLastMetrics6()
        self.RenderMetrics6(
            metrics.RttAvg()
            ,metrics.RttMdn()
            ,metrics.RttMax()
            ,metrics.RttMin()
            ,metrics.LossRate()
            ,metrics.sendSum
            ,metrics.recvSum
            ,metrics.dropSum
        )

        self.metricsGraph.AddGraphValue(1, metrics.LossRate(), metrics.RttMax())

        return
        
        if self.graphAf == 1:
            rttRate = int(metrics.RttMax() / 10)
            if rttRate > 37:
                rttRate = 37
            elif rttRate < 1:
                rttRate = 1                
            self.RenderGraphBar(1, self.graphSeek, rttRate)

            lossRate = int(round(metrics.LossRate() * 5))
            if lossRate > 37:
                lossRate = 37
            self.RenderGraphBar(0, self.graphSeek, lossRate)
            
            self.graphSeek = (self.graphSeek + 1) % self.graphLen
    
    def Update(self):
        chkSet = [False, False]
        if self.collector.Recv(chkSet) == True:
            if chkSet[0] == True:
                self.UpdateMetrics4()
            elif chkSet[1] == True:
                self.UpdateMetrics6()
            
            # metrics.Dump()
            #if (self.collector.GetMetricsCount() % 5) == 0:
            #    print("==[ SUM ] ============================")
            #    metrics = self.collector.GetLastMetrics()
            #    metrics.Dump()
            #    print("======================================")
                
        if (self.proc4 != None) and (self.proc4.poll() != None):
            self.StartProbeV4()
        if (self.proc6 != None) and (self.proc6.poll() != None):
            self.StartProbeV6()
            
    def _StartProbe(self, server, pps, count, timeout, sampling, padSize, sid, af):
        bin = self.pCTX.metricsProcessBinPath
        # MetricsCollectorと測定プロセスは同一マシンで動く前提
        # MetricsPacketが、Sampling数次第ではMTUを超えるため、Loopback経由での通信を奨励
        # 分離したい場合は、Samplingのパラメータを抑えること
        cmd = bin + " " + af + " -host " + server + " -timeout " + timeout + " -c " + count + " -pps " + pps + " -m 127.0.0.1" + " -sid " + sid + " -sample " + sampling
        if padSize != "0":
            cmd = cmd + " -pad " + padSize
        return subprocess.Popen("exec " + cmd, shell=True)

    def StartProbeV4(self):
        if self.testV4Enabled == True:
            server   = self.pCTX.metricsServer
            pps      = str(self.pps)
            count    = str(self.pps * self.pCTX.metricsProcessCycleSec) 
            timeout  = str(self.pCTX.metricsRecvTimeoutMsec) 
            sampling = str(self.sampling)
            pktCount = str(self.sampling * self.pps)
            # ip header + udp header + stun header + padding attr header = 52
            padSize  = str(self.packetSize - 52)
            if self.packetSize < 52:
                padSize = str(0)
            self.proc4 = self._StartProbe(server, pps, count, timeout, sampling, padSize, self.v4SessionId, "-4")

    def StartProbeV6(self):
        if self.testV6Enabled == True:
            server   = self.pCTX.metricsServer
            pps      = str(self.pps)
            count    = str(self.pps * self.pCTX.metricsProcessCycleSec)
            timeout  = str(self.pCTX.metricsRecvTimeoutMsec) 
            sampling = str(self.sampling)
            pktCount = str(self.sampling * self.pps)
            # ip header + udp header + stun header + padding attr header = 72
            padSize  = str(self.packetSize - 72)
            if self.packetSize < 72:
                padSize = str(0)
            self.proc6 = self._StartProbe(server, pps, count, timeout, sampling, padSize, self.v6SessionId, "-6")
           
    def StartProbe(self):
        self.StartProbeV4()
        self.StartProbeV6()        
        return
    
    def StopProbe(self):
        if self.proc4 != None:
            self.proc4.kill()
            self.proc4 = None
        if self.proc6 != None:
            self.proc6.kill()
            self.proc6 = None

        # 暫定：ゾンビプロセスをここでついでに消す
        # TODO：初期化時に残存プロセスがあれば落とす
        cmd = "kill all -9 StunTool.bin"
        try:
            subprocess.check_call(cmd.strip().split(" "))
        except subprocess.CalledProcessError:
            print("Zombie Process Not Found.")
            
        return

    def RenderV6TestSwitch(self):
        if self.testV6Enabled == True:
            c = self.pRender.R
        else:
            c = self.pRender.N
        self.pRender.fb.draw.rect(c, Rect(338+4, 248+10, 6, 6), 0)
        
    def RenderV4TestSwitch(self):
        if self.testV4Enabled == True:
            c = self.pRender.R
        else:
            c = self.pRender.N
        self.pRender.fb.draw.rect(c, Rect(338+4, 284+10, 6, 6), 0)
        
    def RenderApplyBt(self):
        if self.isApply == 0:
            c = self.pRender.ConvRgb(0.18, 0.6, 0.6)
        else:
            c = self.pRender.ConvRgb(0.18, 1.0, 1.0)
                    
        self.pRender.fb.draw.rect(c, Rect(392, 80 * 3 + 8, 110 - 30, 44 + 18), 0)
        c = self.pRender.ConvRgb(0.18, 0.3, 0.3)
        self.pRender.fb.draw.rect(c, Rect(392, 80 * 3 + 8 + 44 + 18, 110 - 30, 4), 0)        
        self.pRender.fb.draw.rect(c, Rect(338, 248 + 26, 48, 4), 0)
        self.pRender.fb.draw.rect(c, Rect(338, 284 + 26, 48, 4), 0)

        if V6Util.IsV6Enabled() == True:
            c = self.pRender.ConvRgb(0.95, 0.7, 0.7)
        else:
            c = self.pRender.ConvRgb(0.95, 0.7, 0.2)            
        self.pRender.fb.draw.rect(c, Rect(338, 248, 48, 26), 0)

        c = self.pRender.ConvRgb(0.74, 0.98, 0.74)
        self.pRender.fb.draw.rect(c, Rect(338, 284, 48, 26), 0)
        
        self.pRender.fb.putstr(338 + 16, 248 + 6, "v6", 0, 2)
        self.pRender.fb.putstr(338 + 16, 284 + 6, "v4", 0, 2)

        self.RenderV6TestSwitch()
        self.RenderV4TestSwitch()
        
        if self.isApply == 0:
            self.pRender.fb.putstr(350 + 24 + 28, 80 * 3 + 22 + 9, "START", 0, 2)
        else:
            self.pRender.fb.putstr(350 + 24 + 6 + 28, 80 * 3 + 22 + 9, "STOP", 0, 2)

import time
from gfx import Rect
from RenderManager import RenderManager

class GraphNode():
    
    def __init__(self):
        self.lossStep = 0
        self.rttStep = 0
        
    def SetValue(self, lossRate, rtt):
        self.rttStep = int(rtt / 10)
        if self.rttStep > 37:
            self.rttStep = 37
        elif self.rttStep < 1:
            self.rttStep = 1

        self.lossStep = int(round(lossRate * 5))
        if self.lossStep > 37:
            self.lossStep = 37

    def GetLossStep(self):
        return self.lossStep

    def GetRttStep(self):
        return self.rttStep
            
class MetricsGraph():
    # nodeMax == graphWidth
    def __init__(self, pRender, nodeMax = 240):
        self.pRender = pRender        
        self.nodeList4 = []
        self.nodeList6 = []
        self.nodeCount4 = 0
        self.nodeCount6 = 0
        self.nodeNr     = nodeMax
        for idx in range(0, self.nodeNr):
            self.nodeList4.append(GraphNode())
            self.nodeList6.append(GraphNode())
        # 0: IPv4, 1: IPv6
        self.currentRenderAf = 0

    def AddGraphValue(self, af, lossRate, rtt):
        if af == 0:
            seek = self.nodeCount4 % self.nodeNr
            self.nodeList4[seek].SetValue(lossRate, rtt)
            if self.currentRenderAf == 0:                
                self.RenderSeek(seek, self.nodeList4[seek].GetLossStep(),
                                self.nodeList4[seek].GetRttStep())
            self.nodeCount4 = self.nodeCount4 + 1
        elif af == 1:
            seek = self.nodeCount6 % self.nodeNr
            self.nodeList6[seek].SetValue(lossRate, rtt)
            if self.currentRenderAf == 1:
                self.RenderSeek(seek, self.nodeList6[seek].GetLossStep(),
                                self.nodeList6[seek].GetRttStep())
            self.nodeCount6 = self.nodeCount6 + 1

    def RenderGraphBase(self):
        c = self.pRender.ConvRgb(0.16, 1, 0.6)
        #self.pRender.fb.draw.rect(c, Rect(1,      160, self.pRender.xres-2, 1), 0)
        self.pRender.fb.draw.rect(
            c, Rect(1, 239, self.pRender.xres - 2 - 150, 1), 0)
        self.pRender.fb.draw.rect(
            c, Rect(1, 239 + 40, self.pRender.xres - 2 - 150, 1), 0)
        self.pRender.fb.draw.rect(
            c, Rect(self.pRender.xres - 150 - 1, 240, 1, 79), 0)
        
        self.pRender.fb.draw.rect(c, Rect(2, 241, 80, 37), 0)
        self.pRender.fb.draw.rect(c, Rect(2, 241 + 40, 80, 37), 0)
        
        self.pRender.fb.putstr(12+7, 241 + 7 + 5 - 5, "LOSS", self.pRender.W, 2)
        self.pRender.fb.putstr(12+7, 241 + 7 + 5 + 40 + 5, " RTT", self.pRender.W, 2)

        c = self.pRender.ConvRgb(0.18, 0.3, 0.1)
        self.pRender.fb.draw.rect(c, Rect(12, 267, 60, 24), 0)

        self.RenderGraphAfBt()
        
    def RenderGraphAfBt(self):
        if self.currentRenderAf == 0:
            c = self.pRender.ConvRgb(0.74, 0.98, 0.74)
            self.pRender.fb.draw.rect(c, Rect(14, 268, 56, 20), 0)
            self.pRender.fb.putstr(31, 271, "v4", 0, 2)            
        elif self.currentRenderAf == 1:
            c = self.pRender.ConvRgb(0.95, 0.7, 0.7)        
            self.pRender.fb.draw.rect(c, Rect(14, 268, 56, 20), 0)
            self.pRender.fb.putstr(31, 271, "v6", 0, 2)            
        
    def ToggleGraphAf(self):
        if self.currentRenderAf == 0:
            self.SwitchRenderAf(1)
        elif self.currentRenderAf == 1:
            self.SwitchRenderAf(0)
            
    def SwitchRenderAf(self, af):
        if self.currentRenderAf == af:
            return 

        self.currentRenderAf = af
        self.RenderGraphAfBt()
        self.RenderFull()

    def _RenderSeek(self, rowIdx, seek, value):
        if value >= 37:
            c = self.pRender.R
        elif value >= 25:
            c = self.pRender.O
        elif value >= 13:
            c = self.pRender.Y
        elif value >= 2:
            c = self.pRender.B
        else :
            c = self.pRender.W
            
        self.pRender.fb.draw.rect(self.pRender.N, Rect(85 + seek, 241 + rowIdx * 40, 1, 37), 0)
        if value > 0:
            self.pRender.fb.draw.rect(c, Rect(85 + seek, 241+(37-value) + rowIdx * 40, 1, value), 0)
        
    def RenderSeek(self, seek, lossStep, rttStep):
        self._RenderSeek(0, seek, lossStep)
        self._RenderSeek(1, seek, rttStep)
        self.RenderCursor(seek)
        
    def RenderCursor(self, seek):
        self.pRender.fb.draw.rect(self.pRender.N, Rect(83, 236, 244, 3), 0)
        self.pRender.fb.draw.rect(self.pRender.W, Rect(83 + seek, 236, 5, 1), 0)
        self.pRender.fb.draw.rect(self.pRender.W, Rect(84 + seek, 237, 3, 1), 0)
        self.pRender.fb.draw.rect(self.pRender.W, Rect(85 + seek, 238, 1, 1), 0)        
        
    def RenderFull(self):
        #self.pRender.fb.draw.rect(self.pRender.N, Rect(85, 241, self.nodeNr, 37), 0)
        #self.pRender.fb.draw.rect(self.pRender.N, Rect(85, 281, self.nodeNr, 37), 0)
        self.pRender.fb.draw.rect(self.pRender.N, Rect(83, 236, 244, 3), 0)

        for idx in range(0, self.nodeNr):
            if self.currentRenderAf == 0:
                self._RenderSeek(0, idx, self.nodeList4[idx].GetLossStep())
                self._RenderSeek(1, idx, self.nodeList4[idx].GetRttStep())
            elif self.currentRenderAf == 1:
                self._RenderSeek(0, idx, self.nodeList6[idx].GetLossStep())
                self._RenderSeek(1, idx, self.nodeList6[idx].GetRttStep())
                

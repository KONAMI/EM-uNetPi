import sys, getopt, struct, time, termios, fcntl, sys, os, colorsys
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/fbtft')
from RenderManager import RenderManager
from WanemManager import WanemManager
from gfx import Rect
from DataAsset import CTX


class ScBase(object):
    def __init__(self, pCTX, pRender, pWanem):
        self.pCTX = pCTX
        self.pRender = pRender
        self.pWanem = pWanem

        self.STATE_INIT = 0
        self.STATE_TERM = 100
        self.state = self.STATE_INIT
        self.nextScene = ""
        self.ptDef = []

    def TouchDownHandler(self, x, y):
        print "TouchDownHandler Pos >> " + str(x) + " : " + str(y)
        self.CallTouchFunc(x, y, True)
        return

    def TouchUpHandler(self, x, y):
        print "TouchUpHandler Pos >> " + str(x) + " : " + str(y)
        self.CallTouchFunc(x, y, False)
        return

    def Start(self):
        self.pRender.Clear()

        c = yellow = self.pRender.fb.rgb(255, 255, 0)
        self.pRender.fb.draw.rect(
            c, Rect(0, 0, self.pRender.fb.xres - 1, self.pRender.fb.yres - 1),
            1)
        self.pRender.fb.draw.rect(c, Rect(2, 2, 4, 4), 0)
        self.pRender.fb.draw.rect(c, Rect(2, self.pRender.fb.yres - 6, 4, 4),
                                  0)
        self.pRender.fb.draw.rect(c, Rect(self.pRender.fb.xres - 6, 2, 4, 4),
                                  0)
        self.pRender.fb.draw.rect(
            c, Rect(self.pRender.fb.xres - 6, self.pRender.fb.yres - 6, 4, 4),
            0)

        self.state = self.STATE_INIT

        return

    def Update(self):
        return

    def RenderBackBt(self, enabled):
        if enabled:
            c = self.pRender.ConvRgb(0.10, 0.2, 0.8)
        else:
            c = self.pRender.ConvRgb(0.10, 0.2, 0.3)
        self.pRender.fb.draw.rect(c, Rect(7, 7, 62, 38), 0)
        c = self.pRender.ConvRgb(0.10, 0.2, 0.2)
        self.pRender.fb.draw.rect(c, Rect(7, 7 + 38, 62, 4), 0)
        self.pRender.fb.putstr(7 + 8, 7 + 12, "Back", c, 2)

    def CallTouchFunc(self, x, y, isOnDown):
        for idx in range(0, len(self.ptDef)):
            pt = self.ptDef[idx]
            if pt[7] != True:
                continue
            if x >= (pt[1] - pt[3]) and x <= pt[1] and y > pt[2] and y < (
                    pt[2] + pt[4]):
                if isOnDown == True:
                    if pt[5] is not None:
                        pt[5](pt[0])
                else:
                    if pt[6] is not None:
                        pt[6](pt[0])
                break

    def SetTouchActive(self, k, isActive):
        for idx in range(0, len(self.ptDef)):
            pt = self.ptDef[idx]
            if pt[0] == k:
                pt[7] = isActive

    def CreateTocuhDef(self,
                       k,
                       x,
                       y,
                       w,
                       h,
                       fOnDown=None,
                       fOnUp=None,
                       isActive=True):
        return [k, x, y, w, h, fOnDown, fOnUp, isActive]

    def GetSelfId(self):
        cpuserial = "0000000000000000"
        try:
            f = open('/proc/cpuinfo', 'r')
            for line in f:
                #print(line)
                if len(line) > 16:
                    if line[0:6] == 'Serial':
                        #print("####### HIT");
                        cpuserial = line[10:26]
                        break
            f.close()
        except Exception as e:
            print '=== EXCEPTION ==='
            print 'type:' + str(type(e))
            print 'args:' + str(e.args)
            print 'message:' + e.message
            print 'e:' + str(e)
            cpuserial = "00000000000ERROR"

        return cpuserial[10:16]

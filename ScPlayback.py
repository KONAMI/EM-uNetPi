import sys, getopt, struct, time, termios, fcntl, sys, os, colorsys, threading, time, datetime, subprocess, random, os.path, math, json
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/fbtft')
from RenderManager import RenderManager
from WanemManager import WanemManager
from ScBase import ScBase
from gfx import Rect
from DataAsset import CTX
from SeekManager import SeekManager


class ScPlayback(ScBase):
    def __init__(self, pCTX, pRender, pWanem):
        super(ScPlayback, self).__init__(pCTX, pRender, pWanem)

        self.STATE_IDLE = 1
        self.STATE_PLAY = 2
        self.STATE_PAUSE = 3

        self.ptDef.insert(
            0, self.CreateTocuhDef("BtBack", 468, 29, 62, 42, self.BtHandler))
        self.ptDef.insert(
            1, self.CreateTocuhDef("BtPrev", 470, 95, 43, 90, self.BtHandler))
        self.ptDef.insert(
            2, self.CreateTocuhDef("BtNext", 65, 95, 43, 90, self.BtHandler))
        #self.ptDef.insert(3, self.CreateTocuhDef("BtAuto",     460,       268,         80, 50, self.BtHandler))
        self.ptDef.insert(
            4, self.CreateTocuhDef("BtStop", 370, 268, 80, 50, self.BtHandler))
        self.ptDef.insert(
            5, self.CreateTocuhDef("BtPlay", 280, 268, 80, 50, self.BtHandler))
        self.ptDef.insert(
            6, self.CreateTocuhDef("BtPause", 190, 268, 80, 50,
                                   self.BtHandler))
        self.ptDef.insert(
            7, self.CreateTocuhDef("BtRepeat", 100, 268, 80, 50,
                                   self.BtHandler))
        #self.ptDef.insert(3, self.CreateTocuhDef("BtTargetL",  430,        95,        120, 90, self.BtHandler))
        #self.ptDef.insert(4, self.CreateTocuhDef("BtTargetC",  430,        95,        120, 90, self.BtHandler))
        #self.ptDef.insert(5, self.CreateTocuhDef("BtTargetR",  430,        95,        120, 90, self.BtHandler))

    def BtHandler(self, key):
        print "BtHandler" + key + " @ " + str(self.state)

        if key == "BtBack":
            if self.state == self.STATE_IDLE:
                self.pWanem.Clear()
                self.nextScene = "Replay"
                self.state = self.STATE_TERM
        elif key == "BtPrev":
            if self.state == self.STATE_IDLE:
                self.UpdatePanel(-1)
        elif key == "BtNext":
            if self.state == self.STATE_IDLE:
                self.UpdatePanel(1)
        elif key == "BtStop":
            if self.state == self.STATE_PLAY or self.state == self.STATE_PAUSE:
                self.StopHandler()
        elif key == "BtPlay":
            if self.state == self.STATE_IDLE:
                self.RenderCurrentInfo("PLAYING")
                self.PlayHandler()
        elif key == "BtPause":
            if self.state == self.STATE_PLAY:
                self.seekManager.isPause = True
            elif self.state == self.STATE_PAUSE:
                self.seekManager.isPause = False
        elif key == "BtRepeat":
            self.seekManager.isRepeat = not self.seekManager.isRepeat
            self.RenderToggleFocus(4, self.seekManager.isRepeat)

    def RenderPanel(self, panelIdx, isActive, isFocus=False, datPath=""):

        offsetX = 128 * panelIdx

        if isActive == False:
            c = self.pRender.ConvRgb(0.31, 0.2, 0.2)
            self.pRender.fb.draw.rect(c, Rect(52 + offsetX, 84, 120, 90), 0)
            return

        targetPath = self.pCTX.currentReplayData + "/" + datPath
        file = open(targetPath)
        dat = json.load(file)
        file.close()

        mtime = os.path.getmtime(targetPath)
        t = datetime.datetime.fromtimestamp(mtime)
        datMtime = t.strftime("%y/%m/%d")

        c = self.pRender.ConvRgb(0.31, 0.2, 0.8)
        self.pRender.fb.draw.rect(c, Rect(52 + offsetX, 84, 120, 90), 0)

        c = self.pRender.ConvRgb(0.31, 0.2, 0.1)
        self.pRender.fb.putstr(52 + 10 + offsetX, 84 + 10, datPath[0:8], c, 2)

        c = self.pRender.ConvRgb(0.31, 0.2, 0.1)
        self.pRender.fb.putstr(52 + 10 + offsetX, 84 + 10 + 12 * 2, "Modify",
                               c, 1)
        self.pRender.fb.putstr(52 + 10 + 70 + offsetX, 84 + 10 + 12 * 2,
                               "Time", c, 1)
        self.pRender.fb.putstr(52 + 10 + offsetX, 84 + 10 + 12 * 3, datMtime,
                               c, 1)
        self.pRender.fb.putstr(
            52 + 10 + 70 + offsetX, 84 + 10 + 12 * 3,
            self.seekManager.Conv2FormatedTime(dat["dps"], dat["duration"]), c,
            1)
        self.pRender.fb.putstr(52 + 10 + offsetX, 84 + 10 + 12 * 4, "Memo", c,
                               1)
        self.pRender.fb.putstr(52 + 10 + offsetX, 84 + 10 + 12 * 5,
                               dat["memo"][0:17], c, 1)

        if isFocus:
            self.RenderGraph(dat["graph"])
            self.seekManager.Setup(dat["dps"], dat["duration"])
            self.RenderSeekInfo()
            self.dat = dat["dat"]

    def UpdatePanel(self, vec, forceClear=False):

        prevPageIdx = self.datPageIdx
        prevFocusIdx = self.datFocusIdx
        isPageSwitch = forceClear

        if (self.datPageIdx * 3 + self.datFocusIdx) == 0 and vec == -1:
            return
        if (self.datPageIdx * 3 + self.datFocusIdx) == (self.datNr -
                                                        1) and vec == 1:
            return
        if (self.datFocusIdx % 3) == 0 and vec == -1:
            self.datPageIdx -= 1
            isPageSwitch = True
        elif (self.datFocusIdx % 3) == 2 and vec == 1:
            self.datPageIdx += 1
            isPageSwitch = True

        self.datFocusIdx = (self.datFocusIdx + vec) % 3

        self.ClearFocus(prevFocusIdx)

        if isPageSwitch:

            self.datFocusIdx = 0

            # Render List
            # currentIdx = self.datPageIdx * 3 + self.datFocusIdx

            currentIdxTop = self.datPageIdx * 3
            focusIdx = 0
            for file in self.datList[currentIdxTop:currentIdxTop + 3]:
                if focusIdx == self.datFocusIdx:
                    self.RenderPanel(focusIdx, True, True, file)
                else:
                    self.RenderPanel(focusIdx, True, False, file)
                focusIdx += 1
            for idx in range(focusIdx, 3):
                self.RenderPanel(idx, False)
        else:
            currentIdxTop = self.datPageIdx * 3
            focusIdx = 0
            for file in self.datList[currentIdxTop:currentIdxTop + 3]:
                if focusIdx == self.datFocusIdx:
                    targetPath = self.pCTX.currentReplayData + "/" + file
                    file = open(targetPath)
                    dat = json.load(file)
                    file.close()
                    self.RenderGraph(dat["graph"])
                    self.seekManager.Setup(dat["dps"], dat["duration"])
                    self.RenderSeekInfo()
                    self.dat = dat["dat"]

                focusIdx += 1

        self.RenderFocus(self.datFocusIdx)

    def RenderFocus(self, idx):
        c = self.pRender.ConvRgb(1.00, 0.9, 0.8)
        self.pRender.fb.draw.rect(c, Rect(48 + 128 * idx, 84 - 4, 128, 4), 0)
        self.pRender.fb.draw.rect(
            c, Rect(48 + 128 * idx, 84 - 4 + 90 + 4, 128, 4), 0)
        self.pRender.fb.draw.rect(c, Rect(48 + 128 * idx, 84, 4, 90), 0)
        self.pRender.fb.draw.rect(c, Rect(48 + 128 * idx + 124, 84, 4, 90), 0)

    def RenderToggleFocus(self, idx, isActivey):
        if idx == 3:
            xoffset = 0
        elif idx == 4:
            xoffset = 90
        else:
            return
        if isActivey:
            c = self.pRender.ConvRgb(1.00, 0.9, 0.8)
        else:
            c = self.pRender.N
        self.pRender.fb.draw.rect(c, Rect(288 + xoffset, 264 - 2, 84, 2), 0)
        self.pRender.fb.draw.rect(c,
                                  Rect(288 + xoffset, 264 - 2 + 50 + 2, 84, 2),
                                  0)
        self.pRender.fb.draw.rect(c, Rect(288 + xoffset, 264, 2, 50), 0)
        self.pRender.fb.draw.rect(c, Rect(288 + xoffset + 82, 264, 2, 50), 0)

    def ClearFocus(self, idx):
        c = self.pRender.ConvRgb(0, 0, 0)
        self.pRender.fb.draw.rect(c, Rect(48 + 128 * idx, 84 - 4, 128, 4), 0)
        self.pRender.fb.draw.rect(
            c, Rect(48 + 128 * idx, 84 - 4 + 90 + 4, 128, 4), 0)
        self.pRender.fb.draw.rect(c, Rect(48 + 128 * idx, 84, 4, 90), 0)
        self.pRender.fb.draw.rect(c, Rect(48 + 128 * idx + 124, 84, 4, 90), 0)

    def RenderFootBt(self, idx, label, h):
        if idx == 0:
            x = 200 - 180
        elif idx == 1:
            x = 200 - 90
        elif idx == 2:
            x = 200 + 0
        elif idx == 3:
            x = 200 + 90
        elif idx == 4:
            x = 200 + 180

        c = self.pRender.ConvRgb(h, 0.6, 0.6)
        self.pRender.fb.draw.rect(c, Rect(x, 264, 80, 44), 0)
        c = self.pRender.ConvRgb(h, 0.6, 0.2)
        self.pRender.fb.draw.rect(c, Rect(x, 264 + 44, 80, 6), 0)
        if idx == 3:
            self.pRender.fb.putstr(x + 4 + 7, 278, label, c, 2)
        else:
            self.pRender.fb.putstr(x + 4, 278, label, c, 2)

    def RenderSeekInfo(self):
        self.pRender.fb.draw.rect(self.pRender.N, Rect(445, 219, 30, 7), 0)
        self.pRender.fb.putstr(445, 240 - 21,
                               self.seekManager.GetTotalFormatTime(),
                               self.pRender.W, 1)

    ################################################################################

    def Update(self):
        isRender = False

        if self.pCTX.tick == 1:
            isRender = True

        if self.state == self.STATE_PLAY:

            #######################################
            if isRender:
                if self.seekManager.isPause:
                    self.RenderToggleFocus(3, self.seekManager.isPause)
                    self.state = self.STATE_PAUSE
                    return
                self.seekManager.seekSec += 1

            if self.seekManager.seekSec < 0:
                return

            if self.seekManager.IsTerm():
                if self.seekManager.isRepeat:
                    self.RenderDotAll()
                    self.PlayHandler()
                    self.UpdateSeekTime()
                else:
                    self.StopHandler()
                return
            #######################################

            # check Seek diff and force loop and apply.
            # @todo variable fps
            if self.pCTX.tick % self.seekManager.updateInterval == 0:
                #datSeek = self.seekSec * 30 + int(self.pCTX.tick / 2)
                #if self.pCTX.tick >= 60:
                #	print str(self.pCTX.tick) + ":" + str(self.seekManager.seekFrame) + ":" + str(self.seekManager.updateInterval)
                self.pWanem.DirectApply(self.dat[self.seekManager.seekFrame])
                if (self.pCTX.tick % 15) == 0:
                    self.RenderCurrentInfo(
                        "", self.dat[self.seekManager.seekFrame])
                self.seekManager.Update(isRender)

            # nnn....
            if isRender:
                self.UpdateSeekTime()

        elif self.state == self.STATE_PAUSE:
            if not self.seekManager.isPause:
                self.RenderToggleFocus(3, self.seekManager.isPause)
                self.state = self.STATE_PLAY
                return

    ################################################################################

    def RenderDotAll(self):
        for idx in range(0, self.seekManager.progressBarResolution):
            self.RenderDot(idx, False)

    def RenderDot(self, idx, isFlush):
        w = 10
        h = 10
        if isFlush:
            c = self.pRender.ConvRgb(0.4, 1, 1)
        else:
            c = self.pRender.ConvRgb(0.4, 0.3, 0.3)
        xoffset = 11 * idx + 20
        self.pRender.fb.draw.rect(c, Rect(xoffset, 238, w, h), 0)

    def RenderGraph(self, graphDat):

        c = self.pRender.ConvRgb(0, 0, 0)
        self.pRender.fb.draw.rect(c, Rect(20, 186, 440, 30), 0)

        for idx in range(0, 440):
            xoffset = idx + 20
            h = graphDat[idx]

            #c = self.pRender.ConvRgb(1.0/440.0*idx,0.8,0.8)
            c = self.pRender.ConvRgb(1.0 / 30.0 * h, 0.8, 0.8)
            self.pRender.fb.draw.rect(c, Rect(xoffset, 216 - h, 1, h), 0)

    # Update block and seek string
    def UpdateSeekTime(self):
        if self.seekManager.seekLap >= self.seekManager.progressBarResolution:
            return

        self.pRender.fb.draw.rect(self.pRender.N, Rect(224, 219, 30, 7), 0)
        self.pRender.fb.putstr(224, 219,
                               self.seekManager.GetCurrentFormatTime(),
                               self.pRender.W, 1)

        while self.seekManager.IsSeekSecOverCurrentLap():
            self.RenderDot(self.seekManager.seekLap, True)
            self.seekManager.seekLap += 1
            if self.seekManager.seekLap >= self.seekManager.progressBarResolution:
                return

        self.isBlockFlash = not self.isBlockFlash
        self.RenderDot(self.seekManager.seekLap, self.isBlockFlash)

    def PlayHandler(self):
        self.seekManager.Start()
        self.state = self.STATE_PLAY
        self.RenderDotAll()

    def StopHandler(self):
        self.seekManager.Stop()
        self.state = self.STATE_IDLE
        self.UpdateSeekTime()
        self.RenderDotAll()
        self.RenderToggleFocus(3, self.seekManager.isPause)
        self.RenderCurrentInfo("STOP", 0)
        self.pWanem.DirectApply(0)

    def Start(self):
        super(ScPlayback, self).Start()

        ##[ INIT STATE ]################################################################

        self.progressBarResolution = 40
        self.seekManager = SeekManager(self.pCTX, self.progressBarResolution)

        self.state = self.STATE_IDLE
        self.isBlockFlash = False
        self.dat = None

        ##[ Get DataDir Info ]######################################################

        self.datList = os.listdir(self.pCTX.currentReplayData)
        self.datList.sort()
        self.datPageIdx = 0
        self.datNr = len(self.datList)
        self.datFocusIdx = 0

        ##[ RENDER ]################################################################

        self.pRender.UpdateTitle("WAN Emulation - Replay")
        self.pRender.UpdateSubTitle("Dat Path : " +
                                    self.pCTX.currentReplayData)

        c = yellow = self.pRender.fb.rgb(255, 255, 0)
        self.pRender.fb.draw.rect(c, Rect(0, 54, self.pRender.xres, 1), 0)
        self.pRender.fb.draw.rect(c, Rect(0, 74, self.pRender.xres, 1), 0)
        self.pRender.fb.draw.rect(c, Rect(0, 54, 10 + 60, 20), 0)
        self.pRender.fb.draw.rect(c, Rect(480 - 10, 54, 10, 20), 0)
        self.pRender.fb.putstr(26, 54 + 7, ">>>", self.pRender.N, 1)

        ######################

        self.UpdatePanel(0, True)

        c = self.pRender.ConvRgb(0.31, 0.2, 0.2)
        self.pRender.fb.draw.rect(c, Rect(1, 84, 43, 90), 0)
        self.pRender.fb.draw.rect(c, Rect(480 - 44, 84, 43, 90), 0)
        self.pRender.fb.putstr(10, 84 + 29, '<', 0, 4)
        self.pRender.fb.putstr(480 - 34, 84 + 29, '>', 0, 4)

        ######################

        c = self.pRender.ConvRgb(0.16, 1, 0.6)
        #self.pRender.fb.draw.rect(c, Rect(1, 240 - 54, self.pRender.xres-2, 1), 0)
        self.pRender.fb.putstr(5, 240 - 21, "00:00", self.pRender.W, 1)

        self.UpdateSeekTime()

        self.pRender.fb.draw.rect(c, Rect(1, 240 - 12, self.pRender.xres - 2,
                                          1), 0)
        self.pRender.fb.draw.rect(c, Rect(1, 240 + 18, self.pRender.xres - 2,
                                          1), 0)

        #self.RenderFootBt(0, " Auto", 0.16)
        self.RenderFootBt(1, " Stop", 0.36)
        self.RenderFootBt(2, " Play", 0.36)
        self.RenderFootBt(3, "Pause", 0.16)
        self.RenderFootBt(4, "Repeat", 0.16)

        self.RenderDotAll()

        self.RenderBackBt(True)

        self.RenderCurrentInfo("STOP", 0)
        self.pRender.fb.putstr(12 + 54, 268 + 24 + 6, "msec", self.pRender.W,
                               1)

        self.pWanem.InitSingle()

    def RenderCurrentInfo(self, state="", delay=-1):
        if state != "":
            self.pRender.fb.draw.rect(self.pRender.N, Rect(12, 268, 84, 16), 0)
            self.pRender.fb.putstr(12, 268, state, self.pRender.W, 2)
        if delay >= 0:
            self.pRender.fb.draw.rect(self.pRender.N,
                                      Rect(12, 268 + 24, 50, 16), 0)
            self.pRender.fb.putstr(12, 268 + 24, "%04d" % delay,
                                   self.pRender.W, 2)

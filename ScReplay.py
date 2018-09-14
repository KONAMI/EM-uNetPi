import sys, getopt, struct, time, termios, fcntl, sys, os, colorsys, threading, time, datetime, subprocess, os.path, math
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/fbtft')
from RenderManager import RenderManager
from WanemManager import WanemManager
from ScBase import ScBase
from gfx import Rect
from DataAsset import CTX


class ScReplay(ScBase):
    def __init__(self, pCTX, pRender, pWanem):
        super(ScReplay, self).__init__(pCTX, pRender, pWanem)
        self.ptDef.insert(
            0, self.CreateTocuhDef("BtMenu", 468, 29, 62, 42, self.BtHandler))

        self.ptDef.insert(
            1,
            self.CreateTocuhDef("BtGroupPrev", 470, 264, 80, 50,
                                self.BtHandler))
        self.ptDef.insert(
            2,
            self.CreateTocuhDef("BtGroupNext", 388, 264, 80, 50,
                                self.BtHandler))
        self.ptDef.insert(
            3,
            self.CreateTocuhDef("BtCatPrev", 296, 264, 80, 50, self.BtHandler))
        self.ptDef.insert(
            4,
            self.CreateTocuhDef("BtCatNext", 214, 264, 80, 50, self.BtHandler))
        self.ptDef.insert(
            5, self.CreateTocuhDef("BtSelect", 110, 264, 80, 50,
                                   self.BtHandler))

    def BtHandler(self, key):
        print "BtHandler" + key
        if key == "BtMenu":
            self.nextScene = "Menu"
            self.state = self.STATE_TERM
        elif key == "BtGroupPrev":
            self.UpdateGroup(-1)
        elif key == "BtGroupNext":
            self.UpdateGroup(1)
        elif key == "BtCatPrev":
            self.UpdateCategory(-1)
        elif key == "BtCatNext":
            self.UpdateCategory(1)
        elif key == "BtSelect":
            if self.datNr > 0:
                self.nextScene = "Playback"
                self.state = self.STATE_TERM

    def UpdateGroup(self, vec, forceClear=False):

        prevPageIdx = self.groupPageIdx
        prevFocusIdx = self.groupFocusIdx
        isPageSwitch = forceClear

        if (self.groupPageIdx * 5 + self.groupFocusIdx) == 0 and vec == -1:
            return
        if (self.groupPageIdx * 5 + self.groupFocusIdx) == (
                self.groupNr - 1) and vec == 1:
            return
        if (self.groupFocusIdx % 5) == 0 and vec == -1:
            self.groupPageIdx -= 1
            isPageSwitch = True
        elif (self.groupFocusIdx % 5) == 4 and vec == 1:
            self.groupPageIdx += 1
            isPageSwitch = True

        self.groupFocusIdx = (self.groupFocusIdx + vec) % 5

        if isPageSwitch:
            # Clear
            c = self.pRender.ConvRgb(0, 0, 0)
            self.pRender.fb.draw.rect(c, Rect(1, 92, 176, 30 * 5 + 14), 0)

            # Render Focus
            c = self.pRender.ConvRgb(1.00, 0.8, 0.4)
            self.pRender.fb.draw.rect(
                c, Rect(1, 92 + 30 * self.groupFocusIdx, 176, 30), 0)

            # Render List
            # currentIdx = self.groupPageIdx * 5 + self.groupFocusIdx
            currentIdxTop = self.groupPageIdx * 5
            focusIdx = 0
            for file in self.groupList[currentIdxTop:currentIdxTop + 5]:
                self.pRender.fb.putstr(12, 100 + 30 * focusIdx,
                                       "> %s" % file[0:8], self.pRender.W, 2)
                focusIdx += 1

            # Render Pager
            self.pRender.fb.putstr(
                12 + 58, 100 + 30 * 5 - 3,
                " %d / %d" % (self.groupPageIdx + 1,
                              math.ceil(self.groupNr / 5.0)), self.pRender.W,
                1)
        else:
            # Clear
            c = self.pRender.ConvRgb(0, 0, 0)
            self.pRender.fb.draw.rect(c,
                                      Rect(1, 92 + 30 * prevFocusIdx, 176, 30),
                                      0)
            #self.pRender.fb.draw.rect(c, Rect(1, 92 + 30 * self.groupFocusIdx, 176, 30), 0)

            # Render Focus
            c = self.pRender.ConvRgb(1.00, 0.8, 0.4)
            self.pRender.fb.draw.rect(
                c, Rect(1, 92 + 30 * self.groupFocusIdx, 176, 30), 0)

            # Render Prev
            idx = prevPageIdx * 5 + prevFocusIdx
            file = self.groupList[idx]
            self.pRender.fb.putstr(12, 100 + 30 * (prevFocusIdx % 5),
                                   "> %s" % file[0:8], self.pRender.W, 2)

            # Render Current
            idx = self.groupPageIdx * 5 + self.groupFocusIdx
            file = self.groupList[idx]
            self.pRender.fb.putstr(12, 100 + 30 * (self.groupFocusIdx % 5),
                                   "> %s" % file[0:8], self.pRender.W, 2)

        self.LoadCategory()
        self.UpdateCategory(0, True)

    def LoadCategory(self):
        print "LoadCategory"
        gidx = self.groupPageIdx * 5 + self.groupFocusIdx
        self.catList = os.listdir(self.pCTX.replayDataPath + "/" +
                                  self.groupList[gidx])
        #self.catList.sort()
        self.catPageIdx = 0
        self.catNr = len(self.catList)
        self.catFocusIdx = 0

    def UpdateCategory(self, vec, forceClear=False):

        prevPageIdx = self.catPageIdx
        prevFocusIdx = self.catFocusIdx
        isPageSwitch = forceClear

        if (self.catPageIdx * 5 + self.catFocusIdx) == 0 and vec == -1:
            return
        if (self.catPageIdx * 5 + self.catFocusIdx) == (
                self.catNr - 1) and vec == 1:
            return
        if (self.catFocusIdx % 5) == 0 and vec == -1:
            self.catPageIdx -= 1
            isPageSwitch = True
        elif (self.catFocusIdx % 5) == 4 and vec == 1:
            self.catPageIdx += 1
            isPageSwitch = True

        self.catFocusIdx = (self.catFocusIdx + vec) % 5

        if isPageSwitch:
            # Clear
            c = self.pRender.ConvRgb(0, 0, 0)
            self.pRender.fb.draw.rect(c, Rect(191, 92, 176, 30 * 5 + 14), 0)

            # Render Focus
            c = self.pRender.ConvRgb(1.00, 0.8, 0.4)
            self.pRender.fb.draw.rect(
                c, Rect(191, 92 + 30 * self.catFocusIdx, 176, 30), 0)

            # Render List
            #currentIdx = self.catPageIdx * 5 + self.catFocusIdx
            currentIdxTop = self.catPageIdx * 5
            focusIdx = 0
            currentIdxTopTerm = currentIdxTop + 5

            if currentIdxTopTerm > self.catNr:
                currentIdxTopTerm = self.catNr
            for file in self.catList[currentIdxTop:currentIdxTopTerm]:
                self.pRender.fb.putstr(202, 100 + 30 * focusIdx,
                                       "> %s" % file[0:8], self.pRender.W, 2)
                focusIdx += 1

            # Render Pager
            self.pRender.fb.putstr(
                260, 100 + 30 * 5 - 3,
                " %d / %d" % (self.catPageIdx + 1, math.ceil(
                    self.catNr / 5.0)), self.pRender.W, 1)
        else:

            # Clear
            c = self.pRender.ConvRgb(0, 0, 0)
            self.pRender.fb.draw.rect(
                c, Rect(191, 92 + 30 * prevFocusIdx, 176, 30), 0)
            #self.pRender.fb.draw.rect(c, Rect(191, 92 + 30 * self.catFocusIdx, 176, 30), 0)

            # Render Focus
            c = self.pRender.ConvRgb(1.00, 0.8, 0.4)
            self.pRender.fb.draw.rect(
                c, Rect(191, 92 + 30 * self.catFocusIdx, 176, 30), 0)

            # Render Prev
            idx = prevPageIdx * 5 + prevFocusIdx
            file = self.catList[idx]
            self.pRender.fb.putstr(202, 100 + 30 * (prevFocusIdx % 5),
                                   "> %s" % file[0:8], self.pRender.W, 2)

            # Render Current
            idx = self.catPageIdx * 5 + self.catFocusIdx
            file = self.catList[idx]
            self.pRender.fb.putstr(202, 100 + 30 * (self.catFocusIdx % 5),
                                   "> %s" % file[0:8], self.pRender.W, 2)

        self.UpdateInfo(True)

    def UpdateInfo(self, forceClear=False):

        gidx = self.groupPageIdx * 5 + self.groupFocusIdx
        self.catList = os.listdir(self.pCTX.replayDataPath + "/" +
                                  self.groupList[gidx])
        cidx = self.catPageIdx * 5 + self.catFocusIdx

        targetPath = self.pCTX.replayDataPath + "/" + self.groupList[
            gidx] + "/" + self.catList[cidx]

        datList = os.listdir(targetPath)
        self.datNr = len(datList)
        mtime = os.path.getmtime(targetPath)
        t = datetime.datetime.fromtimestamp(mtime)
        datMtime = t.strftime("%Y/%m/%d")

        if forceClear:
            self.pRender.fb.putstr(388, 100 + 30 * 0, "* Data Nr",
                                   self.pRender.W, 1)
            self.pRender.fb.putstr(388, 100 + 30 * 2 - 10, "* Last Update",
                                   self.pRender.W, 1)

        # Clear
        c = self.pRender.ConvRgb(0, 0, 0)
        self.pRender.fb.draw.rect(c, Rect(388, 100 + 30 * 1 - 10, 90, 30), 0)
        self.pRender.fb.draw.rect(c, Rect(388, 100 + 30 * 3 - 20, 90, 30), 0)

        self.pRender.fb.putstr(388, 100 + 30 * 1 - 10, "%13d" % self.datNr,
                               self.pRender.W, 1)
        self.pRender.fb.putstr(388, 100 + 30 * 3 - 20, "%13s" % datMtime,
                               self.pRender.W, 1)

        print targetPath
        self.pCTX.currentReplayData = targetPath

    def Start(self):
        super(ScReplay, self).Start()

        ##[ Get DataDir Info ]######################################################

        self.datNr = 0

        self.groupList = os.listdir(self.pCTX.replayDataPath)
        self.groupList.sort()
        self.groupPageIdx = 0
        self.groupNr = len(self.groupList)
        self.groupFocusIdx = 0
        self.LoadCategory()

        #print str(len(files))
        #for file in files[10:15]:
        #	print file

        ##[ RENDER ]################################################################

        self.pRender.UpdateTitle("WAN Emulation - Replay")
        self.pRender.UpdateSubTitle("Please select group and category")

        c = yellow = self.pRender.fb.rgb(255, 255, 0)
        self.pRender.fb.draw.rect(c, Rect(0, 54, self.pRender.xres, 1), 0)
        self.pRender.fb.draw.rect(c, Rect(0, 74, self.pRender.xres, 1), 0)
        self.pRender.fb.draw.rect(c, Rect(0, 54, 10 + 60, 20), 0)
        self.pRender.fb.draw.rect(c, Rect(480 - 10, 54, 10, 20), 0)
        self.pRender.fb.putstr(26, 54 + 7, ">>>", self.pRender.N, 1)

        c = self.pRender.ConvRgb(0.16, 0.4, 0.2)
        self.pRender.fb.draw.rect(c, Rect(1, 75, 478, 16), 0)
        thlabel = "group                         category                   info"
        self.pRender.fb.putstr(74, 79, thlabel, self.pRender.W, 1)
        c = self.pRender.ConvRgb(0.16, 1, 0.6)
        self.pRender.fb.draw.rect(c, Rect(178, 75, 12, 320 - 76), 0)
        self.pRender.fb.draw.rect(c, Rect(368, 75, 12, 320 - 76), 0)
        self.pRender.fb.putstr(178, 160, ">", self.pRender.N, 2)
        self.pRender.fb.putstr(368, 160, ">", self.pRender.N, 2)

        c = self.pRender.ConvRgb(0.16, 1, 0.6)
        self.pRender.fb.draw.rect(c, Rect(1, 240 + 18, self.pRender.xres - 2,
                                          1), 0)

        self.RenderFootBt(0, "  Up", 0.36)
        self.RenderFootBt(1, " Down", 0.36)
        self.RenderFootBt(2, "  Up", 0.36)
        self.RenderFootBt(3, " Down", 0.36)
        self.RenderFootBt(4, "Select", 0.56)

        self.UpdateGroup(0, True)
        self.RenderBackBt(True)

    def RenderFootBt(self, idx, label, h):
        if idx == 0:
            x = 10 - 1
        elif idx == 1:
            x = 10 + 80 + 1
        elif idx == 2:
            x = 198
        elif idx == 3:
            x = 198 + 80 + 2
        elif idx == 4:
            x = 389

        c = self.pRender.ConvRgb(h, 0.6, 0.6)
        self.pRender.fb.draw.rect(c, Rect(x, 264, 80, 44), 0)
        c = self.pRender.ConvRgb(h, 0.6, 0.2)
        self.pRender.fb.draw.rect(c, Rect(x, 264 + 44, 80, 6), 0)
        self.pRender.fb.putstr(x + 4, 278, label, c, 2)

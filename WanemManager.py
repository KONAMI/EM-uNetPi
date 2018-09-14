import sys, getopt, time, struct, termios, fcntl, sys, os, subprocess
from time import sleep
from RenderManager import RenderManager


class WanemManager:
    def __init__(self, pCTX, pRenderManager):
        self.pCTX = pCTX
        self.pRender = pRenderManager
        self.disconnState = 0
        self.speedState = 0
        self.delayState = 0
        self.speedPrevState = 0
        self.delayPrevState = 0
        self.isDualMode = 0
        self.speedLabel = ["nolimit", "8Mbps", "1Mbps", "200Kbps", "128Kbps"]
        self.delayLabel = ["nolimit", "LTE", "LTE(Jitter)", "3G", "3G(Jitter)"]
        self.speedValue = [
            "", "limit 1Mb buffer 2Mb rate 1Mbps",
            "limit 128Kb buffer 256Kb rate 128Kbps",
            "limit 25Kb buffer 50Kb rate 25Kbps",
            "limit 16Kb buffer 32Kb rate 16Kbps"
        ]
        self.delayValue = [
            "0msec", "25msec", "50msec 30msec", "100msec", "250msec 100msec"
        ]
        self.lossValueDef = [0, 1, 2, 1, 2]
        self.lossValue = ["0%", "100%", "100%"]
        self.InitSingle()
        self.upRootDevice = ""
        self.dwRootDevice = ""
        self.upChildDevice = ""
        self.dwChildDevice = ""

        cmd = "cat /etc/wanem/wanemmode.prop"
        try:
            self.wanemMode = int(
                subprocess.check_output(cmd.strip().split(" ")).replace(
                    '\n', ''))
        except subprocess.CalledProcessError:
            self.wanemMode = 0

    def InitSingle(self):
        self.isDualMode = 0
        self.upRootDevice = "eth0 root"
        self.dwRootDevice = "wlan0 root"
        self.dw2RootDevice = "eth2 root"

        cmd = "tc qdisc del dev " + self.upRootDevice
        subprocess.call(cmd.strip().split(" "))
        cmd = "tc qdisc add dev " + self.upRootDevice + " netem delay " + self.delayValue[
            self.delayState] + " loss " + self.lossValue[self.disconnState]
        subprocess.call(cmd.strip().split(" "))

        cmd = "tc qdisc del dev " + self.dwRootDevice
        subprocess.call(cmd.strip().split(" "))
        cmd = "tc qdisc add dev " + self.dwRootDevice + " netem delay " + self.delayValue[
            self.delayState] + " loss " + self.lossValue[self.disconnState]
        subprocess.call(cmd.strip().split(" "))

        if self.pCTX.lanMode == self.pCTX.LAN_MODE_HYBRID:
            cmd = "tc qdisc del dev " + self.dw2RootDevice
            subprocess.call(cmd.strip().split(" "))
            cmd = "tc qdisc add dev " + self.dw2RootDevice + " netem delay " + self.delayValue[
                self.delayState] + " loss " + self.lossValue[self.disconnState]
            subprocess.call(cmd.strip().split(" "))

    def InitDual(self, bandValueIdx):

        #print "InitDual >> " + str(bandValueIdx)
        #print self.speedValue[bandValueIdx]

        self.isDualMode = 1
        self.upRootDevice = "eth0 root"
        self.dwRootDevice = "wlan0 root"
        self.dw2RootDevice = "eth2 root"
        cmd = "tc qdisc del dev " + self.upRootDevice
        subprocess.call(cmd.strip().split(" "))
        cmd = "tc qdisc del dev " + self.dwRootDevice
        subprocess.call(cmd.strip().split(" "))
        if self.pCTX.lanMode == self.pCTX.LAN_MODE_HYBRID:
            cmd = "tc qdisc del dev " + self.dw2RootDevice
            subprocess.call(cmd.strip().split(" "))

        self.upRootDevice = "eth0 root handle 1:"
        self.dwRootDevice = "wlan0 root handle 2:"
        self.dw2RootDevice = "eth2 root handle 3:"
        self.upChildDevice = "eth0 parent 1: handle 10:"
        self.dwChildDevice = "wlan0 parent 2: handle 20:"
        self.dw2ChildDevice = "eth2 parent 3: handle 30:"
        cmd = "tc qdisc add dev " + self.upRootDevice + " tbf " + self.speedValue[
            bandValueIdx]
        subprocess.call(cmd.strip().split(" "))
        cmd = "tc qdisc add dev " + self.upChildDevice + " netem delay " + self.delayValue[
            self.delayState] + " loss " + self.lossValue[self.disconnState]
        subprocess.call(cmd.strip().split(" "))

        cmd = "tc qdisc add dev " + self.dwRootDevice + " tbf " + self.speedValue[
            bandValueIdx]
        subprocess.call(cmd.strip().split(" "))
        cmd = "tc qdisc add dev " + self.dwChildDevice + " netem delay " + self.delayValue[
            self.delayState] + " loss " + self.lossValue[self.disconnState]
        subprocess.call(cmd.strip().split(" "))
        if self.pCTX.lanMode == self.pCTX.LAN_MODE_HYBRID:
            cmd = "tc qdisc add dev " + self.dw2RootDevice + " tbf " + self.speedValue[
                bandValueIdx]
            subprocess.call(cmd.strip().split(" "))
            cmd = "tc qdisc add dev " + self.dw2ChildDevice + " netem delay " + self.delayValue[
                self.delayState] + " loss " + self.lossValue[self.disconnState]
            subprocess.call(cmd.strip().split(" "))

    def EmuDisconnPush(self):
        print "Push"
        self.disconnState = 2
        self.pRender.RenderDot(0, 6)
        self.Apply(False)

    def EmuDisconnRelease(self):
        if self.disconnState != 2:
            return
        print "Release"
        self.pRender.RenderDot(0, 5)
        self.disconnState = 0
        self.Apply(False)

    def EmuDisconnToggle(self):
        if self.disconnState == 1:
            self.disconnState = 0
            self.pRender.RenderDot(0, 5)
        elif self.disconnState == 0:
            self.disconnState = 1
            self.pRender.RenderDot(0, 6)
        self.Apply(False)

    # Call by Only ScManualEx2
    def EmuDisconnPushMini(self, upBand, dwBand, upDelay, dwDelay, upLoss,
                           dwLoss):
        print "Push"
        self.disconnState = 2
        self.pRender.RenderDotMini(2, 6)
        self.DirectUpdateEx2(upBand, dwBand, upDelay, dwDelay, upLoss, dwLoss)

    # Call by Only ScManualEx2
    def EmuDisconnReleaseMini(self, upBand, dwBand, upDelay, dwDelay, upLoss,
                              dwLoss):
        if self.disconnState != 2:
            return
        print "Release"
        self.pRender.RenderDotMini(2, 5)
        self.disconnState = 0
        self.DirectUpdateEx2(upBand, dwBand, upDelay, dwDelay, upLoss, dwLoss)

    # Call by Only ScManualEx2
    def EmuDisconnToggleMini(self, upBand, dwBand, upDelay, dwDelay, upLoss,
                             dwLoss):
        if self.disconnState == 1:
            self.disconnState = 0
            self.pRender.RenderDotMini(2, 5)
        elif self.disconnState == 0:
            self.disconnState = 1
            self.pRender.RenderDotMini(2, 6)
        self.DirectUpdateEx2(upBand, dwBand, upDelay, dwDelay, upLoss, dwLoss)

    def EmuSpeedChange(self, value):
        self.speedPrevState = self.speedState
        self.speedState = (self.speedState + value + 5) % 5
        self.pRender.RenderDot(1, 7 + self.speedState)

        if self.speedState == 0 and self.speedPrevState != 0:
            self.InitSingle()
        elif self.speedState != 0 and self.speedPrevState == 0:
            self.InitDual(self.speedState)

        self.Apply(True)

    def EmuDelayChange(self, value):
        self.delayState = (self.delayState + value + 5) % 5
        self.pRender.RenderDot(2, 7 + self.delayState)
        self.Apply()

    def Clear(self):
        self.speedState = 0
        self.delayState = 0
        self.disconnState = 0
        self.Apply(True)

    def Apply(self, isLabelUpdate=True):
        if isLabelUpdate == True:
            #self.pRender.UpdateTitle("Wan Emulation Mode")
            self.pRender.UpdateSubTitle(
                "speed:" + self.speedLabel[self.speedState] + ", delay:" +
                self.delayLabel[self.delayState])

        if self.disconnState == 0:
            upLossStmt = " loss %d%%" % self.lossValueDef[self.delayState]
            dwLossStmt = " loss %d%%" % self.lossValueDef[self.delayState]
        else:
            upLossStmt = " loss " + self.lossValue[self.disconnState]
            dwLossStmt = " loss " + self.lossValue[self.disconnState]

        if self.isDualMode == 0:
            cmd = "tc qdisc change dev " + self.upRootDevice + " netem delay " + self.delayValue[
                self.delayState] + upLossStmt
            cmd2 = "tc qdisc change dev " + self.dwRootDevice + " netem delay " + self.delayValue[
                self.delayState] + dwLossStmt
            cmd3 = "tc qdisc change dev " + self.dw2RootDevice + " netem delay " + self.delayValue[
                self.delayState] + dwLossStmt

            subprocess.call(cmd.strip().split(" "))
            subprocess.call(cmd2.strip().split(" "))
            if self.pCTX.lanMode == self.pCTX.LAN_MODE_HYBRID:
                subprocess.call(cmd3.strip().split(" "))

        else:
            #print str(self.speedState) + " >> " + self.speedValue[self.speedState]
            cmd = "tc qdisc change dev " + self.upRootDevice + " tbf " + self.speedValue[
                self.speedState]
            cmd2 = "tc qdisc change dev " + self.upChildDevice + " netem delay " + self.delayValue[
                self.delayState] + upLossStmt
            cmd3 = "tc qdisc change dev " + self.dwRootDevice + " tbf " + self.speedValue[
                self.speedState]
            cmd4 = "tc qdisc change dev " + self.dwChildDevice + " netem delay " + self.delayValue[
                self.delayState] + dwLossStmt
            cmd5 = "tc qdisc change dev " + self.dw2RootDevice + " tbf " + self.speedValue[
                self.speedState]
            cmd6 = "tc qdisc change dev " + self.dw2ChildDevice + " netem delay " + self.delayValue[
                self.delayState] + dwLossStmt

            subprocess.call(cmd.strip().split(" "))
            subprocess.call(cmd2.strip().split(" "))
            subprocess.call(cmd3.strip().split(" "))
            subprocess.call(cmd4.strip().split(" "))
            if self.pCTX.lanMode == self.pCTX.LAN_MODE_HYBRID:
                subprocess.call(cmd5.strip().split(" "))
                subprocess.call(cmd6.strip().split(" "))

    def DirectApply(self, delay):
        if delay >= 0:
            param = str(int(delay / 2))
            cmd = "tc qdisc change dev eth0 root netem delay " + param + "msec loss 0%"
            cmd2 = "tc qdisc change dev wlan0 root netem delay " + param + "msec loss 0%"
            cmd3 = "tc qdisc change dev eth2 root netem delay " + param + "msec loss 0%"

            subprocess.call(cmd.strip().split(" "))
            subprocess.call(cmd2.strip().split(" "))
            subprocess.call(cmd3.strip().split(" "))
        else:
            cmd = "tc qdisc change dev eth0 root netem loss 100%"
            cmd2 = "tc qdisc change dev wlan0 root netem loss 100%"
            cmd3 = "tc qdisc change dev eth2 root netem loss 100%"

            subprocess.call(cmd.strip().split(" "))
            subprocess.call(cmd2.strip().split(" "))
            subprocess.call(cmd3.strip().split(" "))

    def ClearEx(self):
        self.upRootDevice = "eth0 root"
        self.dwRootDevice = "wlan0 root"
        self.dw2RootDevice = "eth2 root"
        cmd = "tc qdisc del dev " + self.upRootDevice
        subprocess.call(cmd.strip().split(" "))
        cmd = "tc qdisc del dev " + self.dwRootDevice
        subprocess.call(cmd.strip().split(" "))
        if self.pCTX.lanMode == self.pCTX.LAN_MODE_HYBRID:
            cmd = "tc qdisc del dev " + self.dw2RootDevice
            subprocess.call(cmd.strip().split(" "))

        self.pRender.RenderDotMini(2, 5)
        self.disconnState = 0
        return

    def ClearEx2(self):
        self.upRootDevice = "eth0 root"
        self.dwRootDevice = "wlan0 root"
        self.dw2RootDevice = "eth2 root"
        cmd = "tc qdisc del dev " + self.upRootDevice
        subprocess.call(cmd.strip().split(" "))
        cmd = "tc qdisc del dev " + self.dwRootDevice
        subprocess.call(cmd.strip().split(" "))
        if self.pCTX.lanMode == self.pCTX.LAN_MODE_HYBRID:
            cmd = "tc qdisc del dev " + self.dw2RootDevice
            subprocess.call(cmd.strip().split(" "))

        self.disconnState = 0
        return

    def DirectApplyEx(self,
                      upBand,
                      dwBand,
                      upDelay,
                      dwDelay,
                      upLoss=0,
                      dwLoss=0):

        if self.wanemMode == 0:
            speedUpValue = "limit %dKb buffer %dKb rate %dKbps" % (4, 8,
                                                                   upBand / 8)
            speedDwValue = "limit %dKb buffer %dKb rate %dKbps" % (4, 8,
                                                                   dwBand / 8)
        else:
            speedUpValue = "limit %dKb buffer %dKb rate %dKbps" % (
                upBand / 8, upBand / 4, upBand / 8)
            speedDwValue = "limit %dKb buffer %dKb rate %dKbps" % (
                dwBand / 8, dwBand / 4, dwBand / 8)

        delayUpValue = "%dmsec" % upDelay
        delayDwValue = "%dmsec" % dwDelay

        self.upRootDevice = "eth0 root handle 1:"
        self.dwRootDevice = "wlan0 root handle 2:"
        self.dw2RootDevice = "eth2 root handle 3:"
        self.upChildDevice = "eth0 parent 1: handle 10:"
        self.dwChildDevice = "wlan0 parent 2: handle 20:"
        self.dw2ChildDevice = "eth2 parent 3: handle 30:"

        if self.disconnState == 0:
            upLossStmt = " loss %d%%" % upLoss
            dwLossStmt = " loss %d%%" % dwLoss
        else:
            upLossStmt = " loss " + self.lossValue[self.disconnState]
            dwLossStmt = " loss " + self.lossValue[self.disconnState]

        cmd = "tc qdisc add dev " + self.upRootDevice + " tbf " + speedUpValue
        subprocess.call(cmd.strip().split(" "))
        cmd = "tc qdisc add dev " + self.upChildDevice + " netem delay " + delayUpValue + upLossStmt
        subprocess.call(cmd.strip().split(" "))

        cmd = "tc qdisc add dev " + self.dwRootDevice + " tbf " + speedDwValue
        subprocess.call(cmd.strip().split(" "))
        cmd = "tc qdisc add dev " + self.dwChildDevice + " netem delay " + delayDwValue + dwLossStmt
        subprocess.call(cmd.strip().split(" "))

        if self.pCTX.lanMode == self.pCTX.LAN_MODE_HYBRID:
            cmd = "tc qdisc add dev " + self.dw2RootDevice + " tbf " + speedDwValue
            subprocess.call(cmd.strip().split(" "))
            cmd = "tc qdisc add dev " + self.dw2ChildDevice + " netem delay " + delayDwValue + dwLossStmt
            subprocess.call(cmd.strip().split(" "))

    def DirectApplyEx2(self, upBand, dwBand, upDelay, dwDelay, upLoss, dwLoss):

        if self.wanemMode == 0:
            speedUpValue = "limit %dKb buffer %dKb rate %dKbps" % (4, 8,
                                                                   upBand / 8)
            speedDwValue = "limit %dKb buffer %dKb rate %dKbps" % (4, 8,
                                                                   dwBand / 8)
        else:
            speedUpValue = "limit %dKb buffer %dKb rate %dKbps" % (
                upBand / 8, upBand / 4, upBand / 8)
            speedDwValue = "limit %dKb buffer %dKb rate %dKbps" % (
                dwBand / 8, dwBand / 4, dwBand / 8)

        delayUpValue = "%dmsec" % upDelay
        delayDwValue = "%dmsec" % dwDelay

        self.upRootDevice = "eth0 root handle 1:"
        self.dwRootDevice = "wlan0 root handle 2:"
        self.dw2RootDevice = "eth2 root handle 3:"
        self.upChildDevice = "eth0 parent 1: handle 10:"
        self.dwChildDevice = "wlan0 parent 2: handle 20:"
        self.dw2ChildDevice = "eth2 parent 3: handle 30:"
        cmd = "tc qdisc add dev " + self.upRootDevice + " tbf " + speedUpValue
        subprocess.call(cmd.strip().split(" "))
        cmd = "tc qdisc add dev " + self.upChildDevice + " netem delay " + delayUpValue + " loss " + str(
            upLoss) + "%"
        subprocess.call(cmd.strip().split(" "))

        cmd = "tc qdisc add dev " + self.dwRootDevice + " tbf " + speedDwValue
        subprocess.call(cmd.strip().split(" "))
        cmd = "tc qdisc add dev " + self.dwChildDevice + " netem delay " + delayDwValue + " loss " + str(
            dwLoss) + "%"
        subprocess.call(cmd.strip().split(" "))

        if self.pCTX.lanMode == self.pCTX.LAN_MODE_HYBRID:
            cmd = "tc qdisc add dev " + self.dw2RootDevice + " tbf " + speedDwValue
            subprocess.call(cmd.strip().split(" "))
            cmd = "tc qdisc add dev " + self.dw2ChildDevice + " netem delay " + delayDwValue + " loss " + str(
                dwLoss) + "%"
            subprocess.call(cmd.strip().split(" "))

    def DirectUpdateEx(self, upBand, dwBand, upDelay, dwDelay):

        if self.wanemMode == 0:
            speedUpValue = "limit %dKb buffer %dKb rate %dKbps" % (4, 8,
                                                                   upBand / 8)
            speedDwValue = "limit %dKb buffer %dKb rate %dKbps" % (4, 8,
                                                                   dwBand / 8)
        else:
            speedUpValue = "limit %dKb buffer %dKb rate %dKbps" % (
                upBand / 8, upBand / 4, upBand / 8)
            speedDwValue = "limit %dKb buffer %dKb rate %dKbps" % (
                dwBand / 8, dwBand / 4, dwBand / 8)

        delayUpValue = "%dmsec" % upDelay
        delayDwValue = "%dmsec" % dwDelay

        self.upRootDevice = "eth0 root handle 1:"
        self.dwRootDevice = "wlan0 root handle 2:"
        self.dw2RootDevice = "eth2 root handle 3:"
        self.upChildDevice = "eth0 parent 1: handle 10:"
        self.dwChildDevice = "wlan0 parent 2: handle 20:"
        self.dw2ChildDevice = "eth2 parent 3: handle 30:"
        cmd = "tc qdisc change dev " + self.upRootDevice + " tbf " + speedUpValue
        subprocess.call(cmd.strip().split(" "))
        cmd = "tc qdisc change dev " + self.upChildDevice + " netem delay " + delayUpValue + " loss " + self.lossValue[
            self.disconnState]
        subprocess.call(cmd.strip().split(" "))

        cmd = "tc qdisc change dev " + self.dwRootDevice + " tbf " + speedDwValue
        subprocess.call(cmd.strip().split(" "))
        cmd = "tc qdisc change dev " + self.dwChildDevice + " netem delay " + delayDwValue + " loss " + self.lossValue[
            self.disconnState]
        subprocess.call(cmd.strip().split(" "))

        if self.pCTX.lanMode == self.pCTX.LAN_MODE_HYBRID:
            cmd = "tc qdisc change dev " + self.dw2RootDevice + " tbf " + speedDwValue
            subprocess.call(cmd.strip().split(" "))
            cmd = "tc qdisc change dev " + self.dw2ChildDevice + " netem delay " + delayDwValue + " loss " + self.lossValue[
                self.disconnState]
            subprocess.call(cmd.strip().split(" "))

    def DirectUpdateEx2(self,
                        upBand,
                        dwBand,
                        upDelay,
                        dwDelay,
                        upLoss=0,
                        dwLoss=0):

        if self.wanemMode == 0:
            speedUpValue = "limit %dKb buffer %dKb rate %dKbps" % (4, 8,
                                                                   upBand / 8)
            speedDwValue = "limit %dKb buffer %dKb rate %dKbps" % (4, 8,
                                                                   dwBand / 8)
        else:
            speedUpValue = "limit %dKb buffer %dKb rate %dKbps" % (
                upBand / 8, upBand / 4, upBand / 8)
            speedDwValue = "limit %dKb buffer %dKb rate %dKbps" % (
                dwBand / 8, dwBand / 4, dwBand / 8)

        delayUpValue = "%dmsec" % upDelay
        delayDwValue = "%dmsec" % dwDelay

        self.upRootDevice = "eth0 root handle 1:"
        self.dwRootDevice = "wlan0 root handle 2:"
        self.dw2RootDevice = "eth2 root handle 3:"
        self.upChildDevice = "eth0 parent 1: handle 10:"
        self.dwChildDevice = "wlan0 parent 2: handle 20:"
        self.dw2ChildDevice = "eth2 parent 3: handle 30:"

        if self.disconnState == 0:
            upLossStmt = " loss %d%%" % upLoss
            dwLossStmt = " loss %d%%" % dwLoss
        else:
            upLossStmt = " loss " + self.lossValue[self.disconnState]
            dwLossStmt = " loss " + self.lossValue[self.disconnState]

        cmd = "tc qdisc change dev " + self.upRootDevice + " tbf " + speedUpValue
        subprocess.call(cmd.strip().split(" "))
        cmd = "tc qdisc change dev " + self.upChildDevice + " netem delay " + delayUpValue + upLossStmt
        subprocess.call(cmd.strip().split(" "))

        cmd = "tc qdisc change dev " + self.dwRootDevice + " tbf " + speedDwValue
        subprocess.call(cmd.strip().split(" "))
        cmd = "tc qdisc change dev " + self.dwChildDevice + " netem delay " + delayDwValue + dwLossStmt
        subprocess.call(cmd.strip().split(" "))

        if self.pCTX.lanMode == self.pCTX.LAN_MODE_HYBRID:
            cmd = "tc qdisc change dev " + self.dw2RootDevice + " tbf " + speedDwValue
            subprocess.call(cmd.strip().split(" "))
            cmd = "tc qdisc change dev " + self.dw2ChildDevice + " netem delay " + delayDwValue + dwLossStmt
            subprocess.call(cmd.strip().split(" "))

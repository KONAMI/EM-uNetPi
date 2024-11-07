import sys, getopt, struct, time, termios, fcntl, sys, os, colorsys, threading, time, datetime, subprocess, socket, errno
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/fbtft')
from RenderManager import RenderManager
from WanemManager import WanemManager
from ScBase import ScBase
from gfx import Rect
from DataAsset import CTX
from LogReporter import LogReporter
from fcntl import ioctl
from V6Util import V6Util

class ScSetting(ScBase):
    def __init__(self, pCTX, pRender, pWanem):
        super(ScSetting, self).__init__(pCTX, pRender, pWanem)

        self.naptModeLabels = ["  Default  ", " Symmetric "]
        self.apModeLabelsT = ["  11g ", "  11a "]
        self.apModeLabelsB = ["2.4GHz", " 5GHz "]
        self.apChannelLabelsG = ["  01  ", "  06  ", "  11  "]
        self.apChannelLabelsA = ["  36  ", "  40  ", "  44  ", "  48  "]
        self.wanemModeLabels = ["  Policing  ", "  Shaping  "]
        self.v6ModeLabels = ["   Disable   ", "     NAT     ", "NAT/Symmetric"]

        self.ptDef.append(
            self.CreateTocuhDef("BtMenu", 468, 29, 62, 42, self.BtHandler))
        self.ptDef.append(
            self.CreateTocuhDef("BtTab0", 466, 96 + 45 * 0, 84, 42,
                                self.BtHandler))
        self.ptDef.append(
            self.CreateTocuhDef("BtTab1", 466, 96 + 45 * 1, 84, 42,
                                self.BtHandler))
        self.ptDef.append(
            self.CreateTocuhDef("BtTab2", 466, 96 + 45 * 2, 84, 42,
                                self.BtHandler))
        self.ptDef.append(
            self.CreateTocuhDef("BtTab3", 466, 96 + 45 * 3, 84, 42,
                                self.BtHandler))
        self.ptDef.append(
            self.CreateTocuhDef("BtTab4", 466, 96 + 45 * 4, 80, 42,
                                self.BtHandler))
        self.ptDef.append(
            self.CreateTocuhDef("BtV6L", 366, 135, 80, 48, self.BtHandler,
                                None, False))
        self.ptDef.append(
            self.CreateTocuhDef("BtV6R", 116, 135, 80, 48, self.BtHandler,
                                None, False))
        self.ptDef.append(
            self.CreateTocuhDef("BtNaptL", 366, 135+109, 80, 48, self.BtHandler,
                                None, False))
        self.ptDef.append(
            self.CreateTocuhDef("BtNaptR", 116, 135+109, 80, 48, self.BtHandler,
                                None, False))
        self.ptDef.append(
            self.CreateTocuhDef("BtWanemL", 366, 135, 80, 48, self.BtHandler,
                                None, False))
        self.ptDef.append(
            self.CreateTocuhDef("BtWanemR", 116, 135, 80, 48, self.BtHandler,
                                None, False))
        self.ptDef.append(
            self.CreateTocuhDef("BtDhcpL", 366, 270, 80, 48, self.BtHandler,
                                None, False))
        self.ptDef.append(
            self.CreateTocuhDef("BtDhcpR", 116, 270, 80, 48, self.BtHandler,
                                None, False))
        self.ptDef.append(
            self.CreateTocuhDef("BtDhcpC", 254, 272, 100, 44, self.BtHandler,
                                None, False))
        self.ptDef.append(
            self.CreateTocuhDef("BtReboot", 318, 242, 100, 48, self.BtHandler,
                                None, False))
        self.ptDef.append(
            self.CreateTocuhDef("BtShutdown", 184, 242, 100, 48,
                                self.BtHandler, None, False))

        self.ptDef.append(
            self.CreateTocuhDef("BtApL", 366, 240, 36, 48, self.BtHandler,
                                None, False))
        self.ptDef.append(
            self.CreateTocuhDef("BtApR", 241, 240, 36, 48, self.BtHandler,
                                None, False))
        self.ptDef.append(
            self.CreateTocuhDef("BtChannelL", 200, 240, 36, 48, self.BtHandler,
                                None, False))
        self.ptDef.append(
            self.CreateTocuhDef("BtChannelR", 75, 240, 36, 48, self.BtHandler,
                                None, False))

        self.ptDef.append(
            self.CreateTocuhDef("BtMacReport0", 113, 148, 38, 48,
                                self.BtHandler, None, False))
        self.ptDef.append(
            self.CreateTocuhDef("BtMacTmpReport0", 77, 148, 38, 48,
                                self.BtHandler, None, False))
        self.ptDef.append(
            self.CreateTocuhDef("BtMacReport1", 113, 210, 38, 48,
                                self.BtHandler, None, False))
        self.ptDef.append(
            self.CreateTocuhDef("BtMacTmpReport1", 77, 210, 38, 48,
                                self.BtHandler, None, False))

    def BtHandler(self, key):
        print("BtHandler" + key)
        if key == "BtMenu":
            self.pWanem.Clear()
            self.nextScene = "Menu"
            self.state = self.STATE_TERM
        elif key == "BtTab0":
            self.SwitchTab(0)
        elif key == "BtTab1":
            self.SwitchTab(1)
        elif key == "BtTab2":
            self.SwitchTab(2)
        elif key == "BtTab3":
            self.SwitchTab(3)
        elif key == "BtTab4":
            self.SwitchTab(4)
        elif key == "BtApL":
            self.UpdateApMode(-1)
        elif key == "BtApR":
            self.UpdateApMode(1)
        elif key == "BtChannelL":
            self.UpdateApChannel(-1)
        elif key == "BtChannelR":
            self.UpdateApChannel(1)
        elif key == "BtV6L":
            self.UpdateV6Mode(-1)
        elif key == "BtV6R":
            self.UpdateV6Mode(1)
        elif key == "BtNaptL":
            self.UpdateNaptMode(-1)
        elif key == "BtNaptR":
            self.UpdateNatpMode(1)
        elif key == "BtWanemL":
            self.UpdateWanemMode(-1)
        elif key == "BtWanemR":
            self.UpdateWanemMode(1)
        elif key == "BtDhcpL":
            self.UpdateDhcpList(-2)
        elif key == "BtDhcpR":
            self.UpdateDhcpList(2)
        elif key == "BtDhcpC":
            self.LoadDhcpInfo()
            self.currentClientTotal = len(self.dhcpClientInfo)
            self.UpdateDhcpList(0)
        elif key == "BtMacReport0":
            if self.pCTX.apiStatus == 0:
                self.SendDhcpClientInfo(0, 0)
        elif key == "BtMacReport1":
            if self.pCTX.apiStatus == 0:
                self.SendDhcpClientInfo(1, 0)
        elif key == "BtMacTmpReport0":
            if self.pCTX.apiStatus == 0:
                self.SendDhcpClientInfo(0, 1)
        elif key == "BtMacTmpReport1":
            if self.pCTX.apiStatus == 0:
                self.SendDhcpClientInfo(1, 1)
        elif key == "BtReboot":
            self.Reboot()
        elif key == "BtShutdown":
            self.Shutdown()

    def UpdateApMode(self, vec):
        if vec != 0 and self.pCTX.wifiDongleExist == False:
            return

        self.currentApMode = (self.currentApMode + vec + 2) % 2
        c = self.pRender.N
        self.pRender.fb.draw.rect(c, Rect(166, 236, 74, 44), 0)

        c = self.pRender.ConvRgb(0.26, 0.1, 0.9)
        self.pRender.fb.putstr(168 - 5, 154 + 95 - 12,
                               self.apModeLabelsT[self.currentApMode], c, 2)
        self.pRender.fb.putstr(168, 154 + 95 + 12,
                               self.apModeLabelsB[self.currentApMode], c, 2)

        if vec != 0:
            self.currentChannel = 0
            self.UpdateApChannel(0, True)
            cmd = "cp /etc/wanem/tpl/" + str(
                self.currentApMode) + ".prop /etc/wanem/apmode.prop"
            try:
                subprocess.check_call(cmd.strip().split(" "))
                print("Update Ap Mode Success")
            except subprocess.CalledProcessError:
                print("Update Ap Mode Fail")

        return

    def UpdateApChannel(self, vec, forceUpdate=False):
        if self.currentApMode == 0:
            channelsLen = len(self.apChannelLabelsG)
        else:
            channelsLen = len(self.apChannelLabelsA)
        self.currentChannel = (self.currentChannel + vec +
                               channelsLen) % channelsLen
        c = self.pRender.N
        self.pRender.fb.draw.rect(c, Rect(166 + 175, 236, 74, 44), 0)

        c = self.pRender.ConvRgb(0.26, 0.1, 0.9)
        if self.currentApMode == 0:
            self.pRender.fb.putstr(168 + 175 - 18, 154 + 92,
                                   self.apChannelLabelsG[self.currentChannel],
                                   c, 3)
        else:
            self.pRender.fb.putstr(168 + 175 - 18, 154 + 92,
                                   self.apChannelLabelsA[self.currentChannel],
                                   c, 3)

        if vec != 0 or forceUpdate:
            cmd = "cp /etc/wanem/tpl/" + str(
                self.currentChannel) + ".prop /etc/wanem/apchannel.prop"
            try:
                subprocess.check_call(cmd.strip().split(" "))
                print("Update Ap Channel Success")
            except subprocess.CalledProcessError:
                print("Update Ap Channel Fail")
        return

    def UpdateV6Mode(self, vec):
        self.currentV6Mode = (self.currentV6Mode + vec +
                                len(self.v6ModeLabels)) % 3
        c = self.pRender.N
        self.pRender.fb.draw.rect(c, Rect(210, 140 + 95 + 10 - 105, 160, 24),
                                  c)
        c = self.pRender.ConvRgb(0.26, 0.1, 0.9)
        self.pRender.fb.putstr(225-12, 154 + 95 - 105,
                               self.v6ModeLabels[self.currentV6Mode], c, 2)

        if vec != 0:
            if self.currentV6Mode == 0:
                cmd = "cp /etc/iptables.ipv6.nat.type0 /etc/iptables.ipv6.nat"
                cmd2 = "php /home/pi/EM-uNetPi/scripts/php/IPv6Switcher.php 1"
            elif self.currentV6Mode == 1:
                cmd = "cp /etc/iptables.ipv6.nat.type2 /etc/iptables.ipv6.nat"
                cmd2 = "php /home/pi/EM-uNetPi/scripts/php/IPv6Switcher.php 0"
            elif self.currentV6Mode == 2:
                cmd = "cp /etc/iptables.ipv6.nat.type3 /etc/iptables.ipv6.nat"
                cmd2 = "php /home/pi/EM-uNetPi/scripts/php/IPv6Switcher.php 0"

            try:
                subprocess.check_call(cmd.strip().split(" "))
                print("Update V6 NAPT Mode Success")
            except subprocess.CalledProcessError:
                print("Update V6 NAPT Mode Fail")

            try:
                subprocess.check_call(cmd2.strip().split(" "))
                print("Update V6 Mode Success")
            except subprocess.CalledProcessError:
                print("Update V6 Mode Fail")
                
    def UpdateNatpMode(self, vec):
        self.currentNaptMode = (self.currentNaptMode + vec +
                                len(self.naptModeLabels)) % 2
        c = self.pRender.N
        self.pRender.fb.draw.rect(c, Rect(210, 140 + 95 + 10 - 105 + 109, 160, 24),
                                  c)
        c = self.pRender.ConvRgb(0.26, 0.1, 0.9)
        self.pRender.fb.putstr(225, 154 + 95 - 105 + 109,
                               self.naptModeLabels[self.currentNaptMode], c, 2)
        self.pRender.fb.putstr(
            144, 294 - 105 + 109,
            'IP/NAT Setting change will be applied after reboot.',
            self.pRender.R, 1)

        if vec != 0:
            if self.currentNaptMode == 0:
                cmd = "cp /etc/iptables.ipv4.nat.type2 /etc/iptables.ipv4.nat"
            elif self.currentNaptMode == 1:
                cmd = "cp /etc/iptables.ipv4.nat.type3 /etc/iptables.ipv4.nat"

            try:
                subprocess.check_call(cmd.strip().split(" "))
                print("Update Napt Mode Success")
            except subprocess.CalledProcessError:
                print("Update Napt Mode Fail")

    def UpdateWanemMode(self, vec):
        self.currentWanemMode = (self.currentWanemMode + vec +
                                 len(self.wanemModeLabels)) % 2
        c = self.pRender.N
        self.pRender.fb.draw.rect(c, Rect(210, 140 + 95 + 10 - 105, 160, 24),
                                  c)
        c = self.pRender.ConvRgb(0.26, 0.1, 0.9)
        self.pRender.fb.putstr(225, 154 + 95 - 105,
                               self.wanemModeLabels[self.currentWanemMode], c,
                               2)

        if vec != 0:
            cmd = "cp /etc/wanem/tpl/" + str(
                self.currentWanemMode) + ".prop /etc/wanem/wanemmode.prop"
            try:
                subprocess.check_call(cmd.strip().split(" "))
                print("Update Wanem Mode Success")
            except subprocess.CalledProcessError:
                print("Update Wanem Mode Fail")
            self.pWanem.wanemMode = self.currentWanemMode

    def RenderHeaderLabel(self, baseY, label):
        c = self.pRender.ConvRgb(0.32, 0.4, 0.8)
        self.pRender.fb.draw.rect(c, Rect(120, baseY, 340, 32), 0)
        c = self.pRender.ConvRgb(0.32, 0.4, 0.2)
        self.pRender.fb.putstr(130, baseY + 10, label, c, 2)

    def RenderHeaderLabelTwin(self, baseY, label1, label2):
        c = self.pRender.ConvRgb(0.32, 0.4, 0.8)
        self.pRender.fb.draw.rect(c, Rect(120, baseY, 165, 32), 0)
        c = self.pRender.ConvRgb(0.32, 0.4, 0.2)
        self.pRender.fb.putstr(140, baseY + 10, label1, c, 2)

        c = self.pRender.ConvRgb(0.32, 0.4, 0.8)
        self.pRender.fb.draw.rect(c, Rect(120 + 175, baseY, 165, 32), 0)
        c = self.pRender.ConvRgb(0.32, 0.4, 0.2)
        self.pRender.fb.putstr(140 + 175, baseY + 10, label2, c, 2)

    def SwitchTab(self, activeIdx):
        labels = ["AP", "IP/NAT", "SYSTEM", "CLIENT", "MISC"]

        if activeIdx == self.currentIdx:
            return

        # Cleanup
        if self.currentIdx == 0:
            self.SetTouchActive("BtApL", False)
            self.SetTouchActive("BtApR", False)
            self.SetTouchActive("BtChannelL", False)
            self.SetTouchActive("BtChannelR", False)
        elif self.currentIdx == 1:
            self.SetTouchActive("BtV6L", False)
            self.SetTouchActive("BtV6R", False)
            self.SetTouchActive("BtNaptL", False)
            self.SetTouchActive("BtNaptR", False)
        #elif self.currentIdx == 2:
        elif self.currentIdx == 3:
            self.SetTouchActive("BtDhcpL", False)
            self.SetTouchActive("BtDhcpC", False)
            self.SetTouchActive("BtDhcpR", False)
            self.SetTouchActive("BtMacReport0", False)
            self.SetTouchActive("BtMacReport1", False)
            self.SetTouchActive("BtMacTmpReport0", False)
            self.SetTouchActive("BtMacTmpReport1", False)
        elif self.currentIdx == 4:
            self.SetTouchActive("BtReboot", False)
            self.SetTouchActive("BtShutdown", False)
            self.SetTouchActive("BtWanemL", False)
            self.SetTouchActive("BtWanemR", False)

        c = self.pRender.N
        self.pRender.fb.draw.rect(c, Rect(94, 84, 6, 224), 0)
        self.pRender.fb.draw.rect(c, Rect(110, 84, 360, 230), 0)

        self.currentIdx = activeIdx

        # RenderTab
        c = self.pRender.ConvRgb(0.0, 0.0, 0.8)
        self.pRender.fb.draw.rect(c, Rect(100, 84, 1, 224), 0)

        for idx in range(len(labels)):
            baseY = 85 + 45 * idx
            if activeIdx == idx:
                c = self.pRender.ConvRgb(0.0, 0.0, 0.8)
                tabW = 90
            else:
                c = self.pRender.ConvRgb(0.0, 0.0, 0.5)
                tabW = 84

            self.pRender.fb.draw.rect(c, Rect(10, baseY, tabW, 42), 0)
            c = self.pRender.ConvRgb(0.0, 0.0, 1)
            self.pRender.fb.putstr(17, baseY + 14, labels[idx], c, 2)

        # RenderSubMode
        if activeIdx == 0:
            self.RenderTab0()
        elif activeIdx == 1:
            self.RenderTab1()
        elif activeIdx == 2:
            self.RenderTab2()
        elif activeIdx == 3:
            self.RenderTab3()
        elif activeIdx == 4:
            self.RenderTab4()

    def RenderTab0(self):
        self.RenderHeaderLabel(85, "      AP Information")

        self.pRender.fb.putstr(130, 128 + 32 * 0,
                               "SSID : wanem-" + self.GetSelfId(),
                               self.pRender.W, 2)
        self.pRender.fb.putstr(130, 128 + 32 * 1,
                               "PASS : wanem-" + self.GetSelfId(),
                               self.pRender.W, 2)

        self.RenderHeaderLabelTwin(190, "  AP Mode", "  Channel")

        if self.pCTX.wifiDongleExist:
            prefix = 0
        else:
            prefix = 0.4

        c = self.pRender.ConvRgb(0.26, 0.1, 0.9 - prefix)
        self.pRender.fb.draw.rect(c, Rect(120, 140 + 95, 36, 44), 0)
        self.pRender.fb.draw.rect(c, Rect(248, 140 + 95, 36, 44), 0)
        c = self.pRender.ConvRgb(0.26, 0, 0.5 - prefix)
        self.pRender.fb.draw.rect(c, Rect(120, 140 + 44 + 95, 36, 4), 0)
        self.pRender.fb.draw.rect(c, Rect(248, 140 + 44 + 95, 36, 4), 0)
        c = self.pRender.ConvRgb(0.26, 0, 0.5)
        self.pRender.fb.putstr(122, 140 + 6 + 95, '<', 0, 5)
        self.pRender.fb.putstr(253, 140 + 6 + 95, '>', 0, 5)

        c = self.pRender.ConvRgb(0.26, 0.1, 0.9)
        self.pRender.fb.draw.rect(c, Rect(120 + 175, 140 + 95, 36, 44), 0)
        self.pRender.fb.draw.rect(c, Rect(248 + 175, 140 + 95, 36, 44), 0)
        c = self.pRender.ConvRgb(0.26, 0, 0.5)
        self.pRender.fb.draw.rect(c, Rect(120 + 175, 140 + 44 + 95, 36, 4), 0)
        self.pRender.fb.draw.rect(c, Rect(248 + 175, 140 + 44 + 95, 36, 4), 0)
        self.pRender.fb.putstr(122 + 175, 140 + 6 + 95, '<', 0, 5)
        self.pRender.fb.putstr(253 + 175, 140 + 6 + 95, '>', 0, 5)

        self.pRender.fb.putstr(
            144, 294, 'AP Setting change will be applied after reboot.',
            self.pRender.R, 1)

        self.UpdateApMode(0)
        self.UpdateApChannel(0)

        self.SetTouchActive("BtApL", True)
        self.SetTouchActive("BtApR", True)
        self.SetTouchActive("BtChannelL", True)
        self.SetTouchActive("BtChannelR", True)

        return

    def RenderTab1(self):

        self.RenderHeaderLabel(85, "     IPv6 Mode Setting    ")
        c = self.pRender.ConvRgb(0.26, 0.1, 0.9)
        self.pRender.fb.draw.rect(c, Rect(120, 140 + 95 - 105, 80, 44), 0)
        self.pRender.fb.draw.rect(c, Rect(380, 140 + 95 - 105, 80, 44), 0)
        self.pRender.fb.draw.rect(c, Rect(120, 140 + 95 - 105 + 109, 80, 44), 0)
        self.pRender.fb.draw.rect(c, Rect(380, 140 + 95 - 105 + 109, 80, 44), 0)

        self.UpdateV6Mode(0)

        c = self.pRender.ConvRgb(0.26, 0, 0.5)
        self.pRender.fb.draw.rect(c, Rect(120, 140 + 44 + 95 - 105, 80, 4), 0)
        self.pRender.fb.draw.rect(c, Rect(380, 140 + 44 + 95 - 105, 80, 4), 0)
        self.pRender.fb.putstr(120 + 20, 140 + 6 + 95 - 105, '<', 0, 5)
        self.pRender.fb.putstr(382 + 20 + 5, 140 + 6 + 95 - 105, '>', 0, 5)
        
        self.UpdateNatpMode(0)
        
        c = self.pRender.ConvRgb(0.26, 0, 0.5)
        self.pRender.fb.draw.rect(c, Rect(120, 140 + 44 + 95 - 105 + 109, 80, 4), 0)
        self.pRender.fb.draw.rect(c, Rect(380, 140 + 44 + 95 - 105 + 109, 80, 4), 0)
        self.pRender.fb.putstr(120 + 20, 140 + 6 + 95 - 105 + 109, '<', 0, 5)
        self.pRender.fb.putstr(382 + 20 + 5, 140 + 6 + 95 - 105 + 109, '>', 0, 5)

        self.SetTouchActive("BtV6L", True)
        self.SetTouchActive("BtV6R", True)
        self.SetTouchActive("BtNaptL", True)
        self.SetTouchActive("BtNaptR", True)

        self.RenderHeaderLabel(194, "     IPv4 NAPT Setting    ")
        
    def RenderTab2(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        try:
            ifreq = struct.pack('16s16x', 'eth0'.encode())
            SIOCGIFADDR = 0x8915
            ifaddr = ioctl(sock.fileno(), SIOCGIFADDR, ifreq)
            _, sa_family, port, in_addr = struct.unpack('16sHH4s8x', ifaddr)
            wanIp = socket.inet_ntoa(in_addr)
        except IOError:
            wanIp = "0.0.0.0"

        ifreq = struct.pack('16s16x', 'wlan0'.encode())
        SIOCGIFADDR = 0x8915
        ifaddr = ioctl(sock.fileno(), SIOCGIFADDR, ifreq)
        _, sa_family, port, in_addr = struct.unpack('16sHH4s8x', ifaddr)
        lanIp = socket.inet_ntoa(in_addr)

        ifreq = struct.pack('16s16x', 'eth1'.encode())
        SIOCGIFADDR = 0x8915

        retryLimit = 1
        retryCnt = 0
        while retryCnt <= retryLimit:
            try:
                ifaddr = ioctl(sock.fileno(), SIOCGIFADDR, ifreq)
                _, sa_family, port, in_addr = struct.unpack('16sHH4s8x', ifaddr) 
                lan2Ip = socket.inet_ntoa(in_addr)
                break
            except:
                if retryCnt == 0:
                    subprocess.check_call(['nmcli', 'connection', 'up', 'Wired connection 2'])
                    
            lan2Ip = "0.0.0.0"
            retryCnt += 1                
               
        ifreq = struct.pack('256s', 'eth0'.encode())
        SIOCGIFHWADDR = 0x8927
        ifaddr = ioctl(sock.fileno(), SIOCGIFHWADDR, ifreq)
        hwaddr = ''.join(['%02x:' % char for char in ifaddr[18:24]])[:-1]

        sock.close()

        #print socket.inet_ntoa(in_addr)

        wanIp6 = "-"
        if self.pCTX.v6Available == True:
            addrList = V6Util.GetGua()
            for addr in addrList:
                # raspbian OS なので 一旦初手確定で
                tmpAddr = addr.split('/')
                wanIp6 = tmpAddr[0]
                break

        if self.pCTX.v6Available == True:
            
            self.RenderHeaderLabel(85, "       Network Info      ")
            self.pRender.fb.putstr(120, 128 + 32 * 0, "WAN IP:",
                                   self.pRender.W, 2)
            self.pRender.fb.putstr(104 + 108, 128 - 4,
                                   "V4 > " + wanIp, self.pRender.W, 1)
            self.pRender.fb.putstr(104 + 108, 128 + 12,
                                   "V6 > " + wanIp6, self.pRender.W, 1)

            self.pRender.fb.putstr(120, 128 + 32 * 1, "LAN IP:",
                                   self.pRender.W, 2)
            self.pRender.fb.putstr(104 + 108, 128 + 28 * 1,
                                   "WIRELESS > " + lanIp, self.pRender.W, 1)
            self.pRender.fb.putstr(104 + 108, 128 + 28 * 1 + 16 * 1,
                                   "           " + self.pCTX.wlanV6Addr, self.pRender.W, 1)
            self.pRender.fb.putstr(104 + 108, 128 + 28 * 1 + 16 * 2,
                                   "WIRED    > " + lan2Ip, self.pRender.W, 1)
            self.pRender.fb.putstr(104 + 108, 128 + 28 * 1 + 16 * 3,
                                   "           " + self.pCTX.lanV6Addr, self.pRender.W, 1)
            
            self.pRender.fb.putstr(120, 128 + 32 * 3 - 4, "MAC   : " + hwaddr,
                                   self.pRender.W, 2)
            
            self.RenderHeaderLabel(220 + 32 -8, "       NEP REVISION")
            self.pRender.fb.putstr(120, 220 + 47 + 32 - 12, "REV   : " + self.pCTX.revision,
                                   self.pRender.W, 2)
            
        else:
            
            self.RenderHeaderLabel(85, "       Network Info      ")
            self.pRender.fb.putstr(130, 128 + 32 * 0, "WAN IP : " + wanIp,
                                self.pRender.W, 2)            
            self.pRender.fb.putstr(130, 128 + 32 * 1, "LAN IP : ",
                                   self.pRender.W, 2)
            self.pRender.fb.putstr(130 + 108, 128 + 28 * 1,
                                   "WIRELESS > " + lanIp, self.pRender.W, 1)
            self.pRender.fb.putstr(130 + 108, 128 + 28 * 1 + 16,
                                   "WIRED    > " + lan2Ip, self.pRender.W, 1)

            self.pRender.fb.putstr(130, 128 + 32 * 2, "MAC    : " + hwaddr,
                                   self.pRender.W, 2)

            self.RenderHeaderLabel(220, "       NEP REVISION")
            self.pRender.fb.putstr(130, 220 + 47, "REV    : " + self.pCTX.revision,
                                   self.pRender.W, 2)

        return

    def RenderClientInfo(self, idx, total, ip, mac, clientHostname, isSended):
        if idx % 2 == 0:
            baseY = 128
        else:
            baseY = 128 + 24 * 2 + 16

        self.pRender.fb.putstr(
            120, baseY, "Client " + str(idx + 1) + "/" + str(total) + " : " +
            clientHostname, self.pRender.W, 1)
        self.pRender.fb.putstr(120, baseY + 24 * 0 + 14, "IP :" + ip,
                               self.pRender.W, 2)
        self.pRender.fb.putstr(120, baseY + 24 * 1 + 14, "MAC:" + mac,
                               self.pRender.W, 2)

        if self.pCTX.apiStatus == 0:
            if isSended == 0:
                c = self.pRender.ConvRgb(0.26, 0.1, 0.9)
                self.pRender.fb.draw.rect(c, Rect(382, baseY + 10, 38, 44), 0)
                c = self.pRender.ConvRgb(0.46, 0.3, 0.9)
                self.pRender.fb.draw.rect(c, Rect(382 + 40, baseY + 10, 38,
                                                  44), 0)
                c = self.pRender.ConvRgb(0.26, 0, 0.5)
                self.pRender.fb.draw.rect(c, Rect(382, baseY + 54, 38, 4), 0)
                self.pRender.fb.putstr(384, baseY + 29, 'REGIST', 0, 1)
                c = self.pRender.ConvRgb(0.46, 0, 0.5)
                self.pRender.fb.draw.rect(c, Rect(382 + 40, baseY + 54, 38, 4),
                                          0)
                self.pRender.fb.putstr(384 + 39, baseY + 29, 'TMPADD', 0, 1)
            else:
                c = self.pRender.ConvRgb(0.96, 0.4, 0.9)
                self.pRender.fb.draw.rect(
                    c, Rect(382, baseY + 10, 38 * 2 + 2, 48), 0)
                c = self.pRender.ConvRgb(0.96, 0, 0.5)
                self.pRender.fb.putstr(384 + 18, baseY + 30, 'SENDED', 0, 1)

    def UpdateDhcpList(self, vec, isCleanup=True):
        if isCleanup == True:
            self.pRender.fb.draw.rect(self.pRender.N, Rect(120, 124, 340, 128),
                                      0)

        if self.currentClientTotal > 1:
            block = self.currentClientTotal
            if (block % 2) == 1:
                block += 1
            self.currentClientIdx = (self.currentClientIdx + vec +
                                     block) % block

        if self.currentClientIdx < self.currentClientTotal:
            info = self.dhcpClientInfo[self.currentClientIdx]
            self.RenderClientInfo(info[0], self.currentClientTotal, info[1],
                                  info[2], info[3], info[4])
            self.SetTouchActive("BtMacReport0", True)
            self.SetTouchActive("BtMacTmpReport0", True)
        else:
            self.SetTouchActive("BtMacReport0", False)
            self.SetTouchActive("BtMacTmpReport0", False)
        if (self.currentClientIdx + 1) < self.currentClientTotal:
            info = self.dhcpClientInfo[self.currentClientIdx + 1]
            self.RenderClientInfo(info[0], self.currentClientTotal, info[1],
                                  info[2], info[3], info[4])
            self.SetTouchActive("BtMacReport1", True)
            self.SetTouchActive("BtMacTmpReport1", True)
        else:
            self.SetTouchActive("BtMacReport1", False)
            self.SetTouchActive("BtMacTmpReport1", False)

    def SendDhcpClientInfo(self, odd, isTmp):
        # add BtEffect
        block = self.currentClientTotal
        if (block % 2) == 1:
            block += 1
        target = self.currentClientIdx + odd
        info = self.dhcpClientInfo[target]

        if info[4] != 0:
            return
        else:
            info[4] = 1

        baseY = 128 + 64 * odd

        c = self.pRender.ConvRgb(0.56, 0.4, 0.5)
        self.pRender.fb.draw.rect(c, Rect(382, baseY + 10, 38 * 2 + 2, 48), 0)
        c = self.pRender.ConvRgb(0.26, 0.8, 0.5)
        self.pRender.fb.putstr(384 + 18, baseY + 30, 'SENDING', 0, 1)

        LogReporter.ReportDhcpClientInfo(self.pCTX, info,
                                         "wanem-" + self.GetSelfId(), isTmp)

        c = self.pRender.ConvRgb(0.96, 0.4, 0.9)
        self.pRender.fb.draw.rect(c, Rect(382, baseY + 10, 38 * 2 + 2, 48), 0)
        c = self.pRender.ConvRgb(0.96, 0, 0.5)
        self.pRender.fb.putstr(384 + 18, baseY + 30, 'SENDED', 0, 1)

    def RenderTab3(self):
        self.RenderHeaderLabel(85, "        Client List")

        self.UpdateDhcpList(0, False)

        c = self.pRender.ConvRgb(0.26, 0.1, 0.9)
        self.pRender.fb.draw.rect(c, Rect(120, 140 + 124, 80, 40), 0)
        self.pRender.fb.draw.rect(c, Rect(380, 140 + 124, 80, 40), 0)
        self.pRender.fb.draw.rect(c, Rect(240, 140 + 124 + 2, 100, 36), 0)
        c = self.pRender.ConvRgb(0.26, 0, 0.5)
        self.pRender.fb.draw.rect(c, Rect(120, 140 + 44 + 120, 80, 4), 0)
        self.pRender.fb.draw.rect(c, Rect(380, 140 + 44 + 120, 80, 4), 0)
        self.pRender.fb.draw.rect(c, Rect(240, 140 + 44 + 120 - 2, 100, 4), 0)
        self.pRender.fb.putstr(120 + 20, 140 + 6 + 120, '<', 0, 5)
        self.pRender.fb.putstr(382 + 20 + 5, 140 + 6 + 120, '>', 0, 5)
        self.pRender.fb.putstr(248, 140 + 6 + 130, 'Refresh', 0, 2)

        self.SetTouchActive("BtDhcpL", True)
        self.SetTouchActive("BtDhcpC", True)
        self.SetTouchActive("BtDhcpR", True)

        return

    def Reboot(self):
        cmd = "reboot"
        try:
            self.pRender.fb.putstr(220, 294, ' Now Reboot ', self.pRender.R, 2)
            subprocess.check_call(cmd.strip().split(" "))
        except subprocess.CalledProcessError:
            print("Reboot Fail.")
            self.pRender.fb.putstr(220, 294, ' Reboot Err ', self.pRender.R, 2)

    def Shutdown(self):
        cmd = "shutdown -h now"
        try:
            self.pRender.fb.putstr(220, 294, 'Now Shutdown', self.pRender.R, 2)
            subprocess.check_call(cmd.strip().split(" "))
        except subprocess.CalledProcessError:
            print("Shutdown Fail.")
            self.pRender.fb.putstr(220, 294, 'Shutdown Err', self.pRender.R, 2)

    def RenderTab4(self):
        self.RenderHeaderLabel(85, "        Wanem Mode")

        c = self.pRender.ConvRgb(0.26, 0.1, 0.9)
        self.pRender.fb.draw.rect(c, Rect(120, 140 + 95 - 105, 80, 44), 0)
        self.pRender.fb.draw.rect(c, Rect(380, 140 + 95 - 105, 80, 44), 0)
        self.UpdateWanemMode(0)

        c = self.pRender.ConvRgb(0.26, 0, 0.5)
        self.pRender.fb.draw.rect(c, Rect(120, 140 + 44 + 95 - 105, 80, 4), 0)
        self.pRender.fb.draw.rect(c, Rect(380, 140 + 44 + 95 - 105, 80, 4), 0)
        self.pRender.fb.putstr(120 + 20, 140 + 6 + 95 - 105, '<', 0, 5)
        self.pRender.fb.putstr(382 + 20 + 5, 140 + 6 + 95 - 105, '>', 0, 5)

        self.SetTouchActive("BtWanemL", True)
        self.SetTouchActive("BtWanemR", True)

        self.RenderHeaderLabel(194, "     Hardware Control")

        c = self.pRender.ConvRgb(0.26, 0.1, 0.9)
        self.pRender.fb.draw.rect(c, Rect(240 - 70, 240, 100, 40), 0)
        self.pRender.fb.draw.rect(c, Rect(240 + 70, 240, 100, 40), 0)
        c = self.pRender.ConvRgb(0.26, 0, 0.5)
        self.pRender.fb.draw.rect(c, Rect(240 - 70, 240 + 40, 100, 4), 0)
        self.pRender.fb.putstr(254 - 70, 240 + 12, 'Reboot', 0, 2)
        self.pRender.fb.draw.rect(c, Rect(240 + 70, 240 + 40, 100, 4), 0)
        self.pRender.fb.putstr(243 + 70, 240 + 12, 'Shutdown', 0, 2)

        self.SetTouchActive("BtReboot", True)
        self.SetTouchActive("BtShutdown", True)

        self.pRender.fb.putstr(130 + 80, 300, self.pCTX.copyright,
                               self.pRender.W, 1)

        return

    def LoadDhcpInfo(self):
        self.dhcpClientInfo = []

        state = ""
        ip = ""
        mac = ""
        clientHostname = ""

        try:
            f = open('/var/lib/dhcp/dhcpd.leases', 'r')
            for line in f:

                if len(line) < 1:
                    continue

                if line[0:1] == '}':
                    #if 1 or state == "active":
                    if state == "active":
                        isExist = False
                        for node in self.dhcpClientInfo:
                            if node[2] == mac:
                                node[1] = ip
                                if node[3] == "":
                                    node[3] = clientHostname
                                isExist = True
                                break
                        if isExist == False:
                            self.dhcpClientInfo.append([
                                len(self.dhcpClientInfo), ip, mac,
                                clientHostname, 0
                            ])

                        state = ""
                        ip = ""
                        mac = ""
                        clientHostname = ""
                        continue

                if len(line) < 10:
                    continue

                elm = line.split()
                if len(elm) < 2:
                    continue

                if elm[0] == 'lease':
                    ip = elm[1]
                    # init params
                    state = ""
                    mac = ""
                    clientHostname = ""
                    #print("lease " + ip)
                    continue
                elif elm[0] == 'binding':
                    state = elm[2][0:-1]
                    #print("binding " + state)
                    continue
                elif elm[0] == 'hardware':
                    mac = elm[2][0:-1]
                    #print("hardware " + mac)
                    continue
                elif elm[0] == 'client-hostname':
                    if len(elm[1]) >= 3:
                        tmp = elm[1]
                        clientHostname = tmp[1:-2]
                        #print("client-hostname " + clientHostname)
                    continue

            f.close()
        except Exception as e:
            print('=== EXCEPTION ===')
            print('type:' + str(type(e)))
            print('args:' + str(e.args))
            print('message:' + e.message)
            print('e:' + str(e))

    def LoadDhcpInfoWlan(self):
        ip = ""
        mac = ""
        clientHostname = ""

        try:
            f = open('/var/lib/NetworkManager/dnsmasq-wlan0.leases', 'r')
            for line in f:

                if len(line) < 1:
                    continue

                elm = line.split()
                ip = elm[2]
                mac = elm[1]
                clientHostname = elm[3]

                self.dhcpClientInfo.append([
                    len(self.dhcpClientInfo), ip, mac,
                    clientHostname, 0
                ])

            f.close()
        except Exception as e:
            print('=== EXCEPTION ===')
            print('type:' + str(type(e)))
            print('args:' + str(e.args))
            print('message:' + e.message)
            print('e:' + str(e))
            
    def Start(self):
        super(ScSetting, self).Start()

        self.currentIdx = -1
        self.initialMode = 0

        cmd = "diff /etc/iptables.ipv6.nat.type0 /etc/iptables.ipv6.nat"
        try:
            subprocess.check_call(cmd.strip().split(" "))
            self.currentV6Mode = 0
        except subprocess.CalledProcessError:
            self.currentV6Mode = -1

        if self.currentV6Mode == -1:
            cmd = "diff /etc/iptables.ipv6.nat.type2 /etc/iptables.ipv6.nat"
            try:
                subprocess.check_call(cmd.strip().split(" "))
                self.currentV6Mode = 1
            except subprocess.CalledProcessError:
                self.currentV6Mode = 2
        
        cmd = "diff /etc/iptables.ipv4.nat.type2 /etc/iptables.ipv4.nat"
        try:
            subprocess.check_call(cmd.strip().split(" "))
            self.currentNaptMode = 0
        except subprocess.CalledProcessError:
            self.currentNaptMode = 1

        cmd = "cat /etc/wanem/wanemmode.prop"
        try:
            self.currentWanemMode = int(
                subprocess.check_output(cmd.strip().split(" ")).decode().replace(
                    '\n', ''))
        except subprocess.CalledProcessError:
            self.currentWanemMode = 0

        cmd = "cat /etc/wanem/apchannel.prop"
        try:
            self.currentChannel = int(
                subprocess.check_output(cmd.strip().split(" ")).decode().replace(
                    '\n', ''))
        except subprocess.CalledProcessError:
            self.currentChannel = 1

        cmd = "cat /etc/wanem/apmode.prop"
        try:
            self.currentApMode = int(
                subprocess.check_output(cmd.strip().split(" ")).decode().replace(
                    '\n', ''))
        except subprocess.CalledProcessError:
            self.currentApMode = 0

        #print("[" + self.currentChannel + "]")
        #print("[" + self.currentApMode + "]")

        self.currentClientIdx = 0
        self.LoadDhcpInfo()
        self.LoadDhcpInfoWlan()
        self.currentClientTotal = len(self.dhcpClientInfo)

        ## [ RENDER ] ################################################################

        self.pRender.UpdateTitle("WAN Emulation - Setting")
        self.pRender.UpdateSubTitle("current config")

        c = yellow = self.pRender.fb.rgb(255, 255, 0)
        self.pRender.fb.draw.rect(c, Rect(0, 54, self.pRender.xres, 1), 0)
        self.pRender.fb.draw.rect(c, Rect(0, 74, self.pRender.xres, 1), 0)
        self.pRender.fb.draw.rect(c, Rect(0, 54, 10 + 60, 20), 0)
        self.pRender.fb.draw.rect(c, Rect(480 - 10, 54, 10, 20), 0)
        self.pRender.fb.putstr(26, 54 + 7, ">>>", self.pRender.N, 1)

        self.RenderBackBt(True)

        ##############################################################################

        self.SwitchTab(self.initialMode)

        return

import sys, getopt, struct, time, termios, fcntl, sys, os, colorsys
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/fbtft')
from fb import Framebuffer
from gfx import Rect


class RenderManager:
    def ConvRgb(self, color, saturation, brightness):
        rgb = colorsys.hsv_to_rgb(
            color, saturation,
            brightness)  # rgb (color, light, light),,,poi? 0 < range < 1
        r = int(rgb[0] * ((1 << self.fb.red.length) - 1))
        g = int(rgb[1] * ((1 << self.fb.green.length) - 1))
        b = int(rgb[2] * ((1 << self.fb.blue.length) - 1))
        return self.fb.rgb(r, g, b)

    def __init__(self):
        self.device = '/dev/fb1'
        self.xres = 480
        self.yres = 320
        self.fb = Framebuffer(self.device)
        print self.fb
        self.Clear()
        print "# %-30s [ %s ]" % ("Renderer Initialize", "OK")
        self.laneState = [-1, -1, -1]
        # pink 0.9, purple 0.8, blue 0.7-0.5, green 0.3-0.1, yello 0.16,
        self.N = self.ConvRgb(0, 0, 0)
        self.W = self.ConvRgb(1, 0, 1)
        self.D = self.ConvRgb(1, 0, 0.2)
        self.B = self.ConvRgb(0.7, 1, 1)
        self.G = self.ConvRgb(0.4, 1, 1)
        self.Y = self.ConvRgb(0.16, 1, 1)
        self.O = self.ConvRgb(0.08, 1, 1)
        self.R = self.ConvRgb(1, 1, 1)
        self.H = self.ConvRgb(0.2, 1, 1)
        self.X = self.ConvRgb(0.1, 0.1, 0.1)
        self.T = self.ConvRgb(0.16, 1, 1)
        #self.P = self.ConvRgb(0.82, 1, 1)
        self.P = self.ConvRgb(0.82, 1, 1)
        self.dotPattern = [
            [  # 0: test
                self.R, self.G, self.B, self.H, self.H, self.H, self.H, self.H,
                self.T, self.T, self.P, self.P, self.H, self.H, self.D, self.D
            ],
            [  # 1: chk1
                self.P, self.P, self.D, self.D, self.D, self.D, self.D, self.D,
                self.P, self.P, self.D, self.D, self.D, self.D, self.D, self.D
            ],
            [  # 2: chk2
                self.D, self.D, self.P, self.P, self.D, self.D, self.D, self.D,
                self.D, self.D, self.P, self.P, self.D, self.D, self.D, self.D
            ],
            [  # 3: chk3
                self.D, self.D, self.D, self.D, self.P, self.P, self.D, self.D,
                self.D, self.D, self.D, self.D, self.P, self.P, self.D, self.D
            ],
            [  # 4: chk4
                self.D, self.D, self.D, self.D, self.D, self.D, self.P, self.P,
                self.D, self.D, self.D, self.D, self.D, self.D, self.P, self.P
            ],
            [  # 5: AllDark
                self.D, self.D, self.D, self.D, self.D, self.D, self.D, self.D,
                self.D, self.D, self.D, self.D, self.D, self.D, self.D, self.D
            ],
            [  # 6: AllRed
                self.R, self.R, self.R, self.R, self.R, self.R, self.R, self.R,
                self.R, self.R, self.R, self.R, self.R, self.R, self.R, self.R
            ],
            [  # 7: Gage1
                self.B, self.D, self.D, self.D, self.D, self.D, self.D, self.D,
                self.B, self.D, self.D, self.D, self.D, self.D, self.D, self.D
            ],
            [  # 8: Gage2
                self.D, self.G, self.D, self.D, self.D, self.D, self.D, self.D,
                self.D, self.G, self.D, self.D, self.D, self.D, self.D, self.D
            ],
            [  # 9: Gage3
                self.D, self.D, self.Y, self.D, self.D, self.D, self.D, self.D,
                self.D, self.D, self.Y, self.D, self.D, self.D, self.D, self.D
            ],
            [  # 10: Gage4
                self.D, self.D, self.D, self.O, self.D, self.D, self.D, self.D,
                self.D, self.D, self.D, self.O, self.D, self.D, self.D, self.D
            ],
            [  # 11: Gage5
                self.D, self.D, self.D, self.D, self.R, self.D, self.D, self.D,
                self.D, self.D, self.D, self.D, self.R, self.D, self.D, self.D
            ],
            [
                self.X, self.X, self.X, self.X, self.X, self.X, self.X, self.X,
                self.X, self.X, self.X, self.X, self.X, self.X, self.X, self.X
            ]
        ]

    def Clear(self):
        self.fb.fill(0)

    def Finalize(self):
        self.fb.close()

    def UpdateTitle(self, msg):
        self.fb.draw.rect(self.N, Rect(20 + 60, 10, 440 - 60, 26), 0)
        self.fb.putstr(20 + 60, 20, msg, self.W, 2)

    def UpdateSubTitle(self, msg):
        self.fb.draw.rect(self.N, Rect(20 + 60, 46 + 14, 380, 12), 0)
        # self.fb.putstr(20 + 60, 46, msg, self.W, 2)
        self.fb.putstr(20 + 60, 46 + 14, msg, self.W, 1)

    def RenderDot(self, laneIdx, patIdx):
        w = 20
        h = 20

        #if self.laneState[laneIdx] == patIdx:
        #	return

        self.laneState[laneIdx] = patIdx
        pat = self.dotPattern[patIdx]

        for yidx in range(0, 2):
            yoffset = 80 * (laneIdx + 1) + (20 + 12) * yidx + 14
            for xidx in range(0, 8):
                xoffset = (20 + 12) * xidx + 14
                seek = yidx * 8 + xidx
                #print str(xoffset) + " : " + str(yoffset) + " : " + str(r)+","+str(g)+","+str(b)
                self.fb.draw.rect(pat[seek], Rect(xoffset, yoffset, w, h), 0)

    def RenderDotMini(self, laneIdx, patIdx):
        w = 20
        h = 20

        #if self.laneState[laneIdx] == patIdx:
        #	return

        self.laneState[laneIdx] = patIdx
        pat = self.dotPattern[patIdx]

        for yidx in range(0, 2):
            yoffset = 80 * (laneIdx + 1) + (20 + 12) * yidx + 14
            for xidx in range(0, 4):
                xoffset = (20 + 12) * xidx + 14
                seek = yidx * 8 + xidx
                #print str(xoffset) + " : " + str(yoffset) + " : " + str(r)+","+str(g)+","+str(b)
                self.fb.draw.rect(pat[seek], Rect(xoffset, yoffset, w, h), 0)

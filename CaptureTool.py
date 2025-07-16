import sys, getopt, struct, time, termios, fcntl, sys, os, colorsys, threading, time, datetime, subprocess, random, string, asyncio
from gfx import Rect
from RenderManager import RenderManager

class CaptureTool():
    
    def __init__(self, pRender, posX, posY):
        self.pRender = pRender
        self.btStatus = 0

    def RenderBt(self):
        if self.btStatus == 0:
            c = self.pRender.ConvRgb(0.81, 0.70, 0.8)
            self.pRender.fb.draw.rect(c, Rect(379, 7, 94, 38), 0)
            c = self.pRender.ConvRgb(0.81, 0.70, 0.3)
            self.pRender.fb.draw.rect(c, Rect(379, 7 + 38, 94, 4), 0)
            self.pRender.fb.putstr(385, 7 + 12, "Capture", c, 2)
        elif self.btStatus == 1:
            c = self.pRender.ConvRgb(0.81, 0.70, 0.3)
            self.pRender.fb.draw.rect(c, Rect(379, 7 + 38, 94, 4), 0)
            self.pRender.fb.draw.rect(c, Rect(381, 9, 90, 34), 0)

            date1 = datetime.datetime.now().strftime("%Y/%m/%d")
            date2 = datetime.datetime.now().strftime("%H:%M:%S")
            
            self.pRender.fb.putstr(385 + 1, 7 + 5, "Now Capturing", self.pRender.W, 1)
            self.pRender.fb.putstr(385 + 1, 7 + 16, date1, self.pRender.W, 1)
            self.pRender.fb.putstr(385 + 1, 7 + 27, date2, self.pRender.W, 1)

    def BtHandler(self):
        if self.btStatus != 0:
            return

        self.btStatus = 1
        self.RenderBt()

        self.CallCapture()
        
    def FireAndForget(func):
        def wrapper(*args, **kwargs):
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            return loop.run_in_executor(None, func, *args, *kwargs)
        return wrapper

    @FireAndForget
    def CallCapture(self):
        time.sleep(0.5)
        cmd = "make capture"
        try:
            subprocess.check_call(cmd.strip().split(" "), cwd="/home/pi/EM-uNetPi/screenshots/work")
            print("Capture Success.")
        except subprocess.CalledProcessError:
            print("Capture Fail.")
        time.sleep(0.5)
        self.btStatus = 0
        self.RenderBt()
        

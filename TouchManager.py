import sys, getopt, time, struct, termios, fcntl, sys, os, select
from time import sleep
from RenderManager import RenderManager
from WanemManager import WanemManager
from SceneManager import SceneManager


class TouchManager:
    def __init__(self, pScene):
        self.pScene = pScene
        #self.infile_path = "/dev/input/event" + (sys.argv[1] if len(sys.argv) > 1 else "0")
        self.infile_path = "/dev/input/event0"
        self.FORMAT = 'llHHI'
        self.EVENT_SIZE = struct.calcsize(self.FORMAT)
        self.lastPtX = 0
        self.lastPtY = 0
        self.rateX = float(480) / 3900
        self.rateY = float(320) / 3900
        self.sep = 0
        #print str(rateX)
        #print str(rateY)
        self.in_file = open(self.infile_path, "rb")
        flag = fcntl.fcntl(self.in_file, fcntl.F_GETFL)
        fcntl.fcntl(self.in_file, fcntl.F_SETFL, os.O_NONBLOCK)

    def PollEvent(self):

        try:
            event = self.in_file.read(self.EVENT_SIZE)
        except IOError, e:
            if e.errno == 11:
                return False

        (tv_sec, tv_usec, type, code,
         value) = struct.unpack(self.FORMAT, event)

        if type != 0 or code != 0 or value != 0:
            #print("Event type %u, code %u, value %u at %d.%d" % (type, code, value, tv_sec, tv_usec))
            # Events with code, type and value == 0 are "separator" events
            if code == 0:
                self.lastPtX = int(value * self.rateX)
                #self.sep = 0
            elif code == 1:
                self.lastPtY = int(value * self.rateY)
                if self.sep == 1:
                    self.sep = 0
                    #fDownCallback(pWanem, self.lastPtX, self.lastPtY)
                    self.pScene.TouchDownHandler(self.lastPtX, self.lastPtY)
            elif code == 330:
                self.sep = 1
            elif code == 24:
                if self.sep == 1:
                    self.sep = 0
                    #fUpCallback(pWanem, self.lastPtX, self.lastPtY)
                    self.pScene.TouchUpHandler(self.lastPtX, self.lastPtY)
            else:
                self.sep = 0
        else:
            self.sep = 0

        return True

    #def Update(self, pWanem, fDownCallback, fUpCallback, wait):
    def Update(self, wait):

        if wait <= 0.0:
            return False

        # https://repolinux.wordpress.com/2012/10/09/non-blocking-read-from-stdin-in-python/
        readable = select.select([self.in_file], [], [], wait)[0]
        if not readable:
            return

        recvable = True
        while recvable:
            recvable = self.PollEvent()

    def Finalize(self):
        self.in_file.close()

import sys, getopt, struct, time, termios, fcntl, sys, os, colorsys, threading, time, datetime, subprocess
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/fbtft')
from RenderManager import RenderManager
from WanemManager import WanemManager
from ScBase import ScBase
from gfx import Rect
from DataAsset import CTX
from time import sleep
from TouchManager import TouchManager
from WanemManager import WanemManager
from SceneManager import SceneManager
from argparse import ArgumentParser


def keypressed():
    try:
        c = sys.stdin.read(1)
        return True
    except IOError:
        return False


def pause(secs):
    fd = sys.stdin.fileno()

    oldterm = termios.tcgetattr(fd)
    newattr = termios.tcgetattr(fd)
    newattr[3] = newattr[3] & ~termios.ICANON & ~termios.ECHO
    termios.tcsetattr(fd, termios.TCSANOW, newattr)

    oldflags = fcntl.fcntl(fd, fcntl.F_GETFL)
    fcntl.fcntl(fd, fcntl.F_SETFL, oldflags | os.O_NONBLOCK)

    try:
        ctrlc = False
        paused = False
        t = secs / 0.1
        i = 0
        while i < t:
            if keypressed():
                paused = True
                break
            sleep(0.1)
            i += 1

        if paused:
            while True:
                if keypressed():
                    break
                sleep(0.1)
    except KeyboardInterrupt:
        ctrlc = True

    termios.tcsetattr(fd, termios.TCSAFLUSH, oldterm)
    fcntl.fcntl(fd, fcntl.F_SETFL, oldflags)
    if ctrlc:
        sys.exit(1)


def main(argv):

    desc = '{0} [Args] [Options]\nDetailed options -h or --help'.format(
        __file__)
    parser = ArgumentParser(description=desc)
    parser.add_argument('-debug', action='store_true', dest='debug')
    parser.add_argument('-scene',
                        type=str,
                        dest='initScene',
                        required=False,
                        help='initial scene')
    parser.add_argument('-proxy',
                        type=str,
                        dest='proxy',
                        required=False,
                        help='https proxy setting')
    args = parser.parse_args()
    #print str(args.debug)
    #print str(args.initScene)

    pCTX = CTX()
    pCTX.httpsProxy = args.proxy
    if pCTX.httpsProxy is None:
    	pCTX.httpsProxy = ""
    pRender = RenderManager()
    #pRender.RenderBaseFrame()
    pWanem = WanemManager(pCTX, pRender)
    pSceneManager = SceneManager(pCTX,
                                 pRender,
                                 pWanem,
                                 initScene=args.initScene,
                                 debug=args.debug)
    pTouch = TouchManager(pSceneManager)

    now = time.time()

    while True:
        pSceneManager.Update()

        pCTX.current = time.time()
        waitBy = now + (1 / 60.0 * pCTX.tick)
        #pTouch.Update(pWanem, TouchDownHandler, TouchUpHandler, waitBy - pCTX.current)
        pTouch.Update(waitBy - pCTX.current)

        pCTX.current = time.time()

        if waitBy > pCTX.current:
            time.sleep(waitBy - pCTX.current)
            pCTX.current = time.time()

        if pCTX.current - now >= 1.0:
            # print "pCTX.tick : %02d / %d" % (pCTX.tick, int(pCTX.current * 1000))
            now += 1.0
            pCTX.tick = 0

        pCTX.tick += 1

    pRender.Finalize()
    pTouch.Finalize()


if __name__ == '__main__':
    main(sys.argv[1:])

import sys, getopt, struct, time, termios, fcntl, sys, os, colorsys, select
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/fbtft')
from RenderManager import RenderManager
from WanemManager import WanemManager
from ScInit import ScInit
from ScMenu import ScMenu
from ScManual import ScManual
from ScManualEx import ScManualEx
from ScManualEx2 import ScManualEx2
from ScReplay import ScReplay
from ScPlayback import ScPlayback
from ScSetting import ScSetting
from ScRemoteApi import ScRemoteApi
from DataAsset import CTX


class SceneManager:
    def __init__(self, pCTX, pRender, pWanem, **params):
        self.pCTX = pCTX
        self.pRender = pRender
        self.pWanem = pWanem

        self.pCTX.debug = params["debug"]

        self.pScInit = ScInit(self.pCTX, self.pRender, self.pWanem)
        self.pScMenu = ScMenu(self.pCTX, self.pRender, self.pWanem)
        self.pScManual = ScManual(self.pCTX, self.pRender, self.pWanem)
        self.pScManualEx = ScManualEx(self.pCTX, self.pRender, self.pWanem)
        self.pScManualEx2 = ScManualEx2(self.pCTX, self.pRender, self.pWanem)
        self.pScReplay = ScReplay(self.pCTX, self.pRender, self.pWanem)
        self.pScPlayback = ScPlayback(self.pCTX, self.pRender, self.pWanem)
        self.pScSetting = ScSetting(self.pCTX, self.pRender, self.pWanem)
        self.pScRemoteApi = ScRemoteApi(self.pCTX, self.pRender, self.pWanem)

        if params["initScene"] == None:
            self.LoadScene("Init")
        else:
            self.LoadScene(params["initScene"])

    def Update(self):
        if self.m_currentScene is not None:
            self.m_currentScene.Update()
            if self.m_currentScene.state == self.m_currentScene.STATE_TERM:
                self.LoadScene(self.m_currentScene.nextScene)

    def TouchDownHandler(self, x, y):
        if self.m_currentScene is not None:
            self.m_currentScene.TouchDownHandler(x, y)

    def TouchUpHandler(self, x, y):
        if self.m_currentScene is not None:
            self.m_currentScene.TouchUpHandler(x, y)

    def LoadScene(self, nextScene):
        if nextScene == "":
            self.m_currentScene = None
            return

        if nextScene == "Init":
            self.m_currentScene = self.pScInit
        elif nextScene == "Menu":
            self.m_currentScene = self.pScMenu
        elif nextScene == "Manual":
            self.m_currentScene = self.pScManual
        elif nextScene == "ManualEx":
            self.m_currentScene = self.pScManualEx
        elif nextScene == "ManualEx2":
            self.m_currentScene = self.pScManualEx2
        elif nextScene == "Replay":
            self.m_currentScene = self.pScReplay
        elif nextScene == "Playback":
            self.m_currentScene = self.pScPlayback
        elif nextScene == "Setting":
            self.m_currentScene = self.pScSetting
        elif nextScene == "RemoteApi":
            self.m_currentScene = self.pScRemoteApi
        else:
            self.m_currentScene = self.pScMenu  # default

        self.m_currentScene.Start()

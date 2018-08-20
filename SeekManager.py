import sys, getopt, struct, time, termios, fcntl, sys, os, colorsys, threading, time, datetime, subprocess, random, os.path, math
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/fbtft')
from RenderManager import RenderManager
from WanemManager import WanemManager
from ScBase import ScBase
from gfx import Rect
from DataAsset import CTX

class SeekManager:

	def __init__(self, pCTX, progressBarResolution):
		self.pCTX                  = pCTX
		self.progressBarResolution = progressBarResolution
		self.isRepeat   = False
		self.isPause    = False
		self.laps       = range(0,self.progressBarResolution)
		self.updateInterval = 1
		
		self.dps        = 0
		self.totalFrame = 0
		
		self.seekFrame  = 0
		self.seekLap    = 0
		self.seekSec      = 0
				
	def Setup(self, dps, totalFrame):
		self.dps        = dps
		self.totalFrame = totalFrame
		self.updateInterval = int(60.0 / self.dps)
		
		if self.totalFrame == 0:
			return
		
		#totalSec = float(self.totalFrame) / self.dps
		
		for idx in range(1,self.progressBarResolution):
			#self.laps[idx-1] = int(totalSec / self.progressBarResolution * idx)
			self.laps[idx-1] = int(float(self.totalFrame) / self.progressBarResolution * idx)
			
	def Start(self):
		#self.startTime  = int(self.pCTX.current)
		self.seekSec    = -1 # Precount
		self.seekFrame  = 0
		self.seekLap    = 0

	def Stop(self):
		self.isPause    = False		
		self.seekSec    = -1 # Precount
		self.seekFrame  = 0
		self.seekLap    = 0
		return

	# Seek Impl 
	def Update(self, isBoundary):
		self.seekFrame += 1
		return

	def IsSeekSecOverCurrentLap(self):
		#if self.seekSec >= self.laps[self.seekLap]:
		if self.seekFrame >= self.laps[self.seekLap]:
			return True
		else:
			return False
	
	def Conv2FormatedTime(self, dps, frame):
		return "%02d:%02d" % (int(frame / dps / 60), int((frame / dps) % 60.0))	

	def GetTotalFormatTime(self):
		return self.Conv2FormatedTime(self.dps, self.totalFrame)

	def GetCurrentFormatTime(self):
		return self.Conv2FormatedTime(self.dps, self.seekFrame)

	def IsTerm(self):
		if self.seekFrame >= self.totalFrame:
			return True
		else:
			return False

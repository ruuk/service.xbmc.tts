# -*- coding: utf-8 -*-
from base import WindowReaderBase
from lib import util
import xbmc

class FullScreenVideoReader(WindowReaderBase):
	ID = 'fullscreenvideo'
	
	def init(self):
		self.mode = None
		self.progress = ''
		
	def updateMode(self,new_mode):
		if new_mode == self.mode: return False
		self.mode = new_mode
		return True

	def updateProgress(self,new_prog):
		if new_prog == self.progress: return False
		self.progress = new_prog
		return True
		
	def seek(self,isSpeaking):
		if self.updateMode('seeking'):
			return util.XT(773)
		else:
			st = xbmc.getInfoLabel('Player.Time')
			if not isSpeaking and self.updateProgress(st):
				return st.decode('utf-8')

	def getMonitoredText(self,isSpeaking=False):
		if xbmc.getCondVisibility('Player.Playing'):
			if xbmc.getCondVisibility('Player.DisplayAfterSeek'):
				return self.seek(isSpeaking)
			self.updateMode(None)
			return None
		elif xbmc.getCondVisibility('Player.Paused'):
			if xbmc.getCondVisibility('Player.Caching'):
				if self.updateMode('buffering'):
					return util.XT(15107)
				else:
					pct = xbmc.getInfoLabel('Player.CacheLevel')
					if not isSpeaking and self.updateProgress(pct):
						return pct.decode('utf-8')
			elif xbmc.getCondVisibility('!Player.Seeking + !Player.DisplayAfterSeek'):
				if self.updateMode('paused'):
					return util.XT(112)
			elif xbmc.getCondVisibility('Player.DisplayAfterSeek'):
				return self.seek(isSpeaking)
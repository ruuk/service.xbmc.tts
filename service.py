import sys, re, xbmc, xbmcgui
from lib import guitables
from lib import skintables
from lib import tts

from lib import util

class TTSService:
	def __init__(self):
		self.stop = False
		self.enabled = util.getSetting('enable',False)
		self.skinTable = skintables.getSkinTable()
		self.initState()
		self.tts = None
		self.initTTS()
		
	def initState(self):
		self.winID = None
		self.controlID = None
		self.text = None
		self.win = None
		
	def initTTS(self):
		self.setBackend(tts.getBackend()())
		
	def start(self):
		util.LOG('STARTED :: Enabled: %s :: Interval: %sms' % (self.enabled,self.tts.interval))
		if not self.enabled: return
		try:
			while self.enabled and (not xbmc.abortRequested) and (not self.stop):
				xbmc.sleep(self.tts.interval)
				self.checkForText()
		finally:
			self.tts.close()
			util.LOG('STOPPED')
		
	def setBackend(self,backend):
		self.tts = backend
		util.setSetting('voice',self.tts.currentVoice())
		
	def checkBackend(self):
		settingsBackend = tts.settingsBackend()
		if not settingsBackend: return
		if settingsBackend.provider == self.tts.provider: return
		self.setBackend(settingsBackend())
		
	def checkForText(self):
		newW = self.checkWindow()
		newC = self.checkControl(newW)
		text = self.getControlText(self.controlID)
		if text != self.text or newC: self.newText(text,newC)
	
	def sayText(self,text,interrupt=False):
		self.checkBackend()
		self.tts.say(text,interrupt)
		
	def checkWindow(self):
		winID = xbmcgui.getCurrentWindowId()
		dialogID = xbmcgui.getCurrentWindowDialogId()
		if dialogID != 9999: winID = dialogID
		if winID == self.winID: return False
		self.winID = winID
		del self.win
		self.win = xbmcgui.Window(winID)
		name = guitables.winNames.get(winID) or xbmc.getInfoLabel('System.CurrentWindow') or 'unknown'
		self.tts.say('Window: {0}'.format(name))
		self.tts.pause()
		return True
		
	def checkControl(self,newW):
		controlID = self.win.getFocusId()
		if controlID == self.controlID: return False
		if util.DEBUG: util.LOG('Control: %s' % controlID)
		self.controlID = controlID
		if self.skinTable and self.winID in self.skinTable:
			if self.controlID in self.skinTable[self.winID]:
				if 'prefix' in self.skinTable[self.winID][self.controlID]:
					self.sayText('{0}: {1}'.format(self.skinTable[self.winID][self.controlID]['prefix'],self.skinTable[self.winID][self.controlID]['name']),interrupt=not newW)
				else:
					self.sayText(self.skinTable[self.winID][self.controlID]['name'],interrupt=not newW)
				self.tts.pause()
		return True
		
	def newText(self,text,newC):
		self.text = text
		label2 = xbmc.getInfoLabel('Container({0}).ListItem.Label2'.format(self.controlID))
		seasEp = xbmc.getInfoLabel('Container({0}).ListItem.Property(SeasonEpisode)'.format(self.controlID)) or ''
		if label2:
			if seasEp:
				text = '{0}: {1}: {2} '.format(label2, text,self.formatSeasonEp(seasEp))
		self.sayText(text,interrupt=not newC)
		
	def getControlText(self,controlID):
		if not controlID: return ''
		text = xbmc.getInfoLabel('Container({0}).ListItem.Label'.format(controlID))
		if not text: text = xbmc.getInfoLabel('Control.GetLabel({0})'.format(controlID))
#		if not text:
#			try:
#				cont = self.win.getControl(controlID)
#				text = cont.getLabel()
#			except:
#				pass
#		if not text:
#			try:
#				cont = self.win.getFocus()
#				text = cont.getLabel()
#			except:
#				pass
			
		return self.formatText(text or '')
		
	def formatSeasonEp(self,seasEp):
		if not seasEp: return ''
		return seasEp.replace('S','season ').replace('E','episode ')
		
	def formatText(self,text):
		text = re.sub('\[/[^\[\]]+?\]','',text).rstrip(']')
		text = re.sub('\[[^\[\]]+?\]','',text)
		text = text.lstrip('[')
		if text == '..': text = 'Parent Directory'
		return text
	
if __name__ == '__main__':
	if len(sys.argv) > 1 and sys.argv[1] == 'voice_dialog':
		tts.selectVoice()
	else:
		TTSService().start()
import sys, re, xbmc, xbmcgui
from lib import guitables
from lib import skintables
from lib import backends

from lib import util

util.LOG(util.xbmcaddon.Addon().getAddonInfo('version'))
util.LOG('Platform: {0}'.format(sys.platform))

util.initCommands()

class TTSService(xbmc.Monitor):
	def __init__(self):
		self.stop = False
		self.enabled = True #util.getSetting('enable',False)
		self.skinTable = skintables.getSkinTable()
		self.initState()
		self.tts = None
		self.backendSettingID = None
		self.initTTS()
	
	def onAbortRequested(self):
		self.stop = True
		if self.tts: self.tts.close()
		
	def onSettingsChanged(self):
		command = util.getCommand()
		if not command: return
		util.LOG(command)
		if command == 'REPEAT':
			self.repeatText()
		elif command == 'EXTRA':
			self.sayExtra()
		elif command == 'ITEM_EXTRA':
			self.sayItemExtra()
		elif command == 'STOP':
			self.stopSpeech()

	def initState(self):
		self.winID = None
		self.controlID = None
		self.text = None
		self.win = None
		
	def initTTS(self):
		self.setBackend(backends.getBackend()())
		self.backendSettingID = util.getSetting('default_tts',-1)
		util.LOG('Backend: %s' % self.tts.provider)
		
	def start(self):
		util.LOG('STARTED :: Interval: %sms' % self.tts.interval)
		try:
			while self.enabled and (not xbmc.abortRequested) and (not self.stop):
				xbmc.sleep(self.tts.interval)
				self.checkForText()
		finally:
			self.tts.close()
			util.LOG('STOPPED')
		
	def setBackend(self,backend):
		if self.tts: self.tts.close()
		self.tts = backend
		util.setSetting('voice',self.tts.currentVoice())
		
	def checkBackend(self):
		backendSettingID = util.getSetting('default_tts',-1)
		if backendSettingID == self.backendSettingID: return
		self.initTTS()
		
	def checkForText(self):
		newW = self.checkWindow()
		newC = self.checkControl(newW)
		text = self.getControlText(self.controlID)
		if (text != self.text) or newC: self.newText(text,newC)
	
	def repeatText(self):
		self.winID = None
		self.controlID = None
		self.text = None
		self.checkForText()
		
	def sayExtra(self):
		texts = guitables.getExtraTexts(self.winID)
		self.sayTexts(texts)

	def sayItemExtra(self):
		text = xbmc.getInfoLabel('ListItem.Plot').decode('utf-8')
		if not text: text = xbmc.getInfoLabel('Container.ShowPlot').decode('utf-8')
		if not text: text = xbmc.getInfoLabel('ListItem.Property(Artist_Description)').decode('utf-8')
		if not text: text = xbmc.getInfoLabel('ListItem.Property(Album_Description)').decode('utf-8')
		if not text: text = xbmc.getInfoLabel('ListItem.Property(Addon.Description)').decode('utf-8')
		if not text: text = guitables.getSongInfo()
		if not text: return
		if not isinstance(text,list): text = [text]
		self.sayTexts(text)
			
	def sayText(self,text,interrupt=False):
		assert isinstance(text,unicode), "Not Unicode"
		self.checkBackend()
		self.tts.say(self.cleanText(text),interrupt)
		
	def sayTexts(self,texts,interrupt=True):
		if not texts: return
		self.sayText(texts.pop(0),interrupt=interrupt)
		for t in texts:
				self.pause()
				self.sayText(t)
	
	def pause(self):
		self.tts.pause()
		
	def stopSpeech(self):
		self.tts.stop()
		
	def checkWindow(self):
		winID = xbmcgui.getCurrentWindowId()
		dialogID = xbmcgui.getCurrentWindowDialogId()
		if dialogID != 9999: winID = dialogID
		if winID == self.winID: return False
		self.winID = winID
		del self.win
		self.win = xbmcgui.Window(winID)
		name = guitables.getWindowName(winID)
		heading = xbmc.getInfoLabel('Control.GetLabel(1)').decode('utf-8') or u''
		self.sayText(u'Window: {0}'.format(name),interrupt=True)
		self.pause()
		if heading:
			self.sayText(heading)
			self.pause()
		texts = guitables.getWindowTexts(winID)
		if texts:
			self.pause()
			for t in texts:
				self.sayText(t)
				self.pause()
		return True
		
	def checkControl(self,newW):
		controlID = self.win.getFocusId()
		if controlID == self.controlID: return newW
		if util.DEBUG:
			util.LOG('Control: %s' % controlID)
		self.controlID = controlID
		text = skintables.getControlText(self.skinTable,self.winID,self.controlID)
		if text:
			self.sayText(text,interrupt=not newW)
			self.tts.pause()
			return True
		return newW
		
	def newText(self,text,newC):
		self.text = text
		label2 = xbmc.getInfoLabel('Container({0}).ListItem.Label2'.format(self.controlID)).decode('utf-8')
		seasEp = xbmc.getInfoLabel('Container({0}).ListItem.Property(SeasonEpisode)'.format(self.controlID)).decode('utf-8') or u''
		if label2 and seasEp:
				text = u'{0}: {1}: {2} '.format(label2, text,self.formatSeasonEp(seasEp))
		self.sayText(text,interrupt=not newC)
		
	def getControlText(self,controlID):
		if not controlID: return u''
		text = xbmc.getInfoLabel('Container({0}).ListItem.Label'.format(controlID))
		if not text: text = xbmc.getInfoLabel('Control.GetLabel({0})'.format(controlID))
		if not text: text = xbmc.getInfoLabel('System.CurrentControl')
		if not text: return u''
		return text.decode('utf-8')
		
	def formatSeasonEp(self,seasEp):
		if not seasEp: return u''
		return seasEp.replace(u'S',u'season ').replace(u'E',u'episode ')
		
	def cleanText(self,text):
		text = re.sub('\[/?(?:CR|B|I|UPPERCASE|LOWERCASE)\](?i)','',text)
		text = re.sub('\[/?COLOR[^\]\[]*?\](?i)','',text)
		text = text.strip('[]')
		if text == '..': text = u'Parent Directory'
		return text
	
if __name__ == '__main__':
	if len(sys.argv) > 1 and sys.argv[1] == 'voice_dialog':
		backends.selectVoice()
	else:
		TTSService().start()
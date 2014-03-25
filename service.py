import sys, re, difflib, time, xbmc, xbmcgui
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
		self.enabled = True
		self.skinTable = skintables.getSkinTable()
		self.initState()
		self.tts = None
		self.backendProvider = None
		self.initTTS()
	
	def onAbortRequested(self):
		self.stop = True
		if self.tts: self.tts._close()
		
	def onSettingsChanged(self):
		self.tts._update()
		self.checkBackend()
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
		self.keyboardText = u''
		self.progressPercent = u''
		self.lastProgressPercentUnixtime = 0
		self.win = None
		
	def initTTS(self):
		provider = self.setBackend(backends.getBackend()())
		self.backendProvider = provider
		util.LOG('Backend: %s' % provider)
		
	def start(self):
		util.LOG('STARTED :: Interval: %sms' % self.tts.interval)
		try:
			while self.enabled and (not xbmc.abortRequested) and (not self.stop):
				xbmc.sleep(self.tts.interval)
				self.checkForText()
		except RuntimeError:
			util.ERROR('start()',hide_tb=True)
		finally:
			self.tts._close()
			util.LOG('STOPPED')
		
	def setBackend(self,backend):
		if self.tts: self.tts._close()
		self.tts = backend
		return backend.provider
		
	def checkBackend(self):
		provider = util.getSetting('backend',None)
		if provider == self.backendProvider: return
		self.initTTS()
		
	def checkForText(self):
		newW = self.checkWindow()
		newC = self.checkControl(newW)
		text = self.getControlText(self.controlID)
		if (text != self.text) or newC:
			self.newText(text,newC)
		else:
			if self.winID == 10103:
				self.checkVirtualKeyboard()
			elif self.winID == 10101:
				self.checkProgressDialog()
			
	def checkVirtualKeyboard(self):
		text = xbmc.getInfoLabel('Control.GetLabel(310)').decode('utf-8')
		if (text != self.keyboardText):
			out = ''
			d = difflib.Differ()
			if not text:
				out = u'No text'
			elif len(text) > len(self.keyboardText):
				for c in d.compare(self.keyboardText,text):
					if c.startswith('+'): out += u' ' + (c.strip(' +') or 'space')
			else:
				for c in d.compare(self.keyboardText,text):
					if c.startswith('-'): out += u' ' + (c.strip(' -') or 'space')
				if out: out = out.strip() + ' deleted'
			if out:
				self.sayText(out.strip(),interrupt=True)
			self.keyboardText = text
	
	def checkProgressDialog(self):
		progress = xbmc.getInfoLabel('System.Progressbar').decode('utf-8')
		if not progress or progress == self.progressPercent: return
		isSpeaking = self.tts.isSpeaking()
		if isSpeaking == None:
			now = time.time()
			if now - self.lastProgressPercentUnixtime < 2: return
			self.lastProgressPercentUnixtime = now
		elif isSpeaking:
			return
		self.progressPercent = progress
		self.sayText(u'%s%%' % progress,interrupt=True)
		
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
		self.tts.say(self.cleanText(text),interrupt)
		
	def sayTexts(self,texts,interrupt=True):
		if not texts: return
		self.tts.sayList(texts,interrupt=interrupt)
	
	def insertPause(self):
		self.tts.insertPause()
		
	def stopSpeech(self):
		self.tts._stop()
		
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
		self.insertPause()
		if heading:
			self.sayText(heading)
			self.insertPause()
		texts = guitables.getWindowTexts(winID)
		if texts:
			self.insertPause()
			for t in texts:
				self.sayText(t)
				self.insertPause()
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
			self.tts.insertPause()
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
		
	_formatTagRE = re.compile(r'\[/?(?:CR|B|I|UPPERCASE|LOWERCASE)\](?i)')
	_colorTagRE = re.compile(r'\[/?COLOR[^\]\[]*?\](?i)')
	_okTagRE = re.compile(r'(^|\W|\s)OK($|\s|\W)') #Prevents saying Oklahoma
	def cleanText(self,text):
		if text.endswith(')'): #Skip this most of the time
			text = text.replace('( )','{0} no'.format(self.tts.pauseInsert)).replace('(*)','{0} yes'.format(self.tts.pauseInsert)) #For boolean settings
		text = self._formatTagRE.sub('',text)
		text = self._colorTagRE.sub('',text)
		text = self._okTagRE.sub(r'\1O K\2', text) #Some speech engines say OK as Oklahoma
		text = text.strip('-[]') #getLabel() on lists wrapped in [] and some speech engines have problems with text starting with -
		text = text.replace('XBMC','X B M C')
		if text == '..': text = u'Parent Directory'
		return text
	
if __name__ == '__main__':
	if len(sys.argv) > 1 and sys.argv[1] == 'voice_dialog':
		backends.selectVoice()
	else:
		TTSService().start()

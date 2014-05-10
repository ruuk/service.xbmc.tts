import sys, re, xbmc, xbmcgui, time
from lib import backends
from lib import util
from lib import windows

util.LOG(util.xbmcaddon.Addon().getAddonInfo('version'))
util.LOG('Platform: {0}'.format(sys.platform))

util.initCommands()

class TTSService(xbmc.Monitor):
	def __init__(self):
		self.stop = False
		self.enabled = True
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
		self.reloadSettings()
		self.updateInterval()
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

	def reloadSettings(self):
		util.DEBUG = util.getSetting('debug_logging',True)
		self.speakListCount = util.getSetting('speak_list_count',True)
		self.autoItemExtra = util.getSetting('auto_item_extra',False)

#	def onNotification(self, sender, method, data):
#		util.LOG('NOTIFY: {0} :: {1} :: {2}'.format(sender,method,data))
		
	def initState(self):
		if not self.enabled or xbmc.abortRequested or self.stop: return
		self.winID = None
		self.windowReader = None
		self.controlID = None
		self.text = None
		self.textCompare = None
		self.secondaryText = None
		self.keyboardText = u''
		self.progressPercent = u''
		self.lastProgressPercentUnixtime = 0
		self.interval = 400
		self.listIndex = None
		self.waitingToReadItemExtra = None
		self.reloadSettings()
		
	def initTTS(self,backendClass=None):
		if not backendClass: backendClass = backends.getBackend()
		provider = self.setBackend(backendClass())
		self.backendProvider = provider
		self.updateInterval()
		util.LOG('Backend: %s' % provider)
		
	def fallbackTTS(self):
		backend = backends.getBackendFallback()
		util.LOG('Backend falling back to: {0}'.format(backend.provider))
		self.initTTS(backend)
		self.sayText(u'Notice... Speech engine falling back to {0}'.format(backend.displayName),interrupt=True)
	
	def start(self):
		util.LOG('SERVICE STARTED :: Interval: %sms' % self.tts.interval)
		try:
			while self.enabled and (not xbmc.abortRequested) and (not self.stop):
				xbmc.sleep(self.interval)
				try:
					self.checkForText()
				except RuntimeError:
					util.ERROR('start()',hide_tb=True)
				except: #Because we don't want to kill speech on an error
					util.ERROR('start()',notify=True)
					self.initState() #To help keep errors from repeating on the loop
		finally:
			self.tts._close()
			self.end()
			util.LOG('SERVICE STOPPED')
		
	def end(self):
		if util.DEBUG:
			xbmc.sleep(500) #Give threads a chance to finish
			import threading
			util.LOG('Remaining Threads:')
			for t in threading.enumerate():
				util.LOG('  {0}'.format(t.name))
			
	def updateInterval(self):
		if util.getSetting('override_poll_interval',False):
			self.interval = util.getSetting('poll_interval',self.tts.interval)
		else:
			self.interval = self.tts.interval

	def setBackend(self,backend):
		if self.tts: self.tts._close()
		self.tts = backend
		return backend.provider
		
	def checkBackend(self):
		provider = util.getSetting('backend',None)
		if provider == self.backendProvider: return
		self.initTTS()
		
	def checkForText(self):
		self.checkAutoRead()
		newW = self.checkWindow()
		newC = self.checkControl(newW)
		text, compare = self.windowReader.getControlText(self.controlID)
		secondary = self.windowReader.getSecondaryText()
		if (compare != self.textCompare) or newC:
			self.newText(compare,text,newC,secondary)
		elif secondary != self.secondaryText:
			self.newSecondaryText(secondary)
		else:
			monitored = self.windowReader.getMonitoredText(self.tts.isSpeaking())
			if monitored: self.sayText(monitored,interrupt=True)
		
	def checkAutoRead(self):
		if not self.waitingToReadItemExtra:
			return
		if self.tts.isSpeaking():
			self.waitingToReadItemExtra = time.time()
			return
		if time.time() - self.waitingToReadItemExtra > 2:
			self.waitingToReadItemExtra = None
			self.sayItemExtra(interrupt=False)

	def repeatText(self):
		self.winID = None
		self.controlID = None
		self.text = None
		self.checkForText()

	def sayExtra(self):
		texts = self.windowReader.getWindowExtraTexts()
		self.sayTexts(texts)

	def sayItemExtra(self,interrupt=True):
		texts = self.windowReader.getItemExtraTexts(self.controlID)
		self.sayTexts(texts,interrupt=interrupt)
			
	def sayText(self,text,interrupt=False):
		assert isinstance(text,unicode), "Not Unicode"
		if self.tts.dead: return self.fallbackTTS()
		self.tts.say(self.cleanText(text),interrupt)
		
	def sayTexts(self,texts,interrupt=True):
		if not texts: return
		assert all(isinstance(t,unicode) for t in texts), "Not Unicode"
		if self.tts.dead: return self.fallbackTTS()
		self.tts.sayList(texts,interrupt=interrupt)
	
	def insertPause(self,ms=500):
		self.tts.insertPause(ms=ms)
		
	def stopSpeech(self):
		self.tts._stop()
		
	def updateWindowReader(self):
		readerClass = windows.getWindowReader(self.winID)
		if self.windowReader and readerClass.ID == self.windowReader.ID:
			self.windowReader._reset(self.winID)
			return
		self.windowReader = readerClass(self.winID)
		
	def window(self):
		return xbmcgui.Window(self.winID)
		
	def checkWindow(self):
		winID = xbmcgui.getCurrentWindowId()
		dialogID = xbmcgui.getCurrentWindowDialogId()
		if dialogID != 9999: winID = dialogID
		if winID == self.winID: return False
		if util.DEBUG: util.LOG('WindowID: {0}'.format(winID))
		self.winID = winID
		self.updateWindowReader()
		name = self.windowReader.getName()
		heading = self.windowReader.getHeading()
		self.sayText(u'Window: {0}'.format(name),interrupt=True)
		self.insertPause()
		if heading:
			self.sayText(heading)
			self.insertPause()
		texts = self.windowReader.getWindowTexts()
		if texts:
			self.insertPause()
			for t in texts:
				self.sayText(t)
				self.insertPause()
		return True
		
	def checkControl(self,newW):
		if not self.winID: return newW
		controlID = self.window().getFocusId()
		if controlID == self.controlID: return newW
		if util.DEBUG:
			util.LOG('Control: %s' % controlID)
		self.controlID = controlID
		post = self.getControlPostfix()
		description = self.windowReader.getControlDescription(self.controlID) or ''
		if description or post:
			self.sayText(description + post,interrupt=not newW)
			self.tts.insertPause()
			return True
		return newW
			
	def newText(self,compare,text,newC,secondary=None):
		self.textCompare = compare
		label2 = xbmc.getInfoLabel('Container({0}).ListItem.Label2'.format(self.controlID)).decode('utf-8')
		seasEp = xbmc.getInfoLabel('Container({0}).ListItem.Property(SeasonEpisode)'.format(self.controlID)).decode('utf-8') or u''
		if label2 and seasEp:
				text = u'{0}: {1}: {2} '.format(label2, text,self.formatSeasonEp(seasEp))
		if secondary:
			self.secondaryText = secondary
			text += self.tts.pauseInsert + u' ' + secondary
		self.sayText(text,interrupt=not newC)
		if self.autoItemExtra:
			self.waitingToReadItemExtra = time.time()
		
	def getControlPostfix(self):
		if not self.speakListCount: return u''
		numItems = xbmc.getInfoLabel('Container({0}).NumItems'.format(self.controlID)).decode('utf-8')
		if numItems: return u'... {0} item{1}'.format(numItems,numItems != '1' and 's' or '')
		return u''
		
	def newSecondaryText(self, text):
		if not text: return
		self.secondaryText = text
		if text.endswith('%'): text = text.rsplit(u' ',1)[-1] #Get just the percent part, so we don't keep saying downloading
		if not self.tts.isSpeaking(): self.sayText(text,interrupt=True)
		
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

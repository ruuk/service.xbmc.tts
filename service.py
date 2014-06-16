import sys, re, xbmc, xbmcgui, time, Queue
from lib import util, addoninfo

__version__ = util.xbmcaddon.Addon().getAddonInfo('version')
util.LOG(__version__)
util.LOG('Platform: {0}'.format(sys.platform))

from lib import backends
from lib import windows
from lib.windows import playerstatus, notice

if backends.audio.PLAYSFX_HAS_USECACHED:
	util.LOG('playSFX() has useCached')
else:
	util.LOG('playSFX() does NOT have useCached')
	
util.initCommands()
addoninfo.initAddonsData()

class TTSClosedException(Exception): pass

class TTSService(xbmc.Monitor):
	def __init__(self):
		self.stop = False
		self.disable = False
		self.noticeQueue = Queue.Queue()
		self.initState()
		self._tts = None
		self.backendProvider = None
		util.stopSounds() #To kill sounds we may have started before an update
		util.playSound('on')
		self.playerStatus = playerstatus.PlayerStatus(10115).init()
		self.noticeDialog = notice.NoticeDialog(10107).init()
		self.initTTS()
		util.LOG('SERVICE STARTED :: Interval: %sms' % self.tts.interval)
	
	def onAbortRequested(self):
		self.stop = True
		try:
			self.tts._close()
		except TTSClosedException:
			pass
		
	@property
	def tts(self):
		if self._tts._closed: raise TTSClosedException()
		return self._tts

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
		elif command == 'VOL_UP':
			self.volumeUp()
		elif command == 'VOL_DOWN':
			self.volumeDown()
		elif command == 'STOP':
			self.stopSpeech()
		elif command == 'SHUTDOWN':
			self.shutdown()

	def reloadSettings(self):
		util.DEBUG = util.getSetting('debug_logging',True)
		self.speakListCount = util.getSetting('speak_list_count',True)
		self.autoItemExtra = False
		if util.getSetting('auto_item_extra',False):
			self.autoItemExtra = util.getSetting('auto_item_extra_delay',2)

	def onDatabaseScanStarted(self,database):
		util.LOG('DB SCAN STARTED: {0} - Notifying...'.format(database))
		self.queueNotice(u'{0} database scan started.'.format(database))
		
	def onDatabaseUpdated(self,database):
		util.LOG('DB SCAN UPDATED: {0} - Notifying...'.format(database))
		self.queueNotice(u'{0} database scan finished.'.format(database))
		
#	def onNotification(self, sender, method, data):
#		util.LOG('NOTIFY: {0} :: {1} :: {2}'.format(sender,method,data))
#		#xbmc :: VideoLibrary.OnUpdate :: {"item":{"id":1418,"type":"episode"}}		
		
	def queueNotice(self,text):
		assert isinstance(text,unicode), "Not Unicode"
		self.noticeQueue.put(text)

	def clearNoticeQueue(self):
		try:
			while not self.noticeQueue.empty():
				self.noticeQueue.get()
				self.noticeQueue.task_done()
		except Queue.Empty:
			return
		
	def checkNoticeQueue(self):
		if self.noticeQueue.empty(): return False
		while not self.noticeQueue.empty():
			text = self.noticeQueue.get()
			self.sayText(text)
			self.noticeQueue.task_done()
		return True
		
	def initState(self):
		if xbmc.abortRequested or self.stop: return
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
		
	def fallbackTTS(self,reason=None):
		backend = backends.getBackendFallback()
		util.LOG('Backend falling back to: {0}'.format(backend.provider))
		self.initTTS(backend)
		self.sayText(u'Notice... Speech engine falling back to {0}'.format(backend.displayName),interrupt=True)
		if reason: self.sayText(u'Reason: {0}'.format(reason),interrupt=False)
	
	def checkNewVersion(self):
		from distutils.version import StrictVersion
		lastVersion = util.getSetting('version','0.0.0')
		if StrictVersion(lastVersion) < StrictVersion(__version__):
			util.setSetting('version',__version__)
			self.queueNotice(u'New T T S Version... {0}'.format(__version__))
			return True
		return False
		
	def start(self):	
		self.checkNewVersion()
		try:
			while (not xbmc.abortRequested) and (not self.stop):
				xbmc.sleep(self.interval)
				try:
					self.checkForText()
				except RuntimeError:
					util.ERROR('start()',hide_tb=True)
				except SystemExit:
					if util.DEBUG:
						util.ERROR('SystemExit: Quitting')
					else:
						util.LOG('SystemExit: Quitting')
					break
				except TTSClosedException:
					util.LOG('TTSCLOSED')
				except: #Because we don't want to kill speech on an error
					util.ERROR('start()',notify=True)
					self.initState() #To help keep errors from repeating on the loop
		finally:
			self._tts._close()
			self.end()
			util.playSound('off')
			util.LOG('SERVICE STOPPED')
			if self.disable:
				import enabler
				enabler.disableAddon()
		
	def end(self):
		if util.DEBUG:
			xbmc.sleep(500) #Give threads a chance to finish
			import threading
			util.LOG('Remaining Threads:')
			for t in threading.enumerate():
				util.LOG('  {0}'.format(t.name))
			
	def shutdown(self):
		self.stop = True
		self.disable = True
		
	def updateInterval(self):
		if util.getSetting('override_poll_interval',False):
			self.interval = util.getSetting('poll_interval',self.tts.interval)
		else:
			self.interval = self.tts.interval

	def setBackend(self,backend):
		if self._tts: self._tts._close()
		self._tts = backend
		return backend.provider
		
	def checkBackend(self):
		provider = util.getSetting('backend',None)
		if provider == self.backendProvider: return
		self.initTTS()
		
	def checkForText(self):
		self.checkAutoRead()
		newN = self.checkNoticeQueue()
		newW = self.checkWindow(newN)
		newC = self.checkControl(newW)
		newD = newC and self.checkControlDescription(newW) or False
		text, compare = self.windowReader.getControlText(self.controlID)
		secondary = self.windowReader.getSecondaryText()
		if (compare != self.textCompare) or newC:
			self.newText(compare,text,newD,secondary)
		elif secondary != self.secondaryText:
			self.newSecondaryText(secondary)
		else:
			self.checkMonitored()
		
	def checkMonitored(self):
		monitored = None
		if self.playerStatus.visible():
			monitored = self.playerStatus.getMonitoredText(self.tts.isSpeaking())
		if self.noticeDialog.visible():
			monitored = self.noticeDialog.getMonitoredText(self.tts.isSpeaking())
		if not monitored: monitored = self.windowReader.getMonitoredText(self.tts.isSpeaking())
		if monitored:
			if isinstance(monitored,basestring):
				self.sayText(monitored,interrupt=True)
			else:
				self.sayTexts(monitored,interrupt=True)

	def checkAutoRead(self):
		if not self.waitingToReadItemExtra:
			return
		if self.tts.isSpeaking():
			self.waitingToReadItemExtra = time.time()
			return
		if time.time() - self.waitingToReadItemExtra > self.autoItemExtra:
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
		if self.tts.dead: return self.fallbackTTS(self.tts.deadReason)
		self.tts.say(self.cleanText(text),interrupt)
		
	def sayTexts(self,texts,interrupt=True):
		if not texts: return
		assert all(isinstance(t,unicode) for t in texts), "Not Unicode"
		if self.tts.dead: return self.fallbackTTS(self.tts.deadReason)
		self.tts.sayList(self.cleanText(texts),interrupt=interrupt)

	def insertPause(self,ms=500):
		self.tts.insertPause(ms=ms)
		
	def volumeUp(self):
		msg = self.tts.volumeUp()
		if not msg: return
		self.sayText(msg,interrupt=True)

	def volumeDown(self):
		msg = self.tts.volumeDown()
		if not msg: return
		self.sayText(msg,interrupt=True)

	def stopSpeech(self):
		self.tts._stop()
		
	def updateWindowReader(self):
		readerClass = windows.getWindowReader(self.winID)
		if self.windowReader:
			self.windowReader.close()
			if readerClass.ID == self.windowReader.ID:
				self.windowReader._reset(self.winID)
				return
		self.windowReader = readerClass(self.winID,self)
		
	def window(self):
		return xbmcgui.Window(self.winID)
		
	def checkWindow(self,newN):
		winID = xbmcgui.getCurrentWindowId()
		dialogID = xbmcgui.getCurrentWindowDialogId()
		if dialogID != 9999: winID = dialogID
		if winID == self.winID: return newN
		self.winID = winID
		self.updateWindowReader()
		if util.DEBUG: util.LOG('Window ID: {0} Handler: {1}'.format(winID,self.windowReader.ID))
		name = self.windowReader.getName()
		heading = self.windowReader.getHeading()
		self.sayText(u'Window: {0}'.format(name),interrupt=not newN)
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
		if not controlID: return newW
		return True
		
	def checkControlDescription(self,newW):
		post = self.getControlPostfix()
		description = self.windowReader.getControlDescription(self.controlID) or ''
		if description or post:
			self.sayText(description + post,interrupt=not newW)
			self.tts.insertPause()
			return True
		return newW
			
	def newText(self,compare,text,newD,secondary=None):
		self.textCompare = compare
		label2 = xbmc.getInfoLabel('Container({0}).ListItem.Label2'.format(self.controlID)).decode('utf-8')
		seasEp = xbmc.getInfoLabel('Container({0}).ListItem.Property(SeasonEpisode)'.format(self.controlID)).decode('utf-8') or u''
		if label2 and seasEp:
				text = u'{0}: {1}: {2} '.format(label2, text,self.formatSeasonEp(seasEp))
		if secondary:
			self.secondaryText = secondary
			text += self.tts.pauseInsert + u' ' + secondary
		self.sayText(text,interrupt=not newD)
		if self.autoItemExtra:
			self.waitingToReadItemExtra = time.time()
		
	def getControlPostfix(self):
		if not self.speakListCount: return u''
		numItems = xbmc.getInfoLabel('Container({0}).NumItems'.format(self.controlID)).decode('utf-8')
		if numItems: return u'... {0} item{1}'.format(numItems,numItems != '1' and 's' or '')
		return u''
		
	def newSecondaryText(self, text):
		self.secondaryText = text
		if not text: return
		if text.endswith('%'): text = text.rsplit(u' ',1)[-1] #Get just the percent part, so we don't keep saying downloading
		if not self.tts.isSpeaking(): self.sayText(text,interrupt=True)
		
	def formatSeasonEp(self,seasEp):
		if not seasEp: return u''
		return seasEp.replace(u'S',u'season ').replace(u'E',u'episode ')

	_formatTagRE = re.compile(r'\[/?(?:CR|B|I|UPPERCASE|LOWERCASE)\](?i)')
	_colorTagRE = re.compile(r'\[/?COLOR[^\]\[]*?\](?i)')
	_okTagRE = re.compile(r'(^|\W|\s)OK($|\s|\W)') #Prevents saying Oklahoma
	def _cleanText(self,text):
		text = self._formatTagRE.sub('',text)
		text = self._colorTagRE.sub('',text)
		text = self._okTagRE.sub(r'\1O K\2', text) #Some speech engines say OK as Oklahoma
		text = text.strip('-[]') #getLabel() on lists wrapped in [] and some speech engines have problems with text starting with -
		text = text.replace('XBMC','X B M C')
		if text == '..': text = u'Parent Directory'
		return text

	def cleanText(self,text):
		if isinstance(text,basestring):
			return self._cleanText(text)
		else:
			return [self._cleanText(t) for t in text]
		
	
if __name__ == '__main__':
	if len(sys.argv) > 1 and sys.argv[1] == 'voice_dialog':
		backends.selectVoice()
	else:
		TTSService().start()

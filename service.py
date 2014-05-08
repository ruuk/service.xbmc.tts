import sys, re, difflib, time, xbmc, xbmcgui
from lib import guitables
from lib import skintables
from lib import windowparser
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
		util.DEBUG = util.getSetting('debug_logging',True)
		self.speakListCount = util.getSetting('speak_list_count',True)
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

#	def onNotification(self, sender, method, data):
#		util.LOG('NOTIFY: {0} :: {1} :: {2}'.format(sender,method,data))
		
	def initState(self):
		self.winID = None
		self.controlID = None
		self.text = None
		self.textCompare = None
		self.secondaryText = None
		self.keyboardText = u''
		self.progressPercent = u''
		self.lastProgressPercentUnixtime = 0
		self.interval = 400
		self.win = None
		self.listIndex = None
		self.speakListCount = util.getSetting('speak_list_count',True)
		
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
					self.initState() #To help keep errors repeating on the loop
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
		newW = self.checkWindow()
		newC = self.checkControl(newW)
		text, compare = self.getControlText(self.controlID)
		secondary = guitables.getListItemProperty(self.winID)
		if (compare != self.textCompare) or newC:
			self.newText(compare,text,newC,secondary)
		elif secondary != self.secondaryText:
			self.newSecondaryText(secondary)
		else:
			if self.winID == 10103:
				self.checkVirtualKeyboard(310)
			elif self.winID == 10109:
				self.checkVirtualKeyboard(4)
			elif self.winID == 10101:
				self.checkProgressDialog()
			
	ip_re = re.compile('^[\d ]{3}\.[\d ]{3}\.[\d ]{3}.[\d ]{3}$')
	def checkVirtualKeyboard(self,edit_id):
		text = xbmc.getInfoLabel('Control.GetLabel({0})'.format(edit_id)).decode('utf-8')
		if (text != self.keyboardText):
			out = ''
			d = difflib.Differ()
			if not text:
				out = u'No text'
			elif len(text) > len(self.keyboardText):
				for c in d.compare(self.keyboardText,text):
					if c.startswith('+'):
						out += u' ' + (c.strip(' +') or 'space')
			elif len(text) == len(self.keyboardText):
				if len(text) == 15 and self.ip_re.match(text) and self.ip_re.match(self.keyboardText): #IP Address
					oldip = self.keyboardText.replace(' ','').split('.')
					newip = text.replace(' ','').split('.')
					for old,new in zip(oldip,newip):
						if old == new: continue
						out = ' '.join(list(new))
						break
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
		if not texts: texts = windowparser.getWindowParser().getWindowTexts()
		self.sayTexts(texts)

	def sayItemExtra(self):
		text = guitables.getItemExtraTexts(self.winID)
		if not text: text = xbmc.getInfoLabel('ListItem.Plot').decode('utf-8')
		if not text: text = xbmc.getInfoLabel('Container.ShowPlot').decode('utf-8')
		if not text: text = xbmc.getInfoLabel('ListItem.Property(Artist_Description)').decode('utf-8')
		if not text: text = xbmc.getInfoLabel('ListItem.Property(Album_Description)').decode('utf-8')
		if not text: text = xbmc.getInfoLabel('ListItem.Property(Addon.Description)').decode('utf-8')
		if not text: text = guitables.getSongInfo()
		if not text: text = windowparser.getWindowParser().getListItemTexts(self.controlID)
		if not text: return
		if not isinstance(text,list): text = [text]
		self.sayTexts(text)
			
	def sayText(self,text,interrupt=False):
		assert isinstance(text,unicode), "Not Unicode"
		if self.tts.dead: return self.fallbackTTS()
		self.tts.say(self.cleanText(text),interrupt)
		
	def sayTexts(self,texts,interrupt=True):
		if not texts: return
		if self.tts.dead: return self.fallbackTTS()
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
		if not self.win: return newW
		controlID = self.win.getFocusId()
		if controlID == self.controlID: return newW
		if util.DEBUG:
			util.LOG('Control: %s' % controlID)
		self.controlID = controlID
		post = self.getControlPostfix()
		text = skintables.getControlText(self.skinTable,self.winID,self.controlID) or u''
		if text or post:
			self.sayText(text + post,interrupt=not newW)
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
		
	def getControlText(self,controlID):
		if not controlID: return (u'',u'')
		text = xbmc.getInfoLabel('ListItem.Title')
		if not text: text = xbmc.getInfoLabel('Container({0}).ListItem.Label'.format(controlID))
		if not text: text = xbmc.getInfoLabel('Control.GetLabel({0})'.format(controlID))
		if not text: text = xbmc.getInfoLabel('System.CurrentControl')
		if not text: return (u'',u'')
		compare = text + xbmc.getInfoLabel('ListItem.StartTime'.format(controlID)) + xbmc.getInfoLabel('ListItem.EndTime'.format(controlID))
		return (text.decode('utf-8'),compare)
		
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

import re, sys, xbmc, xbmcgui, subprocess
import guitables
import skintables

DEBUG = False
def ERROR(txt):
	if isinstance (txt,str): txt = txt.decode("utf-8")
	LOG('ERROR: ' + txt)
	short = str(sys.exc_info()[1])
	import traceback
	traceback.print_exc()
	return short
	
def LOG(message):
	message = 'service.xbmc.tts: ' + message
	xbmc.log(msg=message.encode("utf-8"), level=xbmc.LOGNOTICE)

class WindowWrapper(xbmcgui.Window):
	def onAction(self,action):
		LOG('BC: {0} AID: {1}'.format(action.getButtonCode(),action.getId()))
		xbmcgui.Window.onAction(self,action)

class TTSBackendBase:
	provider = None
	def say(self,text): raise Exception('Not Implemented')

	def close(self): pass

class LoggOnlyTTSBackend(TTSBackendBase):
	def say(self,text):
		print 'TTS: ' + repr(text)
		
class FestivalTTSBackend(TTSBackendBase):
	def __init__(self):
		self.startFesticalProcess()
		
	def startFesticalProcess(self):
		#LOG('Starting Festival...')
		#self.festivalProcess = subprocess.Popen(['festival'],shell=True,stdin=subprocess.PIPE)
		pass
		
	def say(self,text):
		if not text: return
		##self.festivalProcess.send_signal(signal.SIGINT)
		#self.festivalProcess = subprocess.Popen(['festival'],shell=True,stdin=subprocess.PIPE)
		self.festivalProcess = subprocess.Popen(['festival','--pipe'],shell=True,stdin=subprocess.PIPE)
		self.festivalProcess.communicate('(SayText "{0}")\n'.format(text))
		#if self.festivalProcess.poll() != None: self.startFesticalProcess()
		
	def close(self):
		#if self.festivalProcess.poll() != None: return
		#self.festivalProcess.terminate()
		pass

class Pico2WaveTTSBackend(TTSBackendBase):
	def __init__(self):
		import xbmcaddon
		import os
		profile = xbmc.translatePath(xbmcaddon.Addon().getAddonInfo('profile'))
		if not os.path.exists(profile): os.makedirs(profile)
		self.outFile = os.path.join(profile,'speech.wav')
		LOG('pico2wave output file: ' + self.outFile)
		
	def say(self,text):
		if not text: return
		subprocess.call(['pico2wave', '-w', '{0}'.format(self.outFile), '{0}'.format(text)])
		#xbmc.playSFX(self.outFile) #Doesn't work - caches wav
		subprocess.call(['aplay','{0}'.format(self.outFile)])
		
class WindowsInternalTTSBackend(TTSBackendBase):
	def __init__(self):
		import xbmcaddon
		import os
		profile = xbmc.translatePath(xbmcaddon.Addon().getAddonInfo('profile'))
		if not os.path.exists(profile): os.makedirs(profile)
		self.vbsFile = os.path.join(profile,'witts.vbs')
		LOG('Windows Internal VBS file: ' + self.outFile)
		self.vbs =		'speech = Wscript.CreateObject("SAPI.spVoice")'
		self.vbs +=	'speech.speak "{0}"'
		
	def say(self,text):
		if not text: return
		with open(self.vbsFile,'w') as f: f.write(self.vbs.format(text))
		subprocess.call([self.vbsFile])
		
class TTSService:
	def __init__(self):
		self.stop = False
		self.wait = 400
		self.enabled = True
		self.skinTable = skintables.getSkinTable()
		self.initState()
		self.tts = WindowsInternalTTSBackend()
		
	def initState(self):
		self.winID = None
		self.controlID = None
		self.text = None
		self.win = None
		
	def start(self):
		LOG('STARTED :: Enabled: %s :: Interval: %sms' % (self.enabled,self.wait))
		if not self.enabled: return
		try:
			while self.enabled and (not xbmc.abortRequested) and (not self.stop):
				xbmc.sleep(self.wait)
				self.checkForText()
		finally:
			self.tts.close()
			LOG('STOPPED')
		
	def checkForText(self):
		winID = xbmcgui.getCurrentWindowId()
		dialogID = xbmcgui.getCurrentWindowDialogId()
		if dialogID != 9999: winID = dialogID
		if winID != self.winID: self.newWindow(winID)
		controlID = self.win.getFocusId()
		newc = False
		if controlID != self.controlID:
			newc = True
			self.newControl(controlID)
		text = self.getControlText(self.controlID)
		if text != self.text or newc: self.newText(text)
	
	def sayText(self,text):
		self.tts.say(text)
		
	def newWindow(self,winID):
		self.winID = winID
		del self.win
		self.win = WindowWrapper(winID)
		name = xbmc.getInfoLabel('System.CurrentWindow') or guitables.winNames.get(winID) or 'unknown'
		self.tts.say('Window: ' + name)
		
	def newControl(self,controlID):
		LOG('Control: %s' % controlID)
		self.controlID = controlID
		if self.skinTable and self.winID in self.skinTable:
			if self.controlID in self.skinTable[self.winID]:
				if 'prefix' in self.skinTable[self.winID][self.controlID]:
					self.sayText('{0}: {1}'.format(self.skinTable[self.winID][self.controlID]['prefix'],self.skinTable[self.winID][self.controlID]['name']))
				else:
					self.sayText(self.skinTable[self.winID][self.controlID]['name'])
		
	def newText(self,text):
		self.text = text
		label2 = xbmc.getInfoLabel('Container({0}).ListItem.Label2'.format(self.controlID))
		seasEp = xbmc.getInfoLabel('Container({0}).ListItem.Property(SeasonEpisode)'.format(self.controlID)) or ''
		if label2:
			if seasEp:
				text = '{0}: {1}: {2} '.format(label2, text,self.formatSeasonEp(seasEp))
#			else:
#				text = '{0}: {1} '.format(text, label2)
		self.sayText(text)
		
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
	TTSService().start()
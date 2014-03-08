import re, sys, xbmc, xbmcgui, subprocess

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

WIN_NAMES = {	10000: 'home',
				10001: 'programs',
				10002: 'pictures',
				10003: 'file manager',
				10004: 'settings',
				10005: 'music',
				10006: 'video',
				10007: 'system info',
				10011: 'screen calibration',
				10012: 'pictures settings',
				10013: 'programs settings',
				10014: 'weather settings',
				10015: 'music settings',
				10016: 'system settings',
				10017: 'videos settings',
				10018: 'network settings',
				10018: 'service settings',
				10019: 'appearance settings',
				10020: 'scripts',
				10024: 'video files',
				10025: 'video library',
				10028: 'video playlist',
				10029: 'login screen',
				10034: 'profiles',
				10040: 'addon browser',
				10100: 'yes/no dialog',
				10101: 'progress dialog',
				10103: 'virtual keyboard',
				10104: 'volume bar',
				10106: 'context menu',
				10107: 'info dialog',
				10109: 'numeric input',
				10111: 'shutdown menu',
				10112: 'music scan',
				10113: 'mute bug',
				10114: 'player controls',
				10115: 'seek bar',
				10120: 'music OSD',
				10122: 'visualisation preset list',
				10123: 'OSD video settings',
				10124: 'OSD audio settings',
				10125: 'video bookmarks',
				10126: 'file browser',
				10128: 'network setup',
				10129: 'media source',
				10130: 'profile settings',
				10131: 'lock settings',
				10132: 'content settings',
				10133: 'video scan',
				10134: 'favourites',
				10135: 'song information',
				10136: 'smart playlist editor',
				10137: 'smart playlist rule',
				10138: 'busy dialog',
				10139: 'picture info',
				10140: 'addon settings',
				10141: 'access points',
				10142: 'fullscreen info',
				10143: 'karaoke selector',
				10144: 'karaoke large selector',
				10145: 'slider dialog',
				10146: 'addon information',
				10147: 'text viewer',
				10149: 'peripherals',
				10150: 'peripheral settings',
				10151: 'extended progress dialog',
				10152: 'media filter',
				10500: 'music playlist',
				10501: 'music files',
				10502: 'music library',
				10503: 'music playlist editor',
				10601: 'pvr',
				10602: 'pvr guide info',
				10603: 'pvr recording info',
				10604: 'pvr timer setting',
				10605: 'pvr group manager',
				10606: 'pvr channel manager',
				10607: 'pvr guide search',
				10610: 'pvr OSD channels',
				10611: 'pvr OSD guide',
				11000: 'virtual keyboard',
				12000: 'select dialog',
				12001: 'music information',
				12002: 'OK dialog',
				12003: 'movie information',
				12005: 'fullscreen video',
				12006: 'visualisation',
				12007: 'slideshow',
				12008: 'file stacking dialog',
				12009: 'karaoke',
				12600: 'weather',
				12900: 'screensaver',
				12901: 'video OSD',
				12902: 'video menu',
				12999: 'startup'
}

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
		subprocess.call(['aplay','{0}'.format(self.outFile)])
		
class TTSService:
	def __init__(self):
		self.stop = False
		self.wait = 400
		self.enabled = True
		self.initState()
		self.tts = FestivalTTSBackend()
		
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
		self.win = xbmcgui.Window(winID)
		name = xbmc.getInfoLabel('System.CurrentWindow') or WIN_NAMES.get(winID) or 'unknown'
		self.tts.say('New Window: ' + name)
		
	def newControl(self,controlID):
		LOG('Control: %s' % controlID)
		self.controlID = controlID
		
	def newText(self,text):
		self.text = text
		self.sayText(self.text)
		
	def getControlText(self,controlID):
		if not controlID: return ''
		text = xbmc.getInfoLabel('Control.GetLabel({0})'.format(controlID))
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
		
	def formatText(self,text):
		text = re.sub('\[/?[^\[\]]+\]','',text)
		text = text.strip('[]')
		if text == '..': text = 'Parent Directory'
		return text
	
if __name__ == '__main__':
	TTSService().start()
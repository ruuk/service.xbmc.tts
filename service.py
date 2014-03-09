import re, xbmc, xbmcgui
from lib import guitables
from lib import skintables
from lib import tts

from lib import util

class TTSService:
	def __init__(self):
		self.stop = False
		self.wait = 400
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
		self.tts = tts.getBackend()

	def start(self):
		util.LOG('STARTED :: Enabled: %s :: Interval: %sms' % (self.enabled,self.wait))
		if not self.enabled: return
		try:
			while self.enabled and (not xbmc.abortRequested) and (not self.stop):
				xbmc.sleep(self.wait)
				self.checkForText()
		finally:
			self.tts.close()
			util.LOG('STOPPED')
		
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
		self.win = xbmcgui.Window(winID)
		name = guitables.winNames.get(winID) or xbmc.getInfoLabel('System.CurrentWindow') or 'unknown'
		self.tts.say('Window: {0}'.format(name))
		self.tts.pause()
		
	def newControl(self,controlID):
		if util.DEBUG: util.LOG('Control: %s' % controlID)
		self.controlID = controlID
		if self.skinTable and self.winID in self.skinTable:
			if self.controlID in self.skinTable[self.winID]:
				if 'prefix' in self.skinTable[self.winID][self.controlID]:
					self.sayText('{0}: {1}'.format(self.skinTable[self.winID][self.controlID]['prefix'],self.skinTable[self.winID][self.controlID]['name']))
				else:
					self.sayText(self.skinTable[self.winID][self.controlID]['name'])
				self.tts.pause()
		
	def newText(self,text):
		self.text = text
		label2 = xbmc.getInfoLabel('Container({0}).ListItem.Label2'.format(self.controlID))
		seasEp = xbmc.getInfoLabel('Container({0}).ListItem.Property(SeasonEpisode)'.format(self.controlID)) or ''
		if label2:
			if seasEp:
				text = '{0}: {1}: {2} '.format(label2, text,self.formatSeasonEp(seasEp))
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
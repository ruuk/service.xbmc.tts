#TODO: NOT WORKING AND NOT USED CURRENTLY

# -*- coding: utf-8 -*-
#from base import WindowReaderBase
import xbmcgui

class NoticeDialog():
	ID = 'notice'
	
	def init(self):
		self.notices = []
		self.lastHeading = '' #401
		self.lastMessage = '' #402
		self.setWindow()
		return self
		
	def setWindow(self):
		self.win = xbmcgui.Window(10107)

	def addNotice(self,heading,message):
		if heading == self.lastHeading and message == self.lastMessage: return False
		self.lastHeading = heading
		self.lastMessage = message
		self.notices.append((heading,message))
		return True

	def takeNoticesForSpeech(self):
		print 'y'
		if not self.notices: return None
		ret = []
		for n in self.notices:
			ret.append('Notice: {0}... {1}'.format(n[0],n[1]))
		self.init()
		print ret
		return ret
	
	def getMonitoredText(self,isSpeaking=False): #getLabel() Doesn't work currently with FadeLabels
		print 'x'
		heading = self.win.getControl(401).getLabel()
		message = self.win.getControl(402).getLabel()
		print repr(message)
		self.addNotice(heading,message)
		if not isSpeaking: return self.takeNoticesForSpeech()	
		return None
		
#class NoticeDialogReader(NoticeDialog,WindowReaderBase): pass
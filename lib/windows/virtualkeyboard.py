# -*- coding: utf-8 -*-
import xbmc, re, difflib
from base import WindowReaderBase

class VirtualKeyboardReader(WindowReaderBase):
	ID = 'virtualkeyboard'
	ip_re = re.compile('^[\d ]{3}\.[\d ]{3}\.[\d ]{3}.[\d ]{3}$')
		
	def init(self):
		self.editID = None
		if self.winID == 10103:
			self.editID = 310
		elif self.winID == 10109:
			self.editID = 4
		self.keyboardText = ''
			
	def getHeading(self): xbmc.getInfoLabel('Control.GetLabel(311)'.decode('utf-8'))
	
	def getMonitoredText(self,isSpeaking=False):
		text = xbmc.getInfoLabel('Control.GetLabel({0})'.format(self.editID)).decode('utf-8')
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
			self.keyboardText = text
			if out:
				return out.strip()
		return None
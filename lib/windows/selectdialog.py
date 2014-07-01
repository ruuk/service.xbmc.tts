# -*- coding: utf-8 -*-
import xbmc
from base import WindowReaderBase, CURRENT_SKIN

class SelectDialogReader(WindowReaderBase):
	ID = 'selectdialog'

	def getHeading(self):
		if CURRENT_SKIN == 'confluence': return None #Broken for Confluence
		return WindowReaderBase.getHeading(self)

	def getControlText(self,controlID):
		text = xbmc.getInfoLabel('System.CurrentControl').decode('utf-8')
		return (text,text)
	
	def getWindowExtraTexts(self):
		return None
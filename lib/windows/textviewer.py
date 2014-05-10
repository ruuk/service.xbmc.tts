# -*- coding: utf-8 -*-
from base import WindowReaderBase

class TextViewerReader(WindowReaderBase):
	ID = 'textviewer'

	def getWindowTexts(self): return self.getWindowExtraTexts()
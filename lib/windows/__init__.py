# -*- coding: utf-8 -*-
from base import DefaultWindowReader
from progressdialog import ProgressDialogReader
from virtualkeyboard import VirtualKeyboardReader
from pvrguideinfo import PVRGuideInfoReader

READERS = {	10101:ProgressDialogReader,
				10103:VirtualKeyboardReader,
				10109:VirtualKeyboardReader,
				10602:PVRGuideInfoReader}
			
def getWindowReader(winID):
	return READERS.get(winID,DefaultWindowReader)
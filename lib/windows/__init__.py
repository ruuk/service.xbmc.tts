# -*- coding: utf-8 -*-
from base import DefaultWindowReader
from progressdialog import ProgressDialogReader
from virtualkeyboard import VirtualKeyboardReader
from pvrguideinfo import PVRGuideInfoReader
from textviewer import TextViewerReader
from busydialog import BusyDialogReader

READERS = {	10101:ProgressDialogReader,
				10103:VirtualKeyboardReader,
				10109:VirtualKeyboardReader,
				10138:BusyDialogReader,
				10147:TextViewerReader,
				10602:PVRGuideInfoReader}
			
def getWindowReader(winID):
	return READERS.get(winID,DefaultWindowReader)
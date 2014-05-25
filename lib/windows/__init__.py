# -*- coding: utf-8 -*-
from base import DefaultWindowReader
from progressdialog import ProgressDialogReader
from virtualkeyboard import VirtualKeyboardReader
from pvrguideinfo import PVRGuideInfoReader
from textviewer import TextViewerReader
from busydialog import BusyDialogReader
from contextmenu import ContextMenuReader
from pvr import PVRWindowReader

READERS = {	10101:ProgressDialogReader,
				10103:VirtualKeyboardReader,
				10106:ContextMenuReader,
				10109:VirtualKeyboardReader,
				10138:BusyDialogReader,
				10147:TextViewerReader,
				10601:PVRWindowReader,
				10602:PVRGuideInfoReader}
			
def getWindowReader(winID):
	return READERS.get(winID,DefaultWindowReader)
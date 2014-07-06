# -*- coding: utf-8 -*-
import xbmc

BASE_COMMAND = 'XBMC.NotifyAll(service.xbmc.tts,SAY,"{{\\"text\\":\\"{0}\\",\\"interrupt\\":{1}}}")'

def sayText(text,interrupt=False):
	command = BASE_COMMAND.format(text,repr(interrupt).lower())
	#print command
	xbmc.executebuiltin(command)

def stop():
	xbmc.executebuiltin('XBMC.NotifyAll(service.xbmc.tts,STOP)')

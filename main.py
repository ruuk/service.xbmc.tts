# -*- coding: utf-8 -*-
import sys

if __name__ == '__main__':
	arg = None
	if len(sys.argv) > 1: arg = sys.argv[1] or False
	if arg and arg.startswith('key.'):
		command = arg[4:]
		from lib import util
		util.sendCommand(command)
	elif arg and arg.startswith('voice_dialog.'):
		provider = arg[13:]
		from lib import util
		util.selectVoice(provider)
	elif arg and arg.startswith('language_dialog.'):
		provider = arg[16:]
		from lib import util
		util.selectLanguage(provider)
	elif arg and arg.startswith('settings_dialog.'):
		provider = arg[16:]
		from lib import util
		setting = sys.argv[2]
		util.selectSetting(provider,setting)
	elif arg and arg.startswith('player_dialog.'):
		provider = arg[14:]
		from lib import util
		util.selectPlayer(provider)
	elif arg == 'backend_dialog':
		from lib import util
		util.selectBackend()
	elif arg == 'install_keymap':
		from lib import util
		util.installKeymap()
	elif arg == 'settings': #No longer used, using XBMC.Addon.OpenSettings(service.xbmc.tts) in keymap instead
		from lib import util
		util.xbmcaddon.Addon().openSettings()
	elif arg == None:
		from service import TTSService
		TTSService().start()
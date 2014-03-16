# -*- coding: utf-8 -*-
import sys

if __name__ == '__main__':
	arg = None
	if len(sys.argv) > 1: arg = sys.argv[1] or False
	if arg and arg.startswith('key.'):
		command = arg[4:]
		from lib import util
		util.sendCommand(command)
	elif arg == 'voice_dialog':
		from lib import backends
		backends.selectVoice()
	elif arg == 'install_keymap':
		from lib import util
		util.installKeymap()
	elif arg == None:
		from service import TTSService
		TTSService().start()
# -*- coding: utf-8 -*-
import sys

if __name__ == '__main__':
	command = None
	if len(sys.argv) > 1: command = sys.argv[1] or False
	if command == 'voice_dialog':
		from lib import backends
		backends.selectVoice()
	elif command == 'repeat_text':
		from lib import util
		util.sendCommand('REPEAT')
	elif command == 'extra_text':
		from lib import util
		util.sendCommand('EXTRA')
	elif command == 'install_keymap':
		from lib import util
		util.installKeymap()
	elif command == None:
		from service import TTSService
		TTSService().start()
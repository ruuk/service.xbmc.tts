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
		from lib import backends
		backends.selectVoice(provider)
	elif arg == 'backend_dialog':
		#<setting id="default_tts" type="enum" label="Default TTS Engine" values="Auto|SAPI|Pico2Wave|Festival|Flite|eSpeak|OSX say|NVDA|Speech dispatcher|Flite (ATV2)|Log" default="0" />
		from lib import util
		util.selectBackend()
	elif arg == 'install_keymap':
		from lib import util
		util.installKeymap()
	elif arg == None:
		from service import TTSService
		TTSService().start()
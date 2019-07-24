#!/usr/bin/python3

from phue import Bridge, Group
import threading
import random
import time, datetime
import skywriter
import signal
from queue import Queue
from collections import deque
import requests
import json
import random
import pychromecast

b = Bridge('10.0.0.80')
b.connect() #Comment out after first run
url = "http://10.0.0.34:8080/post/"
# group = Group(b, "Living room")
group = Group(b, "Office")
lights = group.lights
mode = None
mode_state = {}
media_controller = None

def pushed_up(event):
	print("PUSHED UP")
	for l in lights:
		l.on = (not l.on)

def pushed_right(event):
	val = 3000
	current_hue = int((lights[0].hue+val) % 65535 )
	command = {
		"hue": current_hue,
		"sat": 126
	}
	for l in lights:
		b.set_light(l.light_id, command)

def pushed_down(event):
	print("PUSHED DOWN")

def pushed_left(event):
	val = 3000
	current_hue = int(((lights[0].hue-val)+65535)%65535)
	command = {
		"hue": current_hue,
		"sat": 126
	}
	for l in lights:
		b.set_light(l.light_id, command)

def single_lightning(sound=False):
	print("single_lightning - sound={}".format(sound))
	start_state = {
		"hue": lights[0].hue,
		"saturation": lights[0].saturation,
		"brightness":lights[0].brightness,
		"on": lights[0].on
	}
	# Fade "moonlight"
	group.on = True
	group.transitiontime = 2
	group.brightness = 1
	group.hue = 45000
	group.saturation = 100
	time.sleep(4)
	if(sound): thunder_noise()
	light = lights[random.randint(0, len(lights)-1)]
	light.transitiontime = 0.01
	light.saturation = 100
	light.brightness = 255
	time.sleep(0.05+random.random()*0.1)
	light.brightness = 1
	light.saturation = 100
	group.transitiontime = 2
	time.sleep(2)
	group.hue = start_state["hue"]
	group.saturation = start_state["saturation"]
	group.brightness = start_state["brightness"]
	group.on = start_state["on"]

def double_lightning(sound=False):
	print("double_lightning - sound={}".format(sound))
	start_state = {
		"hue": lights[0].hue,
		"saturation": lights[0].saturation,
		"brightness":lights[0].brightness,
		"on": lights[0].on
	}
	# Fade "moonlight"
	group.on = True
	group.transitiontime = 4
	group.brightness = 1
	group.hue = 45000
	group.saturation = 100
	time.sleep(4)
	if(sound): thunder_noise()
	light = lights[random.randint(0, len(lights)-1)]
	light.transitiontime = 0.01
	light.saturation = 100
	light.brightness = 255
	time.sleep(0.05+random.random()*0.1)
	light.brightness = 1
	light.saturation = 100
	light = lights[random.randint(0, len(lights)-1)]
	light.transitiontime = 0.01
	light.saturation = 100
	light.brightness = 200
	time.sleep(0.05+random.random()*0.1)
	light.brightness = 1
	light.saturation = 100
	group.transitiontime = 2
	time.sleep(2)
	group.hue = start_state["hue"]
	group.saturation = start_state["saturation"]
	group.brightness = start_state["brightness"]
	group.on = start_state["on"]

def toggle_mode_lightning():
	global mode
	if(mode!=None):
		mode=None
	else:
		mode="Lightning"
	print("Set mode to {}".format(mode))

def toggle_mode_magic_missile():
	global mode
	global mode_state
	if(mode!=None):
		mode=None
		group.hue = mode_state["start_state"]["hue"]
		group.saturation = mode_state["start_state"]["saturation"]
		group.brightness = mode_state["start_state"]["brightness"]
		group.on = mode_state["start_state"]["on"]
		mode_state = {}
	else:
		mode="MagicMissile"
		start_state = {
			"hue": lights[0].hue,
			"saturation": lights[0].saturation,
			"brightness":lights[0].brightness,
			"on": lights[0].on
		}
		light_queue = lights.copy()
		random.shuffle(light_queue)
		light_queue = deque(light_queue)
		mode_state["start_state"] = start_state
		mode_state["light_queue"] = light_queue
		group.on = True
		group.transitiontime = 4
		group.brightness = 1
		group.hue = 45000
		group.saturation = 100
	print("Set mode to {}".format(mode))

def magic_missile():
	global mode
	global mode_state
	light = mode_state["light_queue"].pop()
	mode_state["light_queue"].appendleft(light)
	def mm(light):
		# magic_noise() #This doesn't "stack" well across multiple calls
		light.transitiontime = 1
		light.brightness = 255
		light.hue = 55000
		light.saturation = 255
		light.transitiontime = 4
		light.brightness = 1
		time.sleep(0.4)
		light.hue = 45000
		light.saturation = 100
	t = threading.Thread(target=mm, args=(light,))
	t.start()


def init_chromecast():
	chromecasts = pychromecast.get_chromecasts()
	cast = next(cc for cc in chromecasts if cc.device.friendly_name == "Living Room speaker")
	cast.wait()
	cast.set_volume(1)
	mc = cast.media_controller
	# mc.play_media('http://sir-cinnamon.com/dnd/thunder.mp3', 'audio/mp3')
	# mc.block_until_active()
	return mc

def toggle_mode_colour():
	global mode
	if(mode!=None):
		mode=None
	else:
		mode="Colour"
	print("Set mode to {}".format(mode))

def thunder_noise():
	global media_controller
	if(media_controller == None): return
	media_controller.play_media('http://sir-cinnamon.com/dnd/thunder.mp3', 'audio/mp3')
	media_controller.block_until_active()
def magic_noise():
	global media_controller
	if(media_controller == None): return
	media_controller.play_media('http://sir-cinnamon.com/dnd/magic.mp3', 'audio/mp3')
	media_controller.block_until_active()

if __name__ == "__main__":
	@skywriter.tap(position="north")
	def tap_north():
		global mode
		if(mode=="Lightning"): double_lightning(sound=True)

	@skywriter.tap(position="east")
	def tap_east():
		global mode
		if(mode==None or mode=="Lightning"):
			toggle_mode_lightning()

	@skywriter.tap(position="south")
	def tap_south():
		global mode
		global mode_state
		if(mode==None or mode=="Colour"):
			toggle_mode_colour()
		print(json.dumps(mode_state))

	@skywriter.tap(position="west")
	def tap_west():
		global mode
		if(mode==None or mode=="MagicMissile"):
			toggle_mode_magic_missile()
		if(mode=="Lightning"): single_lightning(sound=True)

	@skywriter.tap(position="center", repeat_rate=3)
	def tap_center():
		global mode
		if(mode=="MagicMissile"): magic_missile()
		if(mode=="Lightning"): single_lightning(sound=False)

	@skywriter.flick()
	def flick(start, finish):
		global mode
		if(mode=="Colour"):
			o = start[0]+finish[0]
			if(o == "sn"):
				pushed_up("sn")
			elif(o == "ns"):
				pushed_down("ns")
			elif(o == "we"):
				pushed_right("we")
			elif(o == "ew"):
				pushed_left("ew")

	@skywriter.airwheel()
	def brightness(deg):
		global mode
		if(mode=="Colour"):
			bri = int(lights[0].brightness + (deg/5))
			bri = max(0, min(255, bri))
			print(bri)
			for l in lights:
				l.brightness = bri

	media_controller = init_chromecast()
	print("ready")
	signal.pause()

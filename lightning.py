#!/usr/bin/python3

from phue import Bridge, Group
import threading
import random
import time, datetime
import skywriter
import signal
from queue import Queue
import requests
import json
import random
import pychromecast

b = Bridge('10.0.0.80')
b.connect() #Comment out after first run
url = "http://10.0.0.34:8080/post/"
group = Group(b, "Living room")
lights = group.lights

@skywriter.flick()
def flick(start, finish):
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
	bri = int(lights[0].brightness + (deg/5))
	bri = max(0, min(255, bri))
	print(bri)
	for l in lights:
		l.brightness = bri

fire_effect = [
	{
		"hue": 0, # Red
		"saturation": 126, # Center
		"brightness": 180,
		"fade_in": 12,
	},
	{
		"hue": 3822, # Orange
		"saturation": 126,
		"brightness": 200,
		"fade_in": 5
	},
	{
		"hue": 9284, # Yellow
		"saturation": 126,
		"brightness": 250,
		"fade_in": 3
	},
	{
		"hue": 3822, # Orange
		"saturation": 126,
		"brightness": 200,
		"fade_in": 2
	},
	{
		"hue": 9284, # Yellow
		"saturation": 126,
		"brightness": 250,
		"fade_in": 1
	},
	{
		"hue": 3822, # Orange
		"saturation": 126,
		"brightness": 200,
		"fade_in": 1
	},
	{
		"hue": 0, # Red
		"saturation": 126,
		"brightness": 180,
		"fade_in": 3
	}
]

def play_scene_random_independent(scene, light, start_index):
	original_state = {
		"on": light.on,
		"brightness": light.brightness,
		"hue": light.hue,
		"saturation": light.saturation
	}
	light.on = True
	for step in range(len(scene)):
		i = ((step+start_index)%len(scene))
		command = {
			"transitiontime": (scene[i]["fade_in"] * 10)if "fade_in" in scene[i] else light.transitiontime,
			"hue": scene[i]["hue"] if "hue" in scene[i] else light.hue,
			"sat": scene[i]["saturation"] if "saturation" in scene[i] else light.saturation,
			"bri": scene[i]["brightness"] if "brightness" in scene[i] else light.brightness
		}
		b.set_light(light.light_id, command)
		time.sleep(command["transitiontime"]/10)

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
	# for l in lights:
	# 	t = threading.Thread(target=play_scene_random_independent, args=(fire_effect, l, random.randint(0, len(fire_effect))))
	# 	t.start()

def pushed_left(event):
	val = 3000
	current_hue = int(((lights[0].hue-val)+65535)%65535)
	command = {
		"hue": current_hue,
		"sat": 126
	}
	for l in lights:
		b.set_light(l.light_id, command)

@skywriter.tap(position="north")
def tap_north():
	print("Tapped north")
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
	thunder_noise()
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

@skywriter.tap(position="east")
def tap_north():
	print("Tapped east")
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
	thunder_noise()
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

def init_chromecast():
	chromecasts = pychromecast.get_chromecasts()
	cast = next(cc for cc in chromecasts if cc.device.friendly_name == "Living Room speaker")
	cast.wait()
	cast.set_volume(1)
	mc = cast.media_controller
	# mc.play_media('http://sir-cinnamon.com/dnd/thunder.mp3', 'audio/mp3')
	# mc.block_until_active()
	return mc

media_controller = init_chromecast()
print("ready")
def thunder_noise():
	global media_controller
	media_controller.play_media('http://sir-cinnamon.com/dnd/thunder.mp3', 'audio/mp3')
	media_controller.block_until_active()

if __name__ == "__main__":
	signal.pause()

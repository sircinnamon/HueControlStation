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
media_controller = None


fire_graph = {
	"base_red_1": {
		"transition_to": 3,
		"hue": 1,
		"saturation": 127,
		"brightness": 200,
		"edges": [
			{
				"dest": "base_red_2",
				"weight": 0.66
			},
			{
				"dest": "flicker_orange",
				"weight": 0.66
			}
		]
	},
	"base_red_2": {
		"transition_to": 3,
		"hue": 1,
		"saturation": 150,
		"brightness": 225,
		"edges": [
			{
				"dest": "base_red_3",
				"weight": 1
			}
		]
	},
	"base_red_3": {
		"transition_to": 3,
		"hue": 1,
		"saturation": 100,
		"brightness": 150,
		"edges": [
			{
				"dest": "base_red_1",
				"weight": 1
			}
		]
	},
	"flicker_orange": {
		"transition_to": 3,
		"hue": 1,
		"saturation": 130,
		"brightness": 225,
		"edges": [
			{
				"dest": "flicker_yellow",
				"weight": 1
			}
		]
	},
	"flicker_yellow": {
		"transition_to": 3,
		"hue": 1,
		"saturation": 130,
		"brightness": 225,
		"edges": [
			{
				"dest": "base_red_1",
				"weight": 1
			}
		]
	}
}

def get_next_node(curr_id, graph):
	r = random.random()
	i = 0
	next_node = curr_id
	for edge in graph[curr_id]["edges"]:
		i = i + edge["weight"]
		if i >= r:
			next_node = edge["dest"]
			break
	return next_node

def follow_graph_independent(graph, lights):
	# TODO: Fuzz timings somehow to reduce sync'd transitions?
	# TODO: signal thread to return to original_state and die?
    def light_thread(graph, light)
        original_state = {
            "on": light.on,
            "brightness": light.brightness,
            "hue": light.hue,
            "saturation": light.saturation
        }
        light.on = True
        current_node = graph[list(graph.keys())[0]]
        while True:
            command = {
                "transitiontime": (graph[current_node]["transition_to"] * 10)if "transition_to" in graph[current_node] else light.transitiontime,
                "hue": graph[current_node]["hue"] if "hue" in graph[current_node] else light.hue,
                "sat": graph[current_node]["saturation"] if "saturation" in graph[current_node] else light.saturation,
                "bri": graph[current_node]["brightness"] if "brightness" in graph[current_node] else light.brightness
            }
            b.set_light(light.light_id, command)
            time.sleep(command["transitiontime"])
            current_node = get_next_node(current_node, graph)

    for l in lights:
        t = threading.Thread(target=light_thread, args=(fire_graph, l))
        t.start()


def pushed_up(event):
	print("PUSHED UP")
	for l in lights:
		l.on = (not l.on)

def fire():
	follow_graph_independent(fire_graph, lights)

def init_chromecast():
	chromecasts = pychromecast.get_chromecasts()
	cast = next(cc for cc in chromecasts if cc.device.friendly_name == "Living Room speaker")
	cast.wait()
	cast.set_volume(1)
	mc = cast.media_controller
	# mc.play_media('http://sir-cinnamon.com/dnd/thunder.mp3', 'audio/mp3')
	# mc.block_until_active()
	return mc

if __name__ == "__main__":


	@skywriter.tap(position="center", repeat_rate=3)
	def tap_center():
		fire();

	# media_controller = init_chromecast()
	print("ready")
	signal.pause()

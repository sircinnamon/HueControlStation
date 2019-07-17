#!/usr/bin/python3

from phue import Bridge
import threading
import random
import time, datetime
import skywriter
import signal
from queue import Queue
import requests
import json

# b = Bridge('10.0.0.80')
# b.connect() #Comment out after first run
q = Queue(maxsize=200)
threshold = 0.8

r = [255,0,0]
b = [0,0,0]
r_arrow = [
[b,b,b,b,b,b,b,b],
[b,b,b,b,r,b,b,b],
[b,b,b,b,b,r,b,b],
[b,r,r,r,r,r,r,b],
[b,b,b,b,b,r,b,b],
[b,b,b,b,r,b,b,b],
[b,b,b,b,b,b,b,b],
[b,b,b,b,b,b,b,b],
]
l_arrow = [
[b,b,b,b,b,b,b,b],
[b,b,b,r,b,b,b,b],
[b,b,r,b,b,b,b,b],
[b,r,r,r,r,r,r,b],
[b,b,r,b,b,b,b,b],
[b,b,b,r,b,b,b,b],
[b,b,b,b,b,b,b,b],
[b,b,b,b,b,b,b,b],
]
u_arrow = [
[b,b,b,b,b,b,b,b],
[b,b,b,r,b,b,b,b],
[b,b,r,r,r,b,b,b],
[b,r,b,r,b,r,b,b],
[b,b,b,r,b,b,b,b],
[b,b,b,r,b,b,b,b],
[b,b,b,r,b,b,b,b],
[b,b,b,b,b,b,b,b],
]
d_arrow = [
[b,b,b,b,b,b,b,b],
[b,b,b,r,b,b,b,b],
[b,b,b,r,b,b,b,b],
[b,b,b,r,b,b,b,b],
[b,r,b,r,b,r,b,b],
[b,b,r,r,r,b,b,b],
[b,b,b,r,b,b,b,b],
[b,b,b,b,b,b,b,b],
]
url = "http://10.0.0.34:8080/post/"

class Killer:
	shutdown = False
	def __init__(self):
		signal.signal(signal.SIGINT, self.exit_gracefully)
		signal.signal(signal.SIGTERM, self.exit_gracefully)

	def exit_gracefully(self, signum, frame):
		self.shutdown = True

@skywriter.move()
def move(x, y, z):
	# print( x, y, z )
	if q.full(): q.get()
	q.put({
		"time": datetime.datetime.now().timestamp(),
		"x": x,
		"y": y
	});

@skywriter.flick()
def flick(start, finish):
    o = start[0]+finish[0]
    if(o == "sn"):
        print("flick sn")
    elif(o == "ns"):
        print("flick ns")
    elif(o == "we"):
        print("flick we")
    elif(o == "ew"):
        print("flick ew")

def check_wave(l, axis):
	# l = l[::-1]
	# print(len(l))
	# print(l)
	if(len(l)<2): return {}
	prev = l[0][axis]
	j = 0
	while l[j][axis] == l[0][axis]:
		j = j+1
		if j >= len(l): return {}
	delta = l[j][axis]-l[0][axis]
	i = 0
	while (i+1) < len(l):
		i = i+1
		if(l[i][axis] == prev): pass
		if ((l[0]["time"] - l[i]["time"]) > 2): break
		# print("Not time break")
		if (delta < 0) and ((l[i][axis] - prev) < 0):
			# print("Negative still negative")
			prev = l[i][axis]
		elif (delta > 0) and ((l[i][axis] - prev) > 0):
			# print("positive still positive")
			prev = l[i][axis]
		else:
			break
	# print("Broke at {}".format(i))
	# print("THRESH {}".format(threshold))
	# print(delta)
	# Everything from 0 to i should be part of the gesture
	if (abs(l[0][axis] - l[i][axis]) > threshold):
		# Gesture was long enough
		# print("Dist {}".format(abs(l[0][axis] - l[i][axis])))
		return {"start":l[i], "end":l[0]}
	if((datetime.datetime.now().timestamp() - l[1]["time"]) < 0.75):
		return check_wave(l[1:], axis)

def calculate_speed(wave, axis):
	duration = wave["end"]["time"] - wave["start"]["time"]
	distance = abs(wave["end"][axis] - wave["start"][axis])
	# Returns board width per second
	return distance/duration

def process_actions():
	axis = "x"
	wave = check_wave(list(q.queue)[::-1], "x")
	if not wave:
		wave = check_wave(list(q.queue)[::-1], "y")
		axis = "y"

	if wave:
		print("{} WAVE".format(axis))
		print(wave)
		speed = calculate_speed(wave, axis)
		print(speed)
		colour = [255,0,0]
		if(speed>20):colour = [225,225,0]
		if(speed>30):colour = [0,255,0]
		q.queue.clear()
		if(axis=="x"):		
			if(wave["start"]["x"] < wave["end"]["x"]):
				r_arrow[0][0] = colour
				r = requests.post(url, data=json.dumps({"map":r_arrow}))
			else:
				l_arrow[0][0] = colour
				r = requests.post(url, data=json.dumps({"map":l_arrow}))
		if(axis=="y"):			
			if(wave["start"]["y"] < wave["end"]["y"]):
				u_arrow[0][0] = colour
				r = requests.post(url, data=json.dumps({"map":u_arrow}))
			else:
				d_arrow[0][0] = colour
				r = requests.post(url, data=json.dumps({"map":d_arrow}))

if __name__ == "__main__":
	killer = Killer()
	while not killer.shutdown:
		time.sleep(0.5)
		process_actions()

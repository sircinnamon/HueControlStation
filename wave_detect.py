#!/usr/bin/python3

from phue import Bridge
import threading
import random
import time, datetime
import skywriter
from signal import pause
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

@skywriter.move()
def move(x, y, z):
	# print( x, y, z )
	if q.full(): q.get()
	q.put({
		"time": datetime.datetime.now().timestamp(),
		"x": x,
		"y": y
	});

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
		return {"start":l[0], "end":l[i]}
	if((datetime.datetime.now().timestamp() - l[1]["time"]) < 0.75):
		return check_wave(l[1:], axis)

while True:
	time.sleep(0.5)
	wave = check_wave(list(q.queue)[::-1], "x")
	if wave:
		print("X WAVE")
		print(wave)
		q.queue.clear()
		if(wave["start"]["x"] > wave["end"]["x"]):
			r = requests.post(url, data=json.dumps({"map":r_arrow}))
		else:
			r = requests.post(url, data=json.dumps({"map":l_arrow}))

		print(r)
	wave = check_wave(list(q.queue)[::-1], "y")
	if wave:
		print("Y WAVE")
		print(wave)
		q.queue.clear()
		if(wave["start"]["y"] > wave["end"]["y"]):
			r = requests.post(url, data=json.dumps({"map":u_arrow}))
		else:
			r = requests.post(url, data=json.dumps({"map":d_arrow}))


pause()

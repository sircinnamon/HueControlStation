#!/usr/bin/python

from phue import Bridge
import threading
import random
import time, datetime
import skywriter
from signal import pause
from queue import Queue

# b = Bridge('10.0.0.80')
# b.connect() #Comment out after first run
q = Queue(maxsize=200)
threshold = 0.8

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
	print(len(l))
	# print(l)
	if(len(l)<2): return False
	prev = l[0][axis]
	j = 0
	while l[j][axis] == l[0][axis]:
		j = j+1
		if j >= len(l): return False
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
		print("Dist {}".format(abs(l[0][axis] - l[i][axis])))
		return True
	if((datetime.datetime.now().timestamp() - l[1]["time"]) < 0.75):
		return check_wave(l[1:], axis)

while True:
	time.sleep(0.5)
	if check_wave(list(q.queue)[::-1], "x"):
		print("X WAVE")
		q.queue.clear()
		input()
	if check_wave(list(q.queue)[::-1], "y"):
		print("Y WAVE")
		q.queue.clear()
		input()

pause()

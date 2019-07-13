
#!/usr/bin/python

from phue import Bridge
import threading
import random
import time

from sense_hat import SenseHat, ACTION_PRESSED, ACTION_HELD, ACTION_RELEASED
from signal import pause
sense = SenseHat()

b = Bridge('10.0.0.80')
b.connect() #Comment out after first run

lights = b.lights

# Hue: 0 to 65535
# Saturation: 0 (Black) to 254 (White)
# Brightness: 1 to 254
# Transition time: deciseconds (100ms)

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




# for l in lights:
#     t = threading.Thread(target=play_scene_random_independent, args=(fire_effect, l, random.randint(0, len(fire_effect))))
#     t.start()
current_hue=2000
def pushed_up(event):
    print("PUSHED UP")
    if event.action == ACTION_PRESSED:
        command = {
            "on":True
        }
        for l in lights:
            b.set_light(l.light_id, command)

def pushed_right(event):
    global current_hue
    print("PUSHED RIGHT {}".format(current_hue))
    if event.action == ACTION_PRESSED:
        current_hue = max(current_hue+1000, 0)
        command = {
            "hue": current_hue,
            "sat": 126,
            "bri": 255
        }
        for l in lights:
            b.set_light(l.light_id, command)

def pushed_down(event):
    print("PUSHED DOWN")
    if event.action == ACTION_PRESSED:
        command = {
            "on":False
        }
        for l in lights:
            b.set_light(l.light_id, command)

def pushed_left(event):
    global current_hue
    print("PUSHED LEFT {}".format(current_hue))
    if event.action == ACTION_PRESSED:
        current_hue = max(current_hue-1000, 0)
        command = {
            "hue": current_hue,
            "sat": 126,
            "bri": 255
        }
        for l in lights:
            b.set_light(l.light_id, command)

sense.stick.direction_up = pushed_up
sense.stick.direction_down = pushed_down
sense.stick.direction_left = pushed_left
sense.stick.direction_right = pushed_right

pause()
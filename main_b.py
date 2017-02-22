import kivy
kivy.require('1.0.6') # replace with your current kivy version !

from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.togglebutton import ToggleButton
#from kivy.uix.gridlayout import GridLayout
from kivy.properties import NumericProperty
from kivy.properties import StringProperty
from kivy.properties import BoundedNumericProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.widget import Widget
from kivy.uix.scatter import Scatter
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.progressbar import ProgressBar
import os,inspect
from time import sleep
import time, math
from functools import partial

#from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.image import Image
from kivy.uix.slider import Slider
from kivy.clock import Clock
from kivy.graphics import Color, Rectangle

import RPi.GPIO as GPIO

#variables for speed calculations:
dist_meas = 0.00
km_per_hour = 0
rpm = 0
elapse = 0
sensor = 17
pulse = 0
start_timer = time.time()

# Set up GPIO:
lowbeampin = 27
highbeampin = 22
hazardpin = 23
wiperpin = 24
hornpin = 25
leftsignalpin = 14
rightsignalpin = 15

GPIO.setmode(GPIO.BCM)
GPIO.setup(lowbeampin, GPIO.OUT)
GPIO.output(lowbeampin, GPIO.LOW)
GPIO.setup(highbeampin, GPIO.OUT)
GPIO.output(highbeampin, GPIO.LOW)
GPIO.setup(hazardpin, GPIO.OUT)
GPIO.output(hazardpin, GPIO.LOW)
GPIO.setup(wiperpin, GPIO.OUT)
GPIO.output(wiperpin, GPIO.LOW)
GPIO.setup(hornpin, GPIO.OUT)
GPIO.output(hornpin, GPIO.LOW)
GPIO.setup(leftsignalpin, GPIO.OUT)
GPIO.output(leftsignalpin, GPIO.LOW)
GPIO.setup(rightsignalpin, GPIO.OUT)
GPIO.output(rightsignalpin, GPIO.LOW)

GPIO.setwarnings(False)
GPIO.setup(sensor,GPIO.IN,GPIO.PUD_UP)

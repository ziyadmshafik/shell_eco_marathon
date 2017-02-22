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

# Define some helper functions:
class DummyClass: pass

class Gauge(Widget):
    '''
    Gauge class
    '''

    dummy = DummyClass
    unit = NumericProperty(1.8)
    value = BoundedNumericProperty(0, min=0, max=100, errorvalue=0)
    mypath = os.path.dirname(os.path.abspath(inspect.getsourcefile(dummy)))
    file_gauge = StringProperty(mypath + os.sep + "cadran.png")
    file_needle = StringProperty(mypath + os.sep + "needle.png")
    size_gauge = BoundedNumericProperty(128, min=128, max=256, errorvalue=128)
    size_text = NumericProperty(10)

    def __init__(self, **kwargs):
        super(Gauge, self).__init__(**kwargs)


        self._gauge = Scatter(
            size=(self.size_gauge, self.size_gauge),
            do_rotate=False,
            do_scale=False,
            do_translation=False,
	    scale=1.6
            )

        _img_gauge = Image(source=self.file_gauge, size=(self.size_gauge,
            self.size_gauge))

        self._needle = Scatter(
            size=(self.size_gauge, self.size_gauge),
            do_rotate=False,
            do_scale=False,
            do_translation=False,
	    scale=1.6
            )

        _img_needle = Image(source=self.file_needle, size=(self.size_gauge,
            self.size_gauge))

        self._glab = Label(font_size=self.size_text, markup=True)
        self._progress = ProgressBar(max=100, height=100, value=self.value)

        self._gauge.add_widget(_img_gauge)
        self._needle.add_widget(_img_needle)

        self.add_widget(self._gauge)
        self.add_widget(self._needle)
        self.add_widget(self._glab)
        self.add_widget(self._progress)

        self.bind(pos=self._update)
        self.bind(size=self._update)
        self.bind(value=self._turn)

    def _update(self, *args):
        '''
        Update gauge and needle positions after sizing or positioning.
        '''
        self._gauge.pos = self.pos
        self._needle.pos = (self.x, self.y)
        self._needle.center = self._gauge.center
        self._glab.center_x = self._gauge.center_x
        self._glab.center_y = self._gauge.center_y + (self.size_gauge/4)
        self._progress.x = self._gauge.x+75
        self._progress.y = self._gauge.y + (self.size_gauge / 4)
        self._progress.width = self.size_gauge

    def _turn(self, *args):
        '''
        Turn needle, 1 degree = 1 unit, 0 degree point start on 50 value.
        '''
        self._needle.center_x = self._gauge.center_x
        self._needle.center_y = self._gauge.center_y
        self._needle.rotation = (50 * self.unit) - (self.value * self.unit)
        self._glab.text = "[b]{0:.0f}[/b]".format(self.value)
        self._progress.value = self.value


dirflag = 1
value = 0
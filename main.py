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

#from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.image import Image
from kivy.uix.slider import Slider
from kivy.clock import Clock
from kivy.graphics import Color, Rectangle

import RPi.GPIO as GPIO

#for now, use a global for blink speed (better implementation TBD):
speed = 1.0

# Set up GPIO:
lowbeampin = 27
highbeampin = 22
hazardpin = 23
wiperpin = 24
hornpin = 25

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
            do_translation=False
            )

        _img_gauge = Image(source=self.file_gauge, size=(self.size_gauge, 
            self.size_gauge))

        self._needle = Scatter(
            size=(self.size_gauge, self.size_gauge),
            do_rotate=False,
            do_scale=False,
            do_translation=False
            )

        _img_needle = Image(source=self.file_needle, size=(self.size_gauge, 
            self.size_gauge))

        self._glab = Label(font_size=self.size_text, markup=True)
        self._progress = ProgressBar(max=100, height=20, value=self.value)
       
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
        self._progress.x = self._gauge.x
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
value = 50

# This callback will be bound to the LED toggle and Beep button:
def press_callback(obj):
	print("Button pressed,", obj.text)
	if obj.text == 'BEEP!':
		# turn on the beeper:
		GPIO.output(hornpin, GPIO.HIGH)
		# schedule it to turn off:
		Clock.schedule_once(horn_off, .25)
	if obj.text == 'Driving\nLights':
		if obj.state == "down":
			print ("button on")
			GPIO.output(lowbeampin, GPIO.HIGH)
		else:
			print ("button off")
			GPIO.output(lowbeampin, GPIO.LOW)
        if obj.text == 'Highbeam\nLights':
                if obj.state == "down":
                        print ("button on")
                        GPIO.output(highbeampin, GPIO.HIGH)
                else:
                        print ("button off")
                        GPIO.output(highbeampin, GPIO.LOW)
        if obj.text == 'Wiper':
                if obj.state == "down":
                        print ("button on")
                        GPIO.output(wiperpin, GPIO.HIGH)
                else:
                        print ("button off")
                        GPIO.output(wiperpin, GPIO.LOW)
        if obj.text == 'Hazard':
                if obj.state == "down":
                        print ("button on")
                        GPIO.output(hazardpin, GPIO.HIGH)
			Clock.schedule_once(hazard_toggle, 0.75)
		else:
			Clock.unschedule(hazard_toggle)
			GPIO.output(hazardpin, GPIO.LOW)
def horn_off(dt):
	GPIO.output(hornpin, GPIO.LOW)

def hazard_toggle(dt):
	GPIO.output(hazardpin, not GPIO.input(hazardpin))
	Clock.schedule_once(hazard_toggle, 0.75)

class MyApp(App):

	def build(self):
		# Set up the layout:
		# layout = GridLayout(cols=5, spacing=30, padding=30, row_default_height=150)
		layout = FloatLayout(size=(800,600))
		# Make the background gray:
		#with layout.canvas.before:
		#	Color(.2,.2,.2,1)
		#	self.rect = Rectangle(size=(800,600), pos=layout.pos)
#			from kivy.clock import Clock
#			from functools import partial
#			from kivy.uix.slider import Slider


		def setgauge(sender, value):
			mygauge.value = value
				
		def incgauge(sender, incr):
			global dirflag
			global value
				
				
			if dirflag == 1:
				if value <100:
					value += incr
					setgauge(0,value)
					sl.value = value 
				else:
					dirflag = 0
			else:
				if value >0:
					value -= incr
					setgauge(sender, value)
					sl.value = value
					
				else:
					dirflag = 1
			
		mygauge = Gauge(value=50, size_gauge=256, size_text=25,pos=(100,100))



	# Create the rest of the UI objects (and bind them to callbacks, if necessary):
		highbeam_button = ToggleButton(text="Highbeam\nLights", halign='center', size_hint=(.1,.1),pos = (20,20))
		highbeam_button.bind(on_press=press_callback)
		lowbeam_button = ToggleButton(text="Driving\nLights", halign='center' , size_hint=(.1,.1),pos = (120,20))
        	lowbeam_button.bind(on_press=press_callback)
		hazard_button = ToggleButton(text="Hazard",size_hint=(.1,.1),pos = (220,20))
	        hazard_button.bind(on_press=press_callback)
		wiper_button = ToggleButton(text="Wiper",size_hint=(.1,.1),pos = (320,20))
	        wiper_button.bind(on_press=press_callback)
		horn_button = Button(text="BEEP!",size_hint=(.1,.1),pos = (420,20))
	        horn_button.bind(on_press=press_callback)
		wimg = Image(source='logo.png',pos = (500,100))
		
	# Add the UI elements to the layout:
		layout.add_widget(highbeam_button)
		layout.add_widget(lowbeam_button)
		layout.add_widget(hazard_button)
		layout.add_widget(wiper_button)
		layout.add_widget(horn_button)
		layout.add_widget(mygauge)
		layout.add_widget(wimg)
		return layout

if __name__ == '__main__':
	MyApp().run()

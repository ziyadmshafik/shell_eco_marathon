import kivy
kivy.require('1.0.6') # replace with your current kivy version !

from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.togglebutton import ToggleButton
from kivy.properties import NumericProperty
from kivy.properties import StringProperty
from kivy.properties import ObjectProperty
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
class StopWatch(Widget):
    
    def __init__(self, **kwargs):
        super(StopWatch, self).__init__(**kwargs)

        self.laplbl = Label(text="test",font_size=25, markup=True)
        self.add_widget(self.laplbl)

        self.timelbl = Label(text="test",font_size=50, markup=True)
        self.add_widget(self.timelbl)

        self.startbtn = Button(text="Start", size=(112,120), font_size=25)
        self.add_widget(self.startbtn)
        self.startbtn.bind(on_press=self.start_time)

        self.stopbtn = Button(text="Stop", size=(112,120), font_size=25)
        self.add_widget(self.stopbtn)
        self.stopbtn.bind(on_press=self.stop_time)

        self.resetbtn = Button(text="Reset", size=(112,120), font_size=25)
        self.add_widget(self.resetbtn)
        self.resetbtn.bind(on_press=self.reset_time)

        self.lapbtn = Button(text="Lap", size=(112,120), font_size=25)
        self.add_widget(self.lapbtn)
        self.lapbtn.bind(on_press=self.lap_time)

        self.laplbl.pos = (525,400)
        self.laplbl.max_lines=5
        self.timelbl.pos = (525,235)
        self.startbtn.pos = (344,142)
        self.stopbtn.pos = (458,142)
        self.resetbtn.pos = (572,142)
        self.lapbtn.pos = (686,142)

    #gloabl variables
    seconds = 0
    minuets = 0
    mili = 0
    _mili = 0
    time_track = StringProperty("00:00:00")
    laps = []
    running = False
    resetting = True
    addLap = False

    def printLaps(self):
        lap_string = ""
        count = len(self.laps)
        for lap in reversed(self.laps):
            lap_string += "Lap " + str(count) +": " + lap + "\n"
            count -=1
        return lap_string   

    def update(self,dt):
        self.timelbl.text = str(self.time_track)
        
        if not self.laps:
            self.laplbl.text = ""
        else:
            self.laplbl.text = self.printLaps()
       
        if(self.running):

            if(self.seconds < 10 and self.minuets < 10 and self.mili < 10):
                self.time_track = "0" + str(self.minuets) + ":0" + str(self.seconds) + ":0" + str(self.mili)
            
            elif(self.seconds < 10 and self.minuets < 10 and self.mili >= 10):
                self.time_track = "0" + str(self.minuets) + ":0" + str(self.seconds) + ":" + str(self.mili)
            
            elif(self.seconds >= 10 and self.minuets < 10 and self.mili < 10 ):
                self.time_track = "0" + str(self.minuets) + ":" + str(self.seconds) + ":0" + str(self.mili)

            elif(self.seconds >= 10 and self.minuets < 10 and self.mili >= 10):
                self.time_track = "0" + str(self.minuets) + ":" + str(self.seconds) + ":" + str(self.mili)

            elif(self.seconds >= 10 and self.minuets >= 10 and self.mili < 10):
                self.time_track =  str(self.minuets) + ":" + str(self.seconds) + ":0" + str(self.mili)

            elif(self.seconds < 10 and self.minuets >= 10 and self.mili >= 10):
                self.time_track = "0" + str(self.minuets) + ":" + str(self.seconds) + ":" + str(self.mili)
            
            elif(self.seconds < 10 and self.minuets >= 10 and self.mili < 10):
                self.time_track = str(self.minuets) + ":0" + str(self.seconds) + ":0" + str(self.mili)
            
            elif(self.seconds >= 10 and self.minuets >= 10 and self.mili >= 10):
                self.time_track = str(self.minuets) + ":" + str(self.seconds) + ":" + str(self.mili)

            if(self.seconds >= 60):

                self.minuets += 1
                self.seconds = 0

            if(self.mili >= 99):
                self.seconds+=1
                self.mili = 0
                self._mili = 0

            self._mili += dt*100
            self.mili = int(round(self._mili, 0))
           
        if(self.resetting == True):
            self.minuets = 0
            self.seconds = 0
            self.mili = 0
            self.time_track = str(self.minuets) + "0:0" + str(self.seconds) + ":0" + str(self.mili)
            self.laps = []
            self.resetting = False
            self.running = False

        if(self.addLap == True):
            self.laps.append(self.time_track)
            self.laplbl.text = str(self.time_track)
            self.addLap = False
           

    #Starts the timer
    def start_time(self,dt):
        print("START TIME!")
        self.running = True
        
    #Stops the timer
    def stop_time(self,dt):
        print("STOP TIME!")
        self.running = False

    #Reset the timer
    def reset_time(self,dt):
        print("RESET TIME!")
        self.running = False
        self.resetting = True

    def lap_time(self,dt):
        print("LAP!")
        self.addLap = True
        print(self.time_track)


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
        if obj.text == 'High\nBeam\nLights':
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
			Clock.unschedule(leftsig_toggle)
			Clock.unschedule(rightsig_toggle)
                        GPIO.output(rightsignalpin, GPIO.HIGH)
			GPIO.output(leftsignalpin, GPIO.HIGH)
			Clock.schedule_once(hazard_toggle, 0.75)
		else:
			Clock.unschedule(hazard_toggle)
			GPIO.output(rightsignalpin, GPIO.LOW)
			GPIO.output(leftsignalpin, GPIO.LOW)
        if obj.text == 'Left\nSignal':
                if obj.state == "down":
                        print ("button on")
			Clock.unschedule(rightsig_toggle)
			Clock.unschedule(hazard_toggle)
                        GPIO.output(leftsignalpin, GPIO.HIGH)
			Clock.schedule_once(leftsig_toggle, 0.75)
		else:
			Clock.unschedule(leftsig_toggle)
			GPIO.output(leftsignalpin, GPIO.LOW)
        if obj.text == 'Right\nSignal':
                if obj.state == "down":
                        print ("button on")
			Clock.unschedule(leftsig_toggle)
			Clock.unschedule(hazard_toggle)
                        GPIO.output(rightsignalpin, GPIO.HIGH)
			Clock.schedule_once(rightsig_toggle, 0.75)
		else:
			Clock.unschedule(rightsig_toggle)
			GPIO.output(rightsignalpin, GPIO.LOW)
#def setgauge(sender,value):
#	mygauge.value = value


#def update_speed(dt):
#	value = calculate_speed(20)
#	setgauge(0,value)

def horn_off(dt):
	GPIO.output(hornpin, GPIO.LOW)

def hazard_toggle(dt):
	GPIO.output(rightsignalpin, not GPIO.input(rightsignalpin))
	GPIO.output(leftsignalpin, not GPIO.input(leftsignalpin))
	Clock.schedule_once(hazard_toggle, 0.75)
	
def rightsig_toggle(dt):
	GPIO.output(rightsignalpin, not GPIO.input(rightsignalpin))
	Clock.schedule_once(rightsig_toggle, 0.75)

def leftsig_toggle(dt):
	GPIO.output(leftsignalpin, not GPIO.input(leftsignalpin))
	Clock.schedule_once(leftsig_toggle, 0.75)

def calculate_elapse(channel):            		# callback function
	global pulse, start_timer, elapse
	pulse+=1                        		# increase pulse by 1 whenever interrupt occurred
	elapse = time.time() - start_timer      	# elapse for every 1 complete rotation made!
	start_timer = time.time()            		# let current time equals to start_timer

def calculate_speed(r_cm):
	global pulse,elapse,rpm,dist_km,dist_meas,km_per_sec,km_per_hour
	if elapse !=0:                     		# to avoid DivisionByZero error
		rpm = 1/elapse * 60
		circ_cm = (2*math.pi)*r_cm         	# calculate wheel circumference in CM
		dist_km = circ_cm/100000          	# convert cm to km
		km_per_sec = dist_km / elapse      	# calculate KM/sec
		km_per_hour = km_per_sec * 3600      	# calculate KM/h
		dist_meas = (dist_km*pulse)*1000   	# measure distance traverse in meter
		print('rpm:{0:.0f}-RPM kmh:{1:.0f}-KMH dist_meas:{2:.2f}m pulse:{3}'.format(rpm,km_per_hour,dist_meas,pulse))
		return km_per_hour

def init_interrupt():
   GPIO.add_event_detect(sensor, GPIO.FALLING, callback = calculate_elapse, bouncetime = 20)

class MyApp(App):

	def build(self):
		# Set up the layout:
		# layout = GridLayout(cols=5, spacing=30, padding=30, row_default_height=150)
		layout = FloatLayout(size=(800,600))
		mystopwatch = StopWatch()
        	Clock.schedule_interval(mystopwatch.update, 1/100)
		# Make the background gray:
		#with layout.canvas.before:
		#	Color(.2,.2,.2,1)
		#	self.rect = Rectangle(size=(800,600), pos=layout.pos)
#			from kivy.clock import Clock
#			from functools import partial
#			from kivy.uix.slider import Slider


		def update_speed(dt):
			value = calculate_speed(28)
			setgauge(0,value)

		def setgauge(sender, value):
			mygauge.value = value

		def incgauge(dt):
			global value
			global temp_val
			for temp_val in range(0,100):
				temp_val += 1
				value += 1
				setgauge(0,value)
				print(value)
			for temp_var in range(0,100):
				temp_val += 1
				value -= 1
				setgauge(0,value)
				print(value)

		mygauge = Gauge(value=0, size_gauge=256, size_text=60, pos=(0,84))
		Clock.schedule_interval(update_speed, 0.5)
		Clock.schedule_once(incgauge,1)
		
	# Create the rest of the UI objects (and bind them to callbacks, if necessary):
                highbeam_button = ToggleButton(text="High\nBeam\nLights", halign='center', size_hint=(.14,.25),pos = (2,20), font_size=25)
                highbeam_button.bind(on_press=press_callback)
                lowbeam_button = ToggleButton(text="Driving\nLights", halign='center' , size_hint=(.14,.25),pos = (116,20), font_size=25)
                lowbeam_button.bind(on_press=press_callback)
                leftsig_button = ToggleButton(text="Left\nSignal", group='signals', halign='center' , size_hint=(.14,.25),pos = (230,20), font_size=25)
                leftsig_button.bind(on_press=press_callback)
                hazard_button = ToggleButton(text="Hazard", group='signals',size_hint=(.14,.25),pos = (344,20), font_size=25)
                hazard_button.bind(on_press=press_callback)
                rightsig_button = ToggleButton(text="Right\nSignal", group='signals',halign='center',size_hint=(.14,.25),pos = (458,20), font_size=25)
                rightsig_button.bind(on_press=press_callback)
                wiper_button = ToggleButton(text="Wiper",size_hint=(.14,.25),pos = (572,20), font_size=25)
                wiper_button.bind(on_press=press_callback)
                horn_button = Button(text="BEEP!",size_hint=(.14,.25),pos = (686,20), font_size=25)
                horn_button.bind(on_press=press_callback)

                #wimg = Image(source='texas_logo.jpeg', scale = 0.5, pos = (200,100))

	# Add the UI elements to the layout:
                layout.add_widget(mygauge)
		layout.add_widget(mystopwatch)
                layout.add_widget(highbeam_button)
                layout.add_widget(lowbeam_button)
                layout.add_widget(leftsig_button)
                layout.add_widget(hazard_button)
                layout.add_widget(rightsig_button)
                layout.add_widget(wiper_button)
                layout.add_widget(horn_button)
#	        layout.add_widget(mygauge)

#	        Clock.schedule_once(incgauge,5)
        	return layout

if __name__ == '__main__':
    init_interrupt()
#	Clock.schedule_interval(update_speed, 0.5)
    MyApp().run()


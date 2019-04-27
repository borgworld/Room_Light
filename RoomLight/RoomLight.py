#!/usr/bin/env python
import PCF8591 as ADC
import RPi.GPIO as GPIO
import time
from pytradfri import Gateway
from pytradfri.api.libcoap_api import APIFactory
from pytradfri.util import load_json, save_json
import threading

DO = 17
LEDOUT = 16
PUSH_BUTTON = 12
THRESHOLD = 220  #40
SENSOR_1= 0
SENSOR_2= 1
BLOCKED= 1
UNBLOCKED= 0
PUSHED = 1
NOT_PUSHED = 0
ROOM_ENTRANCE= 1
ROOM_EXIT= 2
LIGHT_OFF = 0
LIGHT_ON = 1
IP_ADDRESS = '192.168.0.68'
CONFIG_FILE = 'tradfri_standalone_psk.conf'

person_count = 0
last_sensor_status= []
current_sensor_status=[]
last_button_status = NOT_PUSHED
current_button_status = NOT_PUSHED

GPIO.setmode(GPIO.BCM)


def flash_led(e, t):
    """ Flash the led once per second per person. """
    global person_count
    blink_count=0
    GPIO.output(LEDOUT, False)
     
    while not e.isSet():
        if person_count > 0:
            GPIO.output(LEDOUT, True)
            time.sleep(0.5)
            GPIO.output(LEDOUT, False)
            blink_count += 1
            if blink_count < person_count:
                time.sleep(0.5)
            else:
                time.sleep(2)
                blink_count= 0
        else:
            GPIO.output(LEDOUT, False)


e = threading.Event()


def reset_system():
    """ Initialize all settings to initial values. """
    global person_count
    global last_sensor_status
    global current_sensor_status
    person_count = 0
    last_sensor_status= [UNBLOCKED, UNBLOCKED]
    current_sensor_status=[UNBLOCKED, UNBLOCKED]

def initialize_tradlos():
    global lights
    global api
    
    # Load in the file, get our password for the gateway and create an API
    conf = load_json(CONFIG_FILE)
    identity = conf[IP_ADDRESS].get('identity')
    psk = conf[IP_ADDRESS].get('key')
    api_factory = APIFactory(host=IP_ADDRESS, psk_id=identity, psk=psk)

    # This section connects to the gateway and gets information on devices
    api = api_factory.request
    gateway = Gateway()
    devices_command = gateway.get_devices()
    devices_commands = api(devices_command)
    devices = api(devices_commands)

    # Create an array of objects that are lights
    lights = [dev for dev in devices if dev.has_light_control]

def initialize_flash_led():
    t = threading.Thread(name='non-block', target=flash_led, args=(e, 2))
    t.start()

def sensor_status(sensor_number):
    light_value = ADC.read(sensor_number)
    #print(sensor_number, light_value)
    if light_value < THRESHOLD:
        return BLOCKED
    else:
        return UNBLOCKED

def button_status():
    button_value = GPIO.input(PUSH_BUTTON)
    if button_value == False:
        return PUSHED
    else:
        return NOT_PUSHED

def handle_button_pressed():
    global person_count
    person_count = 1
    switch_light(LIGHT_ON)
    print('Light has been reset')

def light_level_in_room():
    return 50

def number_of_people_in_room():
    return person_count

def person_entered():
    global person_count
    person_count=person_count+1

def person_left():
    global person_count
    if person_count > 0:
        person_count=person_count-1

def switch_light(on_or_off):
    if on_or_off == LIGHT_ON:
        try:
            api(lights[0].light_control.set_dimmer(254))
            #print('Light on')
        except:
            print('Failed to switch light on')
#        GPIO.output(LEDOUT, True)
    if on_or_off == LIGHT_OFF:
        try:
            api(lights[0].light_control.set_dimmer(0))
            #print('Light off')
        except:
            print('Failed to switch light off')
#        GPIO.output(LEDOUT, False)
    
def handle_person_passed(direction):
    if direction == ROOM_ENTRANCE:
        person_entered()
        switch_light(LIGHT_ON)
    if direction == ROOM_EXIT:
        person_left()
        if person_count == 0:
            switch_light(LIGHT_OFF)
        
def setup():
    ADC.setup(0x48)
    GPIO.setup(DO, GPIO.IN)
    GPIO.setup(LEDOUT, GPIO.OUT)
    GPIO.setup(PUSH_BUTTON, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    reset_system()
    initialize_tradlos()
    initialize_flash_led()

def loop():
    global last_sensor_status
    global current_sensor_status
    global last_button_status
    global current_button_status

    cnt = 0
    last_p_cnt = person_count
    while True:
            current_sensor_status[SENSOR_1] = sensor_status(SENSOR_1)
            current_sensor_status[SENSOR_2] = sensor_status(SENSOR_2)
            cnt += 1
            if cnt % 10 == 0:
                #print(current_sensor_status)
                if last_p_cnt != person_count:
                    print(person_count)
                last_p_cnt = person_count

            if last_sensor_status[SENSOR_1] != current_sensor_status[SENSOR_1]:
                if current_sensor_status[SENSOR_1] == BLOCKED:
                    if last_sensor_status[SENSOR_2] == BLOCKED:
                        handle_person_passed(ROOM_EXIT)

            if last_sensor_status[SENSOR_2] != current_sensor_status[SENSOR_2]:
                if current_sensor_status[SENSOR_2] == BLOCKED:
                    if last_sensor_status[SENSOR_1] == BLOCKED:
                        handle_person_passed(ROOM_ENTRANCE)

            last_sensor_status[SENSOR_1] = current_sensor_status[SENSOR_1]
            last_sensor_status[SENSOR_2] = current_sensor_status[SENSOR_2]
            
            current_button_status = button_status()
            if last_button_status != current_button_status:
                if current_button_status == PUSHED:
                    handle_button_pressed()
            last_button_status = current_button_status

            #print(last_sensor_status[SENSOR_1],last_sensor_status[SENSOR_2]) 
            #time.sleep(0.2)

if __name__ == '__main__':
    try:
            setup()
            loop()
    except KeyboardInterrupt:
            e.set()
            GPIO.cleanup()
            pass    

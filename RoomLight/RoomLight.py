#!/usr/bin/env python
import PCF8591 as ADC
import RPi.GPIO as GPIO
import time

DO = 17
LEDOUT = 16
THRESHOLD = 40
SENSOR_1= 0
SENSOR_2= 1
BLOCKED= 1
UNBLOCKED= 0
ROOM_ENTRANCE= 1
ROOM_EXIT= 2
LIGHT_OFF = 0
LIGHT_ON = 1
personCount = 0
lastSensorStatus= []
currentSensorStatus=[]

GPIO.setmode(GPIO.BCM)

def resetSystem():
    global personCount
    global lastSensorStatus
    global currentSensorStatus
    personCount = 0
    lastSensorStatus= [UNBLOCKED, UNBLOCKED]
    currentSensorStatus=[UNBLOCKED, UNBLOCKED]

def sensorStatus(sensorNumber):
    lightValue = ADC.read(sensorNumber)
    if lightValue > THRESHOLD:
        return BLOCKED
    else:
        return UNBLOCKED

def lightLevelInRoom():
    return 50

def numberOfPeopleInRoom():
    return personCount

def personEntered():
    global personCount
    personCount=personCount+1

def personLeft():
    global personCount
    if personCount > 0:
        personCount=personCount-1

def switchLight(onOrOff):
    if onOrOff == LIGHT_ON:
        GPIO.output(LEDOUT, True)
    if onOrOff == LIGHT_OFF:
        GPIO.output(LEDOUT, False)
    
def handlePersonPassed(direction):
    if direction == ROOM_ENTRANCE:
        personEntered()
        switchLight(LIGHT_ON)
    if direction == ROOM_EXIT:
        personLeft()
        if personCount == 0:
            switchLight(LIGHT_OFF)
        
def setup():
    ADC.setup(0x48)
    GPIO.setup(DO, GPIO.IN)
    GPIO.setup(LEDOUT, GPIO.OUT)
    resetSystem()

def loop():
    global lastSensorStatus
    global currentSensorStatus
    while True:
            currentSensorStatus[SENSOR_1] = sensorStatus(SENSOR_1)
            currentSensorStatus[SENSOR_2] = sensorStatus(SENSOR_2)

            if lastSensorStatus[SENSOR_1] != currentSensorStatus[SENSOR_1]:
                if currentSensorStatus[SENSOR_1] == BLOCKED:
                    if lastSensorStatus[SENSOR_2] == BLOCKED:
                        handlePersonPassed(ROOM_EXIT)

            if lastSensorStatus[SENSOR_2] != currentSensorStatus[SENSOR_2]:
                if currentSensorStatus[SENSOR_2] == BLOCKED:
                    if lastSensorStatus[SENSOR_1] == BLOCKED:
                        handlePersonPassed(ROOM_ENTRANCE)

            lastSensorStatus[SENSOR_1] = currentSensorStatus[SENSOR_1]
            lastSensorStatus[SENSOR_2] = currentSensorStatus[SENSOR_2]

            print(lastSensorStatus[SENSOR_1],lastSensorStatus[SENSOR_2]) 
            #time.sleep(0.2)

if __name__ == '__main__':
    try:
            setup()
            loop()
    except KeyboardInterrupt:
            GPIO.cleanup()
            pass    

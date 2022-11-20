#!/usr/bin/env python
# coding: utf-8

# In[ ]:


from ast import main
import random
import math
import time
import threading
import os


# In[ ]:


# Default values of signal times
defaultRed = 150
defaultYellow = 5
defaultGreen = 20
defaultMinimum = 10
defaultMaximum = 60

signals = []
noOfSignals = 4
simTime = 300       # total simulation time
timeElapsed = 0


# In[ ]:


currentGreen = 0   # Indicates which signal is green

nextGreen = (currentGreen+1) % noOfSignals

currentYellow = 0   # Indicates whether yellow signal is on or off


# Average times for vehicles to pass the intersection
carTime = 2
bikeTime = 1
rickshawTime = 2
busTime = 3
truckTime = 3


# In[ ]:


# Count of vehicles at a traffic signal
noOfCars = 0
noOfBikes = 0
noOfBuses = 0
noOfTrucks = 0
noOfRickshaws = 0
noOfLanes = 2


# In[ ]:


# Red signal time at which vehicles will be detected at a signal (when detection will start running)
detectionTime = 5


# In[ ]:


vehicles = {'right': {'road': [], 'crossed': 0}, 'down': {'road': [], 'crossed': 0},
            'left': {'road': [], 'crossed': 0}, 'up': {'road': [], 'crossed': 0}}

vehicleTypes = {0: 'car', 1: 'bus', 2: 'truck', 3: 'rickshaw', 4: 'bike'}

directionNumbers = {0: 'right', 1: 'down', 2: 'left', 3: 'up'}


# In[ ]:


class TrafficSignal:
    def __init__(self, red, yellow, green, minimum, maximum):
        self.red = red
        self.yellow = yellow
        self.green = green
        self.minimum = minimum
        self.maximum = maximum
        self.totalGreenTime = 0


# In[ ]:


class Vehicle:

    def __init__(self, vehicleClass, direction_number, direction):
        self.vehicleClass = vehicleClass
        self.direction_number = direction_number
        self.direction = direction
        self.crossed = 0
        vehicles[direction]['road'].append(self)


# In[ ]:


# Initialization of signals with default values
def initialize():

    ts1 = TrafficSignal(0, defaultYellow, defaultGreen,
                        defaultMinimum, defaultMaximum)
    signals.append(ts1)
    ts2 = TrafficSignal(ts1.red+ts1.yellow+ts1.green, defaultYellow,
                        defaultGreen, defaultMinimum, defaultMaximum)
    signals.append(ts2)
    ts3 = TrafficSignal(defaultRed, defaultYellow,
                        defaultGreen, defaultMinimum, defaultMaximum)
    signals.append(ts3)
    ts4 = TrafficSignal(defaultRed, defaultYellow,
                        defaultGreen, defaultMinimum, defaultMaximum)
    signals.append(ts4)

    repeat()


# In[ ]:


def setTime():

    global noOfCars, noOfBikes, noOfBuses, noOfTrucks, noOfRickshaws, noOfLanes
    global carTime, busTime, truckTime, rickshawTime, bikeTime

    noOfCars, noOfBuses, noOfTrucks, noOfRickshaws, noOfBikes = 0, 0, 0, 0, 0

    for i in range(len(vehicles[directionNumbers[nextGreen]]['road'])):

        vehicle = vehicles[directionNumbers[nextGreen]]['road'][i]
        if(vehicle.crossed == 0):
            vclass = vehicle.vehicleClass
            vehicle.crossed = 1

            if(vclass == 'car'):
                noOfCars += 1
            elif(vclass == 'bus'):
                noOfBuses += 1
            elif(vclass == 'truck'):
                noOfTrucks += 1
            elif(vclass == 'rickshaw'):
                noOfRickshaws += 1
            elif(vclass == 'bike'):
                noOfBikes += 1

    print("For Vehicles Going = ",
          directionNumbers[(currentGreen+1) % noOfSignals])
    print("Cars = ", noOfCars)
    print("Autos = ", noOfRickshaws)
    print("Buses = ", noOfBuses)
    print("Trucks = ", noOfTrucks)
    print("Bikes = ", noOfBikes)

    total_vehicles = noOfCars + noOfRickshaws + noOfBuses + noOfTrucks + noOfBikes

    vehicles[directionNumbers[nextGreen]]['crossed'] += total_vehicles

    greenTime = math.ceil(((noOfCars*carTime) + (noOfRickshaws*rickshawTime) + (
        noOfBuses*busTime) + (noOfTrucks*truckTime) + (noOfBikes*bikeTime))/(noOfLanes+1))

    print('Green Time: ', greenTime)
    if(greenTime < defaultMinimum):
        greenTime = defaultMinimum
    elif(greenTime > defaultMaximum):
        greenTime = defaultMaximum

    signals[(currentGreen+1) % (noOfSignals)].green = greenTime


# In[ ]:


def repeat():

    global currentGreen, currentYellow, nextGreen
    # while the timer of current green signal is not zero

    while(signals[currentGreen].green > 0):
        printStatus()
        updateValues()

        # set time of next green signal
        if(signals[(currentGreen+1) % (noOfSignals)].red == detectionTime):

            thread = threading.Thread(
                name="detection", target=setTime, args=())
            thread.daemon = True
            thread.start()

        time.sleep(1)

    currentYellow = 1   # set yellow signal on
    # while the timer of current yellow signal is not zero
    while(signals[currentGreen].yellow > 0):
        printStatus()
        updateValues()
        time.sleep(1)
    currentYellow = 0   # set yellow signal off

    # reset all signal times of current signal to default times
    signals[currentGreen].green = defaultGreen
    signals[currentGreen].yellow = defaultYellow
    signals[currentGreen].red = defaultRed

    currentGreen = nextGreen  # set next signal as green signal
    nextGreen = (currentGreen+1) % noOfSignals    # set next green signal

    # set the red time of next to next signal as (yellow time + green time) of next signal
    temp = signals[nextGreen].red
    signals[nextGreen].red = signals[currentGreen].yellow + \
        signals[currentGreen].green

    # checking if the current red timer exceeds the previous ongoing timer or not
    if(signals[nextGreen].red > temp):
        print("I will go crazy...!")

    repeat()


# In[ ]:


# Print the signal timers on cmd

def printStatus():

    for i in range(0, noOfSignals):
        if(i == currentGreen):
            if(currentYellow == 0):
                print(" GREEN TS", i+1, "-> r:",
                      signals[i].red, " y:", signals[i].yellow, " g:", signals[i].green)
            else:
                print("YELLOW TS", i+1, "-> r:",
                      signals[i].red, " y:", signals[i].yellow, " g:", signals[i].green)
        else:
            print("   RED TS", i+1, "-> r:",
                  signals[i].red, " y:", signals[i].yellow, " g:", signals[i].green)
    print()


# In[ ]:


# Update values of the signal timers after every second

def updateValues():

    for i in range(0, noOfSignals):
        if(i == currentGreen):
            if(currentYellow == 0):
                signals[i].green -= 1
                signals[i].totalGreenTime += 1
            else:
                signals[i].yellow -= 1
        else:
            signals[i].red -= 1


# In[ ]:


def generateVehicles():

    while(True):

        vehicle_type = random.randint(0, 4)

        direction_number = random.randint(0, 3)
        # direction_number = random.randint(0, 0)

        Vehicle(vehicleTypes[vehicle_type], direction_number,
                directionNumbers[direction_number])

        time.sleep(1)


# In[ ]:


def simulationTime():

    global timeElapsed, simTime
    while(True):

        timeElapsed += 1
        time.sleep(1)
        if(timeElapsed == simTime):
            # time.sleep(1)
            totalVehicles = 0
            print('Lane-wise Vehicle Counts')

            for i in range(noOfSignals):
                print('Lane', i+1, ':',
                      vehicles[directionNumbers[i]]['crossed'])
                totalVehicles += vehicles[directionNumbers[i]]['crossed']

            print('Total vehicles passed: ', totalVehicles)
            print('Total time passed: ', timeElapsed)
            print('No. of vehicles passed per unit time: ',
                  (float(totalVehicles)/float(timeElapsed)))
            os._exit(1)


# In[ ]:


class Main:

    thread1 = threading.Thread(
        name="simulationTime", target=simulationTime, args=())
    thread1.daemon = True
    thread1.start()

    thread2 = threading.Thread(
        name="initialization", target=initialize, args=())    # initialization
    thread2.daemon = True
    thread2.start()

    thread3 = threading.Thread(
        name="generateVehicles", target=generateVehicles, args=())    # Generating vehicles
    thread3.daemon = True
    thread3.start()


main()
# In[ ]:

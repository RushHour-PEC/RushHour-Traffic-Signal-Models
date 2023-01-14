#!/usr/bin/env python
# coding: utf-8

# In[1]:


import random
import math
import time
import threading
import os
import pygame
import sys
import pandas as pd
import csv


# In[2]:


# header = ['P1', 'P2', 'P3', 'P4', 'Lane1', 'Lane2', 'Lane3', 'Lane4', 'Total']
# with open('../data/4-Way-Analysis-Static-Case-11.csv', 'w', encoding='UTF8', newline='') as f:
#     writer = csv.writer(f)

#     # write the header
#     writer.writerow(header)


# In[3]:


# Default values of signal times
defaultRed = 195
defaultYellow = 5
defaultGreen = 20
defaultMinimum = 10
defaultMaximum = 60

data = []
signals = []
noOfSignals = 4
simTime = 400       # total simulation time
timeElapsed = 0


# In[4]:


currentGreen = 0   # Indicates which signal is green

nextGreen = (currentGreen+1) % noOfSignals

currentYellow = 0   # Indicates whether yellow signal is on or off


# Average times for vehicles to pass the intersection
carTime = 2
bikeTime = 1
rickshawTime = 2.5
busTime = 3
truckTime = 3


# In[5]:


# Count of vehicles at a traffic signal
noOfCars = 0
noOfBikes = 0
noOfBuses = 0
noOfTrucks = 0
noOfRickshaws = 0
noOfLanes = 2


# In[6]:


# Red signal time at which vehicles will be detected at a signal (when detection will start running)
detectionTime = 5

# speeds = {'car': 0.3375, 'bus': 0.27, 'truck': 0.27,
#           'rickshaw': 0.3, 'bike': 0.375}  # average speeds of vehicles

speeds = {'car': 2.25, 'bus': 1.8, 'truck': 1.8,
          'rickshaw': 2, 'bike': 2.5}  # average speeds of vehicles
# In[7]:


# Coordinates of start
x = {'right': [0, 0, 0], 'down': [750, 720, 692],
     'left': [1400, 1400, 1400], 'up': [602, 630, 661]}
y = {'right': [349, 375, 400], 'down': [0, 0, 0],
     'left': [488, 458, 430], 'up': [800, 800, 800]}


# Coordinates of signal image, timer, and vehicle count
signalCoods = [(530, 230), (810, 230), (810, 570), (530, 570)]
signalTimerCoods = [(530, 210), (810, 210), (810, 550), (530, 550)]
vehicleCountCoods = [(480, 210), (880, 210), (880, 550), (480, 550)]
vehicleCountTexts = ["0", "0", "0", "0"]


# Coordinates of stop lines
stopLines = {'right': 590, 'down': 330, 'left': 800, 'up': 535}
defaultStop = {'right': 580, 'down': 320, 'left': 810, 'up': 545}
stops = {'right': [580, 580, 580], 'down': [320, 320, 320],
         'left': [810, 810, 810], 'up': [545, 545, 545]}


mid = {'right': {'x': 720, 'y': 445}, 'down': {'x': 695, 'y': 460},
       'left': {'x': 680, 'y': 425}, 'up': {'x': 695, 'y': 400}}
rotationAngle = 3

# Gap between vehicles
stoppingGap = 25    # stopping gap
movingGap = 25   # moving gap


# In[8]:


vehicles = {'right': {0: [], 1: [], 2: [], 'crossed': 0}, 'down': {0: [], 1: [], 2: [], 'crossed': 0},
            'left': {0: [], 1: [], 2: [], 'crossed': 0}, 'up': {0: [], 1: [], 2: [], 'crossed': 0}}

vehicleTypes = {0: 'car', 1: 'bus', 2: 'truck', 3: 'rickshaw', 4: 'bike'}

directionNumbers = {0: 'right', 1: 'down', 2: 'left', 3: 'up'}


# In[9]:


pygame.init()
simulation = pygame.sprite.Group()


# In[10]:


class TrafficSignal:
    def __init__(self, red, yellow, green, minimum=0, maximum=0):
        self.red = red
        self.yellow = yellow
        self.green = green
        self.minimum = minimum
        self.maximum = maximum
        self.totalGreenTime = 0
        self.signalText = "--"


# In[11]:


class Vehicle(pygame.sprite.Sprite):

    def __init__(self, lane, vehicleClass, direction_number, direction, will_turn):
        pygame.sprite.Sprite.__init__(self)
        self.lane = lane
        self.vehicleClass = vehicleClass
        self.speed = speeds[vehicleClass]
        self.x = x[direction][lane]
        self.y = y[direction][lane]
        self.direction_number = direction_number
        self.direction = direction
        self.crossed = 0
        self.willTurn = will_turn
        self.turned = 0
        self.rotateAngle = 0
        vehicles[direction][lane].append(self)
        self.index = len(vehicles[direction][lane]) - 1
        path = "../images/" + direction + "/" + vehicleClass + ".png"
        self.originalImage = pygame.image.load(path)
        self.currentImage = pygame.image.load(path)

        if(direction == 'right'):

            # if more than 1 vehicle in the lane of vehicle before it has crossed stop line
            if(len(vehicles[direction][lane]) > 1 and vehicles[direction][lane][self.index-1].crossed == 0):
                self.stop = vehicles[direction][lane][self.index-1].stop - vehicles[direction][lane][self.index-1].currentImage.get_rect(
                ).width - stoppingGap         # setting stop coordinate as: stop coordinate of next vehicle - width of next vehicle - gap

            else:

                self.stop = defaultStop[direction]

            # Set new starting and stopping coordinate
            temp = self.currentImage.get_rect().width + stoppingGap
            x[direction][lane] -= temp
            stops[direction][lane] -= temp

        elif(direction == 'left'):

            if(len(vehicles[direction][lane]) > 1 and vehicles[direction][lane][self.index-1].crossed == 0):
                self.stop = vehicles[direction][lane][self.index-1].stop + \
                    vehicles[direction][lane][self.index -
                                              1].currentImage.get_rect().width + stoppingGap

            else:
                self.stop = defaultStop[direction]

            temp = self.currentImage.get_rect().width + stoppingGap
            x[direction][lane] += temp
            stops[direction][lane] += temp

        elif(direction == 'down'):

            if(len(vehicles[direction][lane]) > 1 and vehicles[direction][lane][self.index-1].crossed == 0):
                self.stop = vehicles[direction][lane][self.index-1].stop - \
                    vehicles[direction][lane][self.index -
                                              1].currentImage.get_rect().height - stoppingGap

            else:
                self.stop = defaultStop[direction]

            temp = self.currentImage.get_rect().height + stoppingGap
            y[direction][lane] -= temp
            stops[direction][lane] -= temp

        elif(direction == 'up'):

            if(len(vehicles[direction][lane]) > 1 and vehicles[direction][lane][self.index-1].crossed == 0):
                self.stop = vehicles[direction][lane][self.index-1].stop + \
                    vehicles[direction][lane][self.index -
                                              1].currentImage.get_rect().height + stoppingGap

            else:
                self.stop = defaultStop[direction]

            temp = self.currentImage.get_rect().height + stoppingGap
            y[direction][lane] += temp
            stops[direction][lane] += temp

        simulation.add(self)

    def render(self, screen):
        screen.blit(self.image, (self.x, self.y))

    def move(self):

        if(self.direction == 'right'):

            # if the image has crossed stop lines
            if(self.crossed == 0 and self.x+self.currentImage.get_rect().width > stopLines[self.direction]):

                self.crossed = 1
                vehicles[self.direction]['crossed'] += 1

            if(self.willTurn == 1):

                if(self.lane == 0):

                    if(self.crossed == 0 or self.x+self.currentImage.get_rect().width < stopLines[self.direction] + 40):

                        if((self.x+self.currentImage.get_rect().width <= self.stop or
                            (currentGreen == 0 and currentYellow == 0) or self.crossed == 1) and
                           (self.index == 0 or self.x+self.currentImage.get_rect().width < (vehicles[self.direction][self.lane][self.index-1].x - movingGap)
                                or vehicles[self.direction][self.lane][self.index-1].turned == 1)):

                            self.x += self.speed

                    else:

                        if(self.turned == 0):
                            self.rotateAngle += rotationAngle
                            self.currentImage = pygame.transform.rotate(
                                self.originalImage, self.rotateAngle)
                            self.x += 2.4
                            self.y -= 2.8
                            if(self.rotateAngle == 90):
                                self.turned = 1

                        else:
                            if(self.index == 0 or self.y-self.currentImage.get_rect().height
                               > (vehicles[self.direction][self.lane][self.index-1].y + movingGap)
                               or self.x+self.currentImage.get_rect().width
                               < (vehicles[self.direction][self.lane][self.index-1].x - movingGap)):

                                self.y -= self.speed

                elif(self.lane == 2):

                    if(self.crossed == 0 or self.x+self.currentImage.get_rect().width < mid[self.direction]['x']):

                        if((self.x+self.currentImage.get_rect().width <= self.stop or
                            (currentGreen == 0 and currentYellow == 0) or self.crossed == 1) and
                           (self.index == 0 or self.x+self.currentImage.get_rect().width < (vehicles[self.direction][self.lane][self.index-1].x - movingGap)
                                or vehicles[self.direction][self.lane][self.index-1].turned == 1)):

                            self.x += self.speed

                    else:

                        if(self.turned == 0):
                            self.rotateAngle += rotationAngle
                            self.currentImage = pygame.transform.rotate(
                                self.originalImage, -self.rotateAngle)
                            self.x += 2
                            self.y += 1.8
                            if(self.rotateAngle == 90):
                                self.turned = 1

                        else:
                            if(self.index == 0 or self.y+self.currentImage.get_rect().height
                               < (vehicles[self.direction][self.lane][self.index-1].y - movingGap)
                               or self.x+self.currentImage.get_rect().width
                               < (vehicles[self.direction][self.lane][self.index-1].x - movingGap)):

                                self.y += self.speed

            else:
                if((self.x+self.currentImage.get_rect().width <= self.stop or self.crossed == 1 or
                    (currentGreen == 0 and currentYellow == 0)) and (self.index == 0 or
                                                                     self.x+self.currentImage.get_rect().width
                                                                     < (vehicles[self.direction][self.lane][self.index-1].x - movingGap)
                                                                     or (vehicles[self.direction][self.lane][self.index-1].turned == 1))):

                    # (if the image has not reached its stop coordinate or has crossed stop line or has green signal) and (it is either the first vehicle in that lane or it is has enough gap to the next vehicle in that lane)
                    self.x += self.speed  # move the vehicle

        elif(self.direction == 'down'):

            if(self.crossed == 0 and self.y+self.currentImage.get_rect().height > stopLines[self.direction]):
                self.crossed = 1
                vehicles[self.direction]['crossed'] += 1

            if(self.willTurn == 1):

                if(self.lane == 0):

                    if(self.crossed == 0 or self.y+self.currentImage.get_rect().height < stopLines[self.direction] + 50):

                        if((self.y+self.currentImage.get_rect().height <= self.stop
                            or (currentGreen == 1 and currentYellow == 0) or self.crossed == 1)
                           and (self.index == 0 or self.y+self.currentImage.get_rect().height
                           < (vehicles[self.direction][self.lane][self.index-1].y - movingGap)
                                or vehicles[self.direction][self.lane][self.index-1].turned == 1)):

                            self.y += self.speed

                    else:
                        if(self.turned == 0):
                            self.rotateAngle += rotationAngle
                            self.currentImage = pygame.transform.rotate(
                                self.originalImage, self.rotateAngle)
                            self.x += 1.2
                            self.y += 1.8
                            if(self.rotateAngle == 90):
                                self.turned = 1

                        else:
                            if(self.index == 0 or
                               self.x + vehicles[self.direction][self.lane][self.index-1].currentImage.get_rect(
                               ).width < (vehicles[self.direction][self.lane][self.index-1].x - movingGap)
                               or self.y < (vehicles[self.direction][self.lane][self.index-1].y - movingGap)):
                                self.x += self.speed

                elif(self.lane == 2):

                    if(self.crossed == 0 or self.y+self.currentImage.get_rect().height < mid[self.direction]['y']):

                        if((self.y+self.currentImage.get_rect().height <= self.stop
                            or (currentGreen == 1 and currentYellow == 0) or self.crossed == 1)
                           and (self.index == 0 or self.y+self.currentImage.get_rect().height
                           < (vehicles[self.direction][self.lane][self.index-1].y - movingGap)
                                or vehicles[self.direction][self.lane][self.index-1].turned == 1)):

                            self.y += self.speed

                    else:
                        if(self.turned == 0):
                            self.rotateAngle += rotationAngle
                            self.currentImage = pygame.transform.rotate(
                                self.originalImage, -self.rotateAngle)
                            self.x -= 2.5
                            self.y += 2
                            if(self.rotateAngle == 90):
                                self.turned = 1

                        else:
                            if(self.index == 0 or
                               self.x - vehicles[self.direction][self.lane][self.index-1].currentImage.get_rect(
                               ).width > (vehicles[self.direction][self.lane][self.index-1].x + movingGap)
                               or self.y < (vehicles[self.direction][self.lane][self.index-1].y - movingGap)):
                                self.x -= self.speed

            else:
                if((self.y+self.currentImage.get_rect().height <= self.stop or self.crossed == 1
                    or (currentGreen == 1 and currentYellow == 0))
                   and (self.index == 0 or self.y+self.currentImage.get_rect().height
                        < (vehicles[self.direction][self.lane][self.index-1].y - movingGap)
                        or (vehicles[self.direction][self.lane][self.index-1].turned == 1))):

                    self.y += self.speed

        elif(self.direction == 'left'):

            if(self.crossed == 0 and self.x < stopLines[self.direction]):
                self.crossed = 1
                vehicles[self.direction]['crossed'] += 1

            if(self.willTurn == 1):

                if(self.lane == 0):

                    if(self.crossed == 0 or self.x > stopLines[self.direction] - 60):
                        if((self.x >= self.stop or (currentGreen == 2 and currentYellow == 0) or self.crossed == 1)
                           and (self.index == 0 or self.x - vehicles[self.direction][self.lane][self.index-1].currentImage.get_rect().width > (vehicles[self.direction][self.lane][self.index-1].x + movingGap)
                                or vehicles[self.direction][self.lane][self.index-1].turned == 1)):
                            self.x -= self.speed

                    else:
                        if(self.turned == 0):
                            self.rotateAngle += rotationAngle
                            self.currentImage = pygame.transform.rotate(
                                self.originalImage, self.rotateAngle)
                            self.x -= 1
                            self.y += 1.2
                            if(self.rotateAngle == 90):
                                self.turned = 1

                        else:
                            if(self.index == 0 or
                               self.y + vehicles[self.direction][self.lane][self.index-1].currentImage.get_rect(
                               ).height < (vehicles[self.direction][self.lane][self.index-1].y - movingGap)
                               or self.x > (vehicles[self.direction][self.lane][self.index-1].x + movingGap)):

                                self.y += self.speed

                elif(self.lane == 2):

                    if(self.crossed == 0 or self.x > mid[self.direction]['x']):
                        if((self.x >= self.stop or (currentGreen == 2 and currentYellow == 0) or self.crossed == 1)
                           and (self.index == 0 or self.x - vehicles[self.direction][self.lane][self.index-1].currentImage.get_rect().width > (vehicles[self.direction][self.lane][self.index-1].x + movingGap)
                                or vehicles[self.direction][self.lane][self.index-1].turned == 1)):
                            self.x -= self.speed

                    else:
                        if(self.turned == 0):
                            self.rotateAngle += rotationAngle
                            self.currentImage = pygame.transform.rotate(
                                self.originalImage, -self.rotateAngle)
                            self.x -= 1.8
                            self.y -= 2.5
                            if(self.rotateAngle == 90):
                                self.turned = 1

                        else:
                            if(self.index == 0 or
                               self.y - vehicles[self.direction][self.lane][self.index-1].currentImage.get_rect(
                               ).height > (vehicles[self.direction][self.lane][self.index-1].y + movingGap)
                               or self.x > (vehicles[self.direction][self.lane][self.index-1].x + movingGap)):

                                self.y -= self.speed

            else:
                if((self.x >= self.stop or self.crossed == 1 or (currentGreen == 2 and currentYellow == 0))
                   and (self.index == 0 or self.x - vehicles[self.direction][self.lane][self.index-1].currentImage.get_rect().width > (vehicles[self.direction][self.lane][self.index-1].x + movingGap)
                        or (vehicles[self.direction][self.lane][self.index-1].turned == 1))):

                    # (if the image has not reached its stop coordinate or has crossed stop line or has green signal) and (it is either the first vehicle in that lane or it is has enough gap to the next vehicle in that lane)
                    self.x -= self.speed  # move the vehicle

        elif(self.direction == 'up'):

            if(self.crossed == 0 and self.y < stopLines[self.direction]):
                self.crossed = 1
                vehicles[self.direction]['crossed'] += 1

            if(self.willTurn == 1):

                if(self.lane == 0):

                    if(self.crossed == 0 or self.y > stopLines[self.direction] - 45):
                        if((self.y >= self.stop or (currentGreen == 3 and currentYellow == 0) or self.crossed == 1)
                           and (self.index == 0 or self.y - vehicles[self.direction][self.lane][self.index-1].currentImage.get_rect().height > (vehicles[self.direction][self.lane][self.index-1].y + movingGap)
                                or vehicles[self.direction][self.lane][self.index-1].turned == 1)):

                            self.y -= self.speed

                    else:
                        if(self.turned == 0):
                            self.rotateAngle += rotationAngle
                            self.currentImage = pygame.transform.rotate(
                                self.originalImage, self.rotateAngle)
                            self.x -= 2
                            self.y -= 1.5
                            if(self.rotateAngle == 90):
                                self.turned = 1
                        else:
                            if(self.index == 0 or self.x - vehicles[self.direction][self.lane][self.index-1].currentImage.get_rect().width > (vehicles[self.direction][self.lane][self.index-1].x + movingGap)
                               or self.y > (vehicles[self.direction][self.lane][self.index-1].y + movingGap)):
                                self.x -= self.speed

                elif(self.lane == 2):

                    if(self.crossed == 0 or self.y > mid[self.direction]['y']):
                        if((self.y >= self.stop or (currentGreen == 3 and currentYellow == 0) or self.crossed == 1)
                           and (self.index == 0 or self.y - vehicles[self.direction][self.lane][self.index-1].currentImage.get_rect().height > (vehicles[self.direction][self.lane][self.index-1].y + movingGap)
                                or vehicles[self.direction][self.lane][self.index-1].turned == 1)):

                            self.y -= self.speed

                    else:
                        if(self.turned == 0):
                            self.rotateAngle += rotationAngle
                            self.currentImage = pygame.transform.rotate(
                                self.originalImage, -self.rotateAngle)
                            self.x += 1
                            self.y -= 1
                            if(self.rotateAngle == 90):
                                self.turned = 1
                        else:
                            if(self.index == 0 or self.x + vehicles[self.direction][self.lane][self.index-1].currentImage.get_rect().width < (vehicles[self.direction][self.lane][self.index-1].x - movingGap)
                               or self.y > (vehicles[self.direction][self.lane][self.index-1].y + movingGap)):
                                self.x += self.speed
            else:
                if((self.y >= self.stop or self.crossed == 1 or (currentGreen == 3 and currentYellow == 0))
                   and (self.index == 0 or self.y - vehicles[self.direction][self.lane][self.index-1].currentImage.get_rect().height > (vehicles[self.direction][self.lane][self.index-1].y + movingGap)
                        or (vehicles[self.direction][self.lane][self.index-1].turned == 1))):

                    self.y -= self.speed


# In[12]:


# Initialization of signals with default values
def initialize():

    # static system
    ts1 = TrafficSignal(0, 5, 60)
    signals.append(ts1)
    ts2 = TrafficSignal(65, 5, 60)
    signals.append(ts2)
    ts3 = TrafficSignal(130, 5, 60)
    signals.append(ts3)
    ts4 = TrafficSignal(195, 5, 60)
    signals.append(ts4)

    repeat()


# In[13]:


def setTime():

    global noOfCars, noOfBikes, noOfBuses, noOfTrucks, noOfRickshaws, noOfLanes
    global carTime, busTime, truckTime, rickshawTime, bikeTime

    noOfCars, noOfBuses, noOfTrucks, noOfRickshaws, noOfBikes = 0, 0, 0, 0, 0

    for i in range(0, 3):

        for j in range(len(vehicles[directionNumbers[nextGreen]][i])):

            vehicle = vehicles[directionNumbers[nextGreen]][i][j]

            if(vehicle.crossed == 0):
                vclass = vehicle.vehicleClass

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

#     print("For Vehicles Going = ",directionNumbers[(currentGreen+1)%noOfSignals])
#     print("Cars = ",noOfCars)
#     print("Autos = ",noOfRickshaws)
#     print("Buses = ",noOfBuses)
#     print("Trucks = ",noOfTrucks)
#     print("Bikes = ",noOfBikes)

#     total_vehicles = noOfCars + noOfRickshaws + noOfBuses + noOfTrucks + noOfBikes

#     vehicles[directionNumbers[nextGreen]]['crossed'] += total_vehicles

    ############################ not for static cases #############################
#     greenTime = math.ceil(((noOfCars*carTime) + (noOfRickshaws*rickshawTime) + (
#         noOfBuses*busTime) + (noOfTrucks*truckTime) + (noOfBikes*bikeTime))/(noOfLanes+1))

#     print('Green Time: ', greenTime)
#     if(greenTime < defaultMinimum):
#         greenTime = defaultMinimum
#     elif(greenTime > defaultMaximum):
#         greenTime = defaultMaximum

#     signals[(nextGreen) % (noOfSignals)].green = greenTime
#     buffer = defaultMaximum - greenTime

#     signals[(nextGreen + 1) % (noOfSignals)].red -= buffer
#     signals[(nextGreen + 2) % (noOfSignals)].red -= buffer


# In[14]:


def repeat():

    global currentGreen, currentYellow, nextGreen

    # while the timer of current green signal is not zero
    while(signals[currentGreen].green > 0):
        printStatus()
        updateValues()

#         set time of next green signal
        if(signals[(currentGreen+1) % (noOfSignals)].red == detectionTime):

            thread = threading.Thread(
                name="detection", target=setTime, args=())
            thread.daemon = True
            thread.start()

        time.sleep(1)

    currentYellow = 1   # set yellow signal on
    for i in range(0, 3):
        # for all the lanes with current yellow signal
        stops[directionNumbers[currentGreen]
              ][i] = defaultStop[directionNumbers[currentGreen]]
        for vehicle in vehicles[directionNumbers[currentGreen]][i]:
            vehicle.stop = defaultStop[directionNumbers[currentGreen]]

    # while the timer of current yellow signal is not zero
    while(signals[currentGreen].yellow > 0):
        printStatus()
        updateValues()
        time.sleep(1)
    currentYellow = 0   # set yellow signal off

    # reset all signal times of current signal to default times
    ########### not for static case ###############
    # signals[currentGreen].green = defaultGreen
    # signals[currentGreen].yellow = defaultYellow
    # signals[currentGreen].red = defaultRed

    signals[currentGreen].green = defaultMaximum
    signals[currentGreen].yellow = defaultYellow
    signals[currentGreen].red = defaultRed

    currentGreen = nextGreen  # set next signal as green signal
    nextGreen = (currentGreen+1) % noOfSignals    # set next green signal

    ############# not for static cases #########################
    # set the red time of next to next signal as (yellow time + green time) of next signal
#     temp = signals[nextGreen].red
#     signals[nextGreen].red = signals[currentGreen].yellow + signals[currentGreen].green

#     # checking if the current red timer exceeds the previous ongoing timer or not
#     if(signals[nextGreen].red > temp):
#         print("I will go crazy...!")

    repeat()


# In[15]:


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


# In[16]:


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


# In[17]:


def generateVehicles():

    global distribution
    while(True):

        vehicle_type = random.randint(0, 4)

        lane_number = random.randint(0, 2)

        will_turn = 0

        # deciding whether the vehicle will turn or not
        if(lane_number == 2 or lane_number == 0):
            temp = random.randint(0, 5)
            if(temp < 3):
                will_turn = 1
            elif(temp < 6):
                will_turn = 0

        # deciding the direction_number from
        # a range of values from 1 to 1000
        temp = random.randint(0, 999)
        direction_number = 0
        distribution = [200, 400, 500, 1000]

        if(temp < distribution[0]):
            direction_number = 0
        elif(temp < distribution[1]):
            direction_number = 1
        elif(temp < distribution[2]):
            direction_number = 2
        elif(temp < distribution[3]):
            direction_number = 3

        Vehicle(lane_number, vehicleTypes[vehicle_type], direction_number,
                directionNumbers[direction_number], will_turn)

        time.sleep(1)


# In[18]:


def simulationTime():

    global timeElapsed, simTime
    while(True):

        timeElapsed += 1
        time.sleep(1)
        if(timeElapsed == simTime):
            totalVehicles = 0
            print('Lane-wise Vehicle Counts')

            data.append(distribution[0]/1000)
            data.append((distribution[1] - distribution[0])/1000)
            data.append((distribution[2] - distribution[1])/1000)
            data.append((distribution[3] - distribution[2])/1000)

            for i in range(noOfSignals):
                print('Lane', i+1, ':',
                      vehicles[directionNumbers[i]]['crossed'])
                data.append(vehicles[directionNumbers[i]]['crossed'])
                totalVehicles += vehicles[directionNumbers[i]]['crossed']

            data.append(totalVehicles)

            with open('../data/4-Way-Analysis-Static-Case-11.csv', 'a', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(data)

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

    # Colours
    black = (0, 0, 0)
    white = (255, 255, 255)

    # Screensize
    screenWidth = 1400
    screenHeight = 800
    screenSize = (screenWidth, screenHeight)

    # Setting background image i.e. image of intersection
    background = pygame.image.load(
        '../images/intersection/intersection-4-Way.png')

    screen = pygame.display.set_mode(screenSize)
    pygame.display.set_caption("TRAFFIC SIMULATION")

    icon = pygame.image.load('../images/Icons/rush.png')
    pygame.display.set_icon(icon)

    # Loading signal images and font
    redSignal = pygame.image.load('../images/signals/red.png')
    yellowSignal = pygame.image.load('../images/signals/yellow.png')
    greenSignal = pygame.image.load('../images/signals/green.png')
    font = pygame.font.Font(None, 30)

    thread3 = threading.Thread(
        name="generateVehicles", target=generateVehicles, args=())    # Generating vehicles
    thread3.daemon = True
    thread3.start()

    FPS = 60
    clock = pygame.time.Clock()
    while True:

        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()

        screen.blit(background, (0, 0))

        # display signal and set timer according to current status: green, yellow, or red
        for i in range(0, noOfSignals):
            if(i == currentGreen):
                if(currentYellow == 1):
                    if(signals[i].yellow == 0):
                        signals[i].signalText = "STOP"
                    else:
                        signals[i].signalText = signals[i].yellow
                    screen.blit(yellowSignal, signalCoods[i])
                else:
                    if(signals[i].green == 0):
                        signals[i].signalText = "SLOW"
                    else:
                        signals[i].signalText = signals[i].green
                    screen.blit(greenSignal, signalCoods[i])
            else:
                if(signals[i].red <= 15):
                    if(signals[i].red == 0):
                        signals[i].signalText = "GO"
                    else:
                        signals[i].signalText = signals[i].red
                else:
                    signals[i].signalText = "---"
                screen.blit(redSignal, signalCoods[i])
        signalTexts = ["", "", "", ""]

        for i in range(0, noOfSignals):
            signalTexts[i] = font.render(
                str(signals[i].signalText), True, white, black)
            screen.blit(signalTexts[i], signalTimerCoods[i])
            displayText = vehicles[directionNumbers[i]]['crossed']
            vehicleCountTexts[i] = font.render(
                str(displayText), True, black, white)
            screen.blit(vehicleCountTexts[i], vehicleCountCoods[i])

        timeElapsedText = font.render(
            ("Time Elapsed: "+str(timeElapsed)), True, black, white)
        screen.blit(timeElapsedText, (1100, 50))

        for vehicle in simulation:
            screen.blit(vehicle.currentImage, [vehicle.x, vehicle.y])
            vehicle.move()
        pygame.display.update()


Main()


# In[ ]:


# In[ ]:

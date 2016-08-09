#!/usr/bin/env python

import serial
import time
import os
import psutil
from time import gmtime, strftime, localtime
from decimal import Decimal
from datetime import timedelta

lcd = serial.Serial("/dev/serial/by-id/usb-Silicon_Labs_CP2102_USB_to_UART_Bridge_Controller_0001-if00-port0", 9600)

isLcdLit = True
width = 20


def setBacklightOff():
   lcd.write("\xFE")
   lcd.write("\x46")
   lcd.write("\xFE")
   lcd.write("\x46")
   isLcdLit = False
   time.sleep(0.1)
def setBacklightOn():
   lcd.write("\xFE")
   lcd.write("\x42")
   lcd.write("\x00")
   lcd.write("\xFE")
   lcd.write("\x42")
   lcd.write("\x00")
   isLcdLit = True
   time.sleep(0.1)

def writeLine( str, line):
   lcd.write("\xFE")
   lcd.write("\x47")
   lcd.write("\x01")
   lcd.write(chr(line))   
   lcd.write(str.ljust(width))
   time.sleep(0.1)

def generateGraph(name, max, value, maxCharWidth):
   graphStartStr		= name.upper() + "["
   graphEndStr			= "]"
   allowedGraphLength		= maxCharWidth - (len(graphStartStr) + len(graphEndStr))
   numberOfCharactersForGraph	= int((value * allowedGraphLength) / max)
   squareCharacter		= "".join( chr(255) )
   outputString			= graphStartStr + ( squareCharacter * numberOfCharactersForGraph).ljust(allowedGraphLength) + graphEndStr
   return outputString

def generateHddUsageGraph(mountPoint, name):
   st				= os.statvfs(mountPoint)
   totalDiskSpace               = round(Decimal(st.f_frsize * st.f_blocks) / 1073741824 / 1024, 2)
   freeDiskSpace                = round(Decimal(st.f_frsize * st.f_bfree) / 1073741824 / 1024, 2) 
   usedDiskSpace		= totalDiskSpace - freeDiskSpace	
   return generateGraph(name, totalDiskSpace, usedDiskSpace, width/2)
   

def generateCpuUsageGraph():
   return generateGraph("CPU",100,psutil.cpu_percent(), width/2)

def generateMemUsageGraph():
   mem                          = psutil.virtual_memory()
   return generateGraph("MEM",100,mem.percent, width/2)

def generateTemp():
   f = open('/sys/class/thermal/thermal_zone0/temp','r')
   temp = int(f.read())
   return str(temp/1000)+"C"

def generateUptime():
   with open('/proc/uptime', 'r') as f:
      uptime_seconds = float(f.readline().split()[0])
      uptime_string = str(timedelta(seconds = uptime_seconds))
   return uptime_string

def isPowerSaving():
   powerSaveStartHour = 23
   powerSaveEndHour = 7
   currentHour = int(strftime("%H", localtime()))
   return ( currentHour > powerSaveStartHour or currentHour < powerSaveEndHour )
   


#/sys/class/thermal/thermal_zone0/temp   

setBacklightOn()


while True :

   if isPowerSaving():
      if isLcdLit :
         setBacklightOff()      
   else :
      if isLcdLit == False:
         setBacklightOn()
   writeLine( strftime("%d %b %Y %H:%M:%S", localtime())   ,1)
   writeLine( generateHddUsageGraph("/media/sg","SGT") + generateHddUsageGraph("/media/wd", "WDG"), 2)
   writeLine( "TEMP:" + generateTemp() + " UP: " + generateUptime(), 4)
   writeLine( generateCpuUsageGraph() + generateMemUsageGraph(), 3)
   time.sleep(0.5)

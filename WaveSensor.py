
import spidev
from time import sleep, strftime, time
import os
import RPi.GPIO as GPIO
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import sqlite3 as lite
import sys

GPIO.setmode(GPIO.BOARD) # the physical pin number scheme

# Open SPI bus
spi = None
spi = spidev.SpiDev()
spi.open(0,0)
spi.max_speed_hz=1000000

# Global variables
light_channel = 0
flag = True
delay = 0.5
x_len = 200         # Number of points to display
y_range = [20, 80]  # Range of possible Y values to display, ldr never goes beyond these values
dbName = "sensorsData.db"

# Create figure for plotting
fig = plt.figure()
ax = fig.add_subplot(1, 1, 1)
time_array = list(range(0, 200))
light_array = [0] * x_len
ax.set_ylim(y_range)

# Create a blank line. to update the line in animate
line, = ax.plot(time_array, light_array)


# Function to read SPI data from MCP3008 chip
def ReadChannel(channel):
  adc = spi.xfer2([1,(8+channel)<<4,0])
  data = ((adc[1]&3) << 8) + adc[2]
  return data

# Function to convert data to light percentage
def ConvertLight(data,places):
  vol = (data / float(1023))*100
  vol = round(vol,places)
  return vol

# function for monitoring 
def analogMonitor():
  light_level = ReadChannel(light_channel)
  light_volts = ConvertLight(light_level,2)
  # print("light = ", light_volts)
  return light_volts

# function for csv file to use with Database
def writeCSV(light):
  with open("/home/pi/Desktop/EEE/ES-ProjectB-IoT-Wave-Sensor/light.csv", "a") as log:    
    log.write("{0},{1}\n".format(strftime("%H:%M:%S"),str(light)))
    
# function to insert data to table
def logData(light):
	conn  = lite.connect(dbName)
	curs  = conn.cursor()
	curs.execute("INSERT INTO Light_Data VALUES(datetime('now'),(?))", (light,))
	conn.commit()
	conn.close()
	
# Function to display database
def displayData():
	conn=sqlite3.connect(dbname)
	curs=conn.cursor()
	print ("\nEntire database contents:\n")
	for row in curs.execute("SELECT * FROM Light_Data"):
		print (row)
	conn.close()

# This function is called periodically from FuncAnimation in matplot
#  in real time, live animation of graph
def animate(i, light_array):
    light = analogMonitor()
    
    light_array.append(light)
    light_array = light_array[-x_len:]

    line.set_ydata(light_array)

    return line,

# Format plot
plt.title("Wave Sensor Graph")
plt.ylabel("Light Intensity ( % )")
plt.xlabel("samples")

# Set up plot to call animate() function periodically
#ani = animation.FuncAnimation(fig, animate, fargs=(light_array,), interval=50, blit=True)
def main():
	for i in range(0,5):
		logData(analogMonitor())
		sleep(1)
	displayData()
	  
try:
	main()
	#add_data(analogMonitor())
    #plt.show()
        
except KeyboardInterrupt:
    spi.close()
    GPIO.cleanup()

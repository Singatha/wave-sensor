from datetime import datetime
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
import io

from flask import Flask, render_template, send_file, make_response, request
app = Flask(__name__)

import sqlite3
conn=sqlite3.connect('../sensorsData.db',check_same_thread=False)
curs=conn.cursor()

# Retrieve LAST data from database
def getLastData():
	for row in curs.execute("SELECT * FROM Light_Data ORDER BY timestamp DESC LIMIT 1"):
		time = str(row[0])
		light = row[1]
	#conn.close()
	return time, light

# Get 'x' samples of historical data
def getHistData (numSamples):
	curs.execute("SELECT * FROM Light_Data ORDER BY timestamp DESC LIMIT "+str(numSamples))
	data = curs.fetchall()
	dates = []
	lights = []
	
	for row in reversed(data):
		dates.append(row[0])
		lights.append(row[1])
		lights = testData(lights)
	return dates, lights

# Test data for cleanning possible "out of range" values
def testData(lights):
	n = len(lights)
	for i in range(0, n-1):
		if (lights[i] < 0 or lights[i] >100):
			lights[i] = lights[i-2]
	return lights

# Get Max number of rows (table size)
def maxRowsTable():
	for row in curs.execute("select COUNT(light) FROM Light_Data"):
		maxNumberRows=row[0]
	return maxNumberRows

# Get sample frequency in minutes
def freqSample():
	times, lights = getHistData (2)
	fmt = '%Y-%m-%d %H:%M:%S'
	tstamp0 = datetime.strptime(times[0], fmt)
	tstamp1 = datetime.strptime(times[1], fmt)
	freq = tstamp1-tstamp0
	freq = int(round(freq.total_seconds()/60))
	return (freq)

# define and initialize global variables
global numSamples
numSamples = maxRowsTable()
if (numSamples > 101):
        numSamples = 100

global freqSamples
freqSamples = freqSample()

global rangeTime
rangeTime = 100
				
# main route 
@app.route("/")
def index():
	time, light = getLastData()
	templateData = {
	  'time'		: time,
      'light'		: light,
      'freq'		: freqSamples,
      'rangeTime'	: rangeTime
	}
	return render_template('index.html', **templateData)

@app.route('/', methods=['POST'])
def my_form_post():
    global numSamples 
    global freqSamples
    global rangeTime
    rangeTime = int (request.form['rangeTime'])
    if (rangeTime < freqSamples):
        rangeTime = freqSamples + 1
    numSamples = rangeTime//freqSamples
    numMaxSamples = maxRowsTable()
    if (numSamples > numMaxSamples):
        numSamples = (numMaxSamples-1)
    
    time, light  = getLastData()
    
    templateData = {
	  'time'		: time,
      'light'		: light,
      'freq'		: freqSamples,
      'rangeTime'	: rangeTime
	}
    return render_template('index.html', **templateData)
	
@app.route('/plot/light')
def plot_light():
	times, lights = getHistData(numSamples)
	ys = lights
	fig = Figure()
	axis = fig.add_subplot(1, 1, 1)
	axis.set_title("Wave Sensor")
	axis.set_ylabel("light intensity [%]")
	axis.set_xlabel("Samples")
	axis.grid(True)
	xs = range(numSamples)
	axis.plot(xs, ys)
	canvas = FigureCanvas(fig)
	output = io.BytesIO()
	canvas.print_png(output)
	response = make_response(output.getvalue())
	response.mimetype = 'image/png'
	return response
	
if __name__ == "__main__":
	app.run(host='0.0.0.0', port=80, debug=True)

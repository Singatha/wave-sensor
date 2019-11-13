import sqlite3
from flask import Flask, render_template, request

app = Flask(__name__)

# Retrieve data from database
def getData():
	conn=sqlite3.connect('../sensorsData.db')
	curs=conn.cursor()
	for row in curs.execute("SELECT * FROM Light_Data ORDER BY timestamp DESC LIMIT 1"):
		time  = str(row[0])
		light = row[1]
	conn.close()
	return time, light
	
# main route 
@app.route("/")
def index():	
	time, light = getData()
	templateData = {
		'time': time,
		'light': light
	}
	
	return render_template('index.html', **templateData)
if __name__ == "__main__":
	app.run(host='0.0.0.0', port=80, debug=False)

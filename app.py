from flask import Flask, render_template
from flask import request
import json
from data import Articles
import requests
from datetime import datetime

app = Flask(__name__)

Articles = Articles();

app.debug=True

@app.route('/')
def index():
	return render_template('home.html')
@app.route('/about')
def about():
	return render_template('about.html')

@app.route('/articles')
def articles():
	return render_template('articles.html', articles = Articles)

@app.route('/article/<string:id>/')
def article(id):
	return render_template('article.html', id = id)

@app.route('/joke', methods=['GET', 'POST'])
def joke():
	#variables created as empty strings as we'll be getting back some string data from the url.
	url = 'https://official-joke-api.appspot.com/jokes/programming/random'
	resp = requests.get(url)
	setup = resp.json()[0]['setup']
	punchline = resp.json()[0]['punchline']

	return render_template('joke.html', setup = setup, punchline = punchline)

'''testing api data'''
@app.route('/traintime', methods=['GET', 'POST'])
def traintime():
	#variables created as empty strings as we'll be getting back some string data from the url.
	station = '120S'
	url = 'http://mtaapi.herokuapp.com/api?id='+station
	resp = requests.get(url);
	times = resp.json()['result']['arrivals']
	times.sort() #sorts the long list
	unique_times = [] #creates an empty array to store unique values

	#getting time... can we filter for current time?
	now = datetime.now()
	current_time = now.strftime("%H:%M:%S")

	counter = 0; 

	for time in times:
		#checks to see if the time is already in the unique_times list
		#gets rid of the 24 hour from the data which does not exist since midnight is 00.
		if time not in unique_times and not (time[0]+time[1] == '24'):
			#how to check against the current time to get values of the same hour or greater than...
			if time >= current_time and counter < 10:
				unique_times.append(time)
				counter+=1

	times = unique_times #resets the value of times to the value of unique_times.




	name = resp.json()['result']['name']
	
	return render_template('traintime.html', times = times, name=name, current_time = current_time)


if __name__ == '__main__':
	 app.run(); #host and port can be added into parameters


from flask import Flask, render_template, flash, redirect, url_for, session, logging
from flask import request
from flask_mysqldb import MySQL
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from passlib.hash import sha256_crypt 
import json
from data import Articles
import requests
from datetime import datetime
from dbconfig import dbConfig
app = Flask(__name__)

creds = dbConfig(); #using git ignore to keep credentials secret
#print(creds)

#config MySQL
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] =  creds[0] 
app.config['MYSQL_PASSWORD'] = creds[1] 
app.config['MYSQL_DB'] = creds[2] 
app.config['MYSQL_CURSORCLASS'] = 'DictCursor' #sets to dictionary

#init mySQL
mysql = MySQL(app)

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
	#articles are found in data.py, def Articles() function returns a dictionary of articles.
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

@app.route('/stations', methods=['GET', 'POST'])
def stations():
	url = 'http://mtaapi.herokuapp.com/stations' #the url for the stations list
	resp = requests.get(url)
	stations = resp.json()['result'] #list with dictionaries inside

	#sorting magic goes here			
	stations =	sorted(stations, key = lambda d: d['name']) 

	return render_template('stations.html', stations = stations)

'''getting api data on a specific station -- add <string:id> to this like article's above'''
@app.route('/traintime/<string:id>', methods=['GET', 'POST'])
def traintime(id):
	# if id != '':
		station = id 
		url = 'http://mtaapi.herokuapp.com/api?id='+station #ex: 120S
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
		
		return render_template('traintime.html', times = times, name = name, current_time = current_time)
#how do I render a different template if there is no id? or tell the user on the page that an id is needed

#need to create a class for each form

class RegisterForm(Form):
	name = StringField('name', [validators.Length(min=1, max=50)])
	username = StringField('Username', [validators.Length(min=6, max=20)])
	email = StringField('Email', [validators.Length(min=6, max=256)])
	password = PasswordField('Password', [
		validators.DataRequired(),
		validators.EqualTo('confirm', message = 'Passwords do not match' )
	])
	confirm = PasswordField('Confirm Password')

@app.route('/register', methods=['GET', 'POST'])
def register():
	form = RegisterForm(request.form)
	if request.method == 'POST' and form.validate():
		print('method post and form is valid')	
		name = form.name.data
		email = form.email.data
		username = form.username.data
		password = sha256_crypt.hash(str(form.password.data))

		# create cursor
		cur = mysql.connection.cursor()
		#write the query
		cur.execute("INSERT INTO users(name, email, username, password) VALUES(%s, %s, %s, %s)", (name, email, username, password))

		#send to db
		mysql.connection.commit()

		#close the connection
		cur.close()

		flash('You are now registered and can log in.', 'success')
		#redirect(url_for('index'))


	return render_template('register.html', form=form)

if __name__ == '__main__':
	 app.secret_key='secret123'
	 app.run(); #host and port can be added into parameters


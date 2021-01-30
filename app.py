from flask import Flask, render_template, flash, redirect, url_for, session, logging
from flask import request
from flask_mysqldb import MySQL
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from passlib.hash import sha256_crypt 
import json
#from data import Articles # do not need to import articles once db is connected.
import requests
from datetime import datetime
from dbconfig import dbConfig
from dbconfig import secretKey
from functools import wraps 



app = Flask(__name__)

creds = dbConfig() #using git ignore to keep db credentials secret
print(secretKey())

#config MySQL
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] =  creds[0] 
app.config['MYSQL_PASSWORD'] = creds[1] 
app.config['MYSQL_DB'] = creds[2] 
app.config['MYSQL_CURSORCLASS'] = 'DictCursor' #sets to dictionary

#init mySQL
mysql = MySQL(app)

#Articles = Articles(); #not needed once db is connected.

app.debug=True

@app.route('/')
def index():
	return render_template('home.html')

@app.route('/about', methods=['GET', 'POST'])
def about(): 
	return render_template('about.html')

@app.route('/articles')
def articles():
	#a dictionary of articles are found in data.py, def Articles() function returns a dictionary of articles.
	cur = mysql.connection.cursor();
	#getarticles
	result = cur.execute("SELECT * FROM articles");
	articles = cur.fetchall() #fetches in dictionary form because of DictCursor

	if result > 0: # we have rows of data
		return render_template('articles.html', articles = articles)
	else:
		msg = 'No Articles Found.'
		return render_template('articles.html', msg=msg)		

	cur.close()


	return render_template('articles.html', articles = Articles)

@app.route('/article/<string:id>/')
def article(id):
	cur = mysql.connection.cursor();
	#get article
	result = cur.execute("SELECT * FROM articles WHERE id = %s", [id]);
	article = cur.fetchone() #fetches in dictionary form because of DictCursor

	if result > 0: # we have rows of data
		return render_template('article.html', article = article)
	else:
		msg = 'Your article is not found.'
		return render_template('article.html', msg=msg)		

	cur.close()	
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

	#flash('You need a station id in order to access times.', 'danger')
		
	return render_template('traintime.html', times = times, name = name, current_time = current_time)
	#how do I render a different template if there is no id? or tell the user on the page that an id is needed

#need to create a class for each form for the WTForms to work

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
	#this is a self parsing form.
	if request.method == 'POST' and form.validate():
		#print('method post and form is valid')	
		name = form.name.data
		email = form.email.data
		username = form.username.data
		password = sha256_crypt.hash(str(form.password.data))

		# create cursor
		cur = mysql.connection.cursor()
		#write the query. the %s are string replacements placeholders for the variables that follow: 
		cur.execute("INSERT INTO users(name, email, username, password) VALUES(%s, %s, %s, %s)", (name, email, username, password))

		#send to db
		mysql.connection.commit()

		#close the connection
		cur.close()

		#not sure why this worked the first time and no times after.
		flash('You are now registered and can log in.', 'success')

		#this redirect is not working either....
		return redirect(url_for('index'))

	return render_template('register.html', form=form)

#user login
@app.route('/login', methods=['GET', 'POST'])
def login():
	if request.method == 'POST':
		#get form fields
		username = request.form['username']
		password_candidate = request.form['password']

		#create cursor
		cur = mysql.connection.cursor()

		#get user by username
		result = cur.execute("SELECT * FROM users WHERE username = %s", [username])
		#by using fetchone, we don't have to say LIMIT 1 in this query

		if result > 0:
			#get stored hash - fetchone as a method only gets the first match.
			#this means usernames should be unique
			data = cur.fetchone()
			password = data['password']

			#compare passwords
			if sha256_crypt.verify(password_candidate, password):
				app.logger.info('password match')
				#passed
				session['logged_in'] = True #just like PHP
				session['username'] = username 

				flash('you are now logged in', 'success')
				return redirect(url_for('dashboard'))
			else:
				app.logger.info('no password match')	
				error = 'invalid login'
				return render_template('login.html', error=error)		
			#close connection
			cur.close()		
		else:
			error = 'Username not found'
			return render_template('login.html', error=error)		

	return render_template('login.html')

#check if user logged in
def is_logged_in(f):
	@wraps(f)
	def wrap(*args, **kwargs):
		if 'logged_in' in session:
			return f(*args, **kwargs)
		else:
			flash('Unauthorized, please login', 'danger')
			return redirect(url_for('login'))
	return wrap		

@app.route('/dashboard')
@is_logged_in
def dashboard():
	cur = mysql.connection.cursor();
	#getarticles
	result = cur.execute("SELECT * FROM articles");
	articles = cur.fetchall() #fetches in dictionary form because of DictCursor

	if result > 0: # we have rows of data
		return render_template('dashboard.html', articles = articles)
	else:
		msg = 'No Articles Found.'
		return render_template('dashboard.html', msg=msg)		

	cur.close()
	

@app.route('/logout')
@is_logged_in
def logout():
	session.clear()
	flash('You are now logged out.', 'success')
	return redirect(url_for('login'))

#this is used in both the adding and the editing articles
class ArticleForm(Form):
	title = StringField('Title', [validators.Length(min=1, max=200)])
	body = TextAreaField('Body', [validators.Length(min=30)])


@app.route('/add_article', methods=['GET', 'POST'])
@is_logged_in
def add_article():
	form = ArticleForm(request.form)
	if request.method == 'POST' and form.validate():
		title = form.title.data
		body = form.body.data

		cur = mysql.connection.cursor()

		cur.execute("INSERT INTO articles(title, body, author) VALUES (%s,%s,%s)", (title, body, session['username']))
		mysql.connection.commit()
		cur.close()

		flash('Article Created', 'success')

		return redirect(url_for('dashboard'))
	return render_template('add_article.html', form=form)	


#################### me testing my learning ######################
@app.route('/test', methods=['GET', 'POST'])
def test():
	if request.method == 'POST':
		#get form fields	
		#db fields on users_ext are:
		#name, email, username, password, register_date, phone, bio, age, birthday
		#required fields are: name, email, password, phone
		name = request.form['name']
		username = request.form['user_name']
		email = request.form['user_email']
		phone = request.form['phone']
		password = request.form['password']
		
		print(name)
		print(username)
		print(email)
		print(password)
		print(phone)

		password = sha256_crypt.hash(str(password))

		#create cursor
		cur = mysql.connection.cursor()
		#write the query. the %s are string replacements placeholders for the variables that follow: 
		cur.execute("INSERT INTO users_ext(name, email, username, password, phone) VALUES(%s, %s, %s, %s, %s)", (name, email, username, password, phone))

		#send to db
		mysql.connection.commit()

		#close the connection
		cur.close()

		flash('This was successful', 'success')

		#this redirect finally worked
		return redirect(url_for('index'))

	return render_template('form_test2.html')


#db display stuff... ?
@app.route('/dbstuff', methods=['GET', 'POST'])
def dbstuff():
	cur = mysql.connection.cursor()
	#this line creates a table for future reference - table has been created.
	#cur.execute("CREATE TABLE articles (id INT AUTO_INCREMENT PRIMARY KEY, title VARCHAR(100), author VARCHAR(100), body TEXT, create_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP)")


	cur.execute("SHOW TABLES")

	for x in cur:
  		print(x)

	#send to db
	mysql.connection.commit()

	#close the connection
	cur.close()

	#if result is not null:
	#	flash('This was successful', 'success')

	return render_template('dbstuff.html')

if __name__ == '__main__':
	 app.secret_key = secretKey() #make a better secret key and put this in creds.
	 app.run(); #host and port can be added into parameters


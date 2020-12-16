
from flask import Flask, render_template
from flask import request
import json
from data import Articles 

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
	url = 'https://official-joke-api.appspot.com/jokes/programming/random'
	resp = requests.get(url)
	'''
	tried resp=requests.get(url) got following error:
	NameError: name 'requests' is not defined (line 31 )

	tried resp=request.get(url) got following error:
	AttributeError: 'Request' object has no attribute 'get'
	this looks like a better error to me because it is at least returning an object.

	tried resp = request.json.get(url)
	AttributeError: 'NoneType' object has no attribute 'get'

	tried resp = request.json().get(url)
	TypeError: 'NoneType' object is not callable

	'''
	setup = resp.json()[0]['setup']
	punchline = resp.json()[0]['punchline']

	return render_template('joke.html', setup = setup, punchline = punchline)

	''' 
	#this is not working either
	j_string = resp.json()
	setup = j_string[0].setup
	punchline = j_string[0].punchline
	'''

	'''		
	#is there more than one item? No... then why the loop?
	for item in resp.json():
		setup = item['setup']
		punchline = item['punchline'] 
	'''

if __name__ == '__main__':
	 app.run(); #host and port can be added into parameters


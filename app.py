
from flask import Flask, render_template
from flask import request
import json
from data import Articles
import requests

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


if __name__ == '__main__':
	 app.run(); #host and port can be added into parameters


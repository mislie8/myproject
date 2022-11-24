import pymysql
pymysql.install_as_MySQLdb()
import MySQLdb
from flask import Flask, render_template, request
import pandas as pd
import numpy as np
import pickle
import matplotlib.pyplot as plt
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import train_test_split
from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re

app = Flask(__name__)

app.secret_key = 'yannimonamour'

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'Mis2013#'
app.config['MYSQL_DB'] = 'hyperapp'

mysql = MySQL(app)

model = pickle.load(open('model.pkl', 'rb'))

@app.route("/")

@app.route('/login', methods =['GET', 'POST'])
def login():
	msg = ''
	if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
		username = request.form['username']
		password = request.form['password']
		cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
		cursor.execute('SELECT * FROM tablelog WHERE username = % s AND password = % s', (username, password, ))
		log = cursor.fetchone()
		if log:
			session['loggedin'] = True
			session['id'] = log['id']
			session['username'] = log['username']
			msg = 'Logged in successfully !'
			return render_template('form.html', msg = msg)
		else:
			msg = 'Incorrect username / password !'
	return render_template('login.html', msg = msg)

@app.route('/logout')
def logout():
	session.pop('loggedin', None)
	session.pop('id', None)
	session.pop('username', None)
	return redirect(url_for('login'))

@app.route('/register', methods =['GET', 'POST'])
def register():
	msg = ''
	if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form :
		username = request.form['username']
		password = request.form['password']
		email = request.form['email']
		cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
		cursor.execute('SELECT * FROM tablelog WHERE username = % s', (username, ))
		account = cursor.fetchone()
		if account:
			msg = 'Account already exists !'
		elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
			msg = 'Invalid email address !'
		elif not re.match(r'[A-Za-z0-9]+', username):
			msg = 'Username must contain only characters and numbers !'
		elif not username or not password or not email:
			msg = 'Please fill out the form !'
		else:
			cursor.execute('INSERT INTO tablelog VALUES (NULL, % s, % s, % s)', (username, password, email, ))
			mysql.connection.commit()
			msg = 'You have successfully registered !'
	elif request.method == 'POST':
		msg = 'Please fill out the form !'
	return render_template('register.html', msg = msg)
def hello():
    return render_template('form.html')

@app.route("/predict", methods=['POST'])
def predict():
    sex = int(request.form['sex'])
    age = int(request.form['age'])
    height = int(request.form['height'])
    weight = int(request.form['weight'])
    systolic= int(request.form['systolic'])
    diastolic= int(request.form['diastolic'])
    hr = int(request.form['hr'])
    bmi = float(request.form['bmi'])
    prediction = model.predict([[sex, age, height, weight, systolic, diastolic, hr,bmi]])
    output = round(prediction[0], 2)
    if (prediction[0] == 0):
         prediction = "Normal"
    elif(prediction[0] == 1):
         prediction = "Prehypertension"
    elif(prediction[0] == 2):
         prediction = "Hypertension stage 1"
    else:
         prediction = "Hypertension stage 2"

    return render_template('form.html', prediction_text=f'This is your report: You are a {sex}, you are {age} year-old, you are {height} cm tall, you weight{weight} kg, your blood presure is {systolic}/{diastolic} mmHg, Your  heart rate is {hr} b/m, your body mass is {bmi} kg/m², you are {prediction}')
	

 
if __name__ == '__main__':
    app.run()
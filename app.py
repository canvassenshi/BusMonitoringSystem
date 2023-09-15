import json
from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re
import requests
from twilio.rest import Client

app = Flask(__name__)
app.config["SECRET_KEY"] = "xyzabcd"
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'ussers'

mysql = MySQL(app) 

@app.route("/", methods=["GET", "POST"])
def index():
	msg=requests.get("https://api.thingspeak.com/channels/2008032/feeds.json?results=2")
	msg=msg.json()['feeds'][-1]['field1']
	print(msg)
	# return redirect(url_for("index"))
	return render_template("index.html", message = int(msg))


@app.route('/login', methods =['GET', 'POST'])
def login():
    mesage = ''
    if request.method == 'POST' and 'email' in request.form and 'password' in request.form:
        email = request.form['email']
        password = request.form['password']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM user WHERE email = % s AND password = % s', (email, password, ))
        user = cursor.fetchone()
        if user:
            session['loggedin'] = True
            session['userid'] = user['userid']
            session['name'] = user['name']
            session['email'] = user['email']
            mesage = 'Logged in successfully !'
            return redirect(url_for("index"))
        else:
            mesage = 'Please enter correct email / password !'
    return render_template('login.html', mesage = mesage)

@app.route('/register', methods =['GET', 'POST'])
def register():
    mesage = ''
    if request.method == 'POST' and 'name' in request.form and 'password' in request.form and 'email' in request.form :
        userName = request.form['name']
        password = request.form['password']
        email = request.form['email']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM user WHERE email = % s', (email, ))
        account = cursor.fetchone()
        if account:
            mesage = 'Account already exists !'
        elif not userName or not password or not email:
            mesage = 'Please fill out the form !'
        else:
            cursor.execute('INSERT INTO user VALUES (NULL, % s, % s, % s)', (userName, email, password, ))
            mysql.connection.commit()
            mesage = 'You have successfully registered !'
    elif request.method == 'POST':
        mesage = 'Please fill out the form !'
    return render_template('registration.html', mesage = mesage)


@app.route('/sent', methods = ['GET', 'POST'])
def sent():
     account_sid = 'AC9e65e022f10cc8fbbd92eeca5d4abf33'
     auth_token = '3de939067967a7544f72736ba1b7cd3b'
     client = Client(account_sid, auth_token)
     message = client.messages.create(from_='+15715729852', body ='Bus On Route #1 is on the way.', to ='+918016786060')
     return render_template('sent.html')


@app.route('/server', methods = ['GET', 'POST'])
def server():
     return render_template('server.html')


if __name__ == "__main__":
	    app.run(debug=True)
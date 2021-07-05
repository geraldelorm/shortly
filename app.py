from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

import random
import string
import os

app = Flask(__name__)

#CONFIGURATIONS 
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'

#to stop modification tracking errors
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False 

#CREATE DATABASE MODULE
db = SQLAlchemy(app)

#THE MODULE
class Links(db.Model):
    id_ = db.Column("id_", db.Integer, primary_key=True)
    long = db.Column("long", db.String())
    short = db.Column("short", db.String(5))

    #CONSTRUCTOR FOR CREATING OBJECTS - which are instances of the class
    def __init__(self, long, short):
        self.long = long
        self.short = short

#CREATES DATABASE BEFORE ANY REQUEST
@app.before_first_request
def create_tables():
    db.create_all()


#FUNCTION TO GENERATE SHORT URL
def shorten_url():
    letters = string.ascii_lowercase + string.ascii_uppercase
    #LOOP THROUGH LETTERS AND PICK LETTERS
    while True:
        random_letters = random.choices(letters, k=5)
        #CONVERT RANDOM LIST INTO STRING 
        random_letters = "".join(random_letters)
        #CHECK IS RANDOM LETTERS ARE NOT ALREADY IN DB
        short_url = Links.query.filter_by(short=random_letters).first()
        #IF RANDOM SORT DON'T EXIST WE LEAVE THE LOOP
        if not short_url:
            return random_letters


#HOME END-POINT OR ROUTE
@app.route("/", methods=['POST', 'GET'])
def home():
    if request.method == "POST":
        url_inputted = request.form["user-input"]

        #CHECK IF URL ALREADY EXIST IN THE DATABASE
        found_url = Links.query.filter_by(long=url_inputted).first()
        
        if found_url:
            #IF LINK IS FOUND IN DB- Return short value and redirect to that route
            return redirect(url_for("display_short_url", url=found_url.short))
        else:
            #IF LINK IS NOT FOUND - we create an entry and a short url
            short_url = shorten_url()
            # print(short_url)
            #CREATING AN instance of the DB class - here we are using the constructor we created 
            new_url = Links(url_inputted, short_url)
            #ADD entry to DB
            db.session.add(new_url)
            #COMMIT OR SAVE CHANGES
            db.session.commit()

            return redirect(url_for("display_short_url", url=short_url))
    else:
        return render_template("home.html")

#DISPLAY  FOR THE SHORT LINK - just to keep it simple
@app.route('/display/<url>')
def display_short_url(url):
    return render_template('shorturl.html', short_url_display=url)

#PATH FOR REDIRECTION TO ORIGINAL LONG URL WHEN SHORT URL IS THE CURRENT ROUTE
@app.route('/<short_url>')
def redirection(short_url):
    #CHECK FOR THE 5 UNIQUE LETTERS IN THE DB
    long_url = Links.query.filter_by(short=short_url).first()
    if long_url:
        #REDIRECT TO THE CPORESPONDING LONG URL
        return redirect(long_url.long)
    else:
        return f'<h1>Url does not exist</h1>'

@app.route('/data')
def display_all():
    return render_template('data.html', Data=Links.query.all())

if __name__ == "__main__":
    app.run(port=5000, debug=True)
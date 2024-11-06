from flask import Flask, render_template, request, redirect, url_for, flash
from pymongo import MongoClient
import database 

app = Flask(__name__)
app.secret_key = 'Javy!321' 

def create_mongo_connection():
    client = MongoClient("mongodb://localhost:27017/")  
    db = client["travel_booking"]
    return db

db = create_mongo_connection()

@app.route('/')
def home():
    app.logger.debug('Home page accessed')
    return render_template('index.html')

@app.route('/flights', methods=['GET', 'POST'])
def flights():
    if request.method == 'POST':
       
        departure_city = request.form.get('departure')
        arrival_city = request.form.get('arrival')
        departure_date = request.form.get('departure_date')
        return_date = request.form.get('return_date')

       
        formatted_departure_date = departure_date if departure_date else None
        formatted_return_date = return_date if return_date else None

       
        flights_list = database.get_flights(
            db,
            departure_city=departure_city,
            destination=arrival_city,
            departure_date=formatted_departure_date,
            return_date=formatted_return_date
        )
    else:
        flights_list = database.get_flights(db)

    return render_template('flights.html', flights=flights_list)

@app.route('/hotels')
def hotels():
    app.logger.debug('Hotels page accessed')
    return render_template('hotels.html')

@app.route('/trains')
def trains():
    app.logger.debug('Trains page accessed')
    return render_template('trains.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        
        users_collection = db.users

        existing_user = users_collection.find_one({"username": username})
        if existing_user:
            flash('Username already exists! Please choose another one.')
        else:
            result = users_collection.insert_one({
                "username": username,
                "email": email,
                "password": password
            })
            
            if result.acknowledged:
                flash('Registration successful! You can now log in.')
                return redirect(url_for('login'))
            else:
                flash('Registration failed. Please try again.')

    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        users_collection = db.users
        user = users_collection.find_one({"username": username, "password": password})
        if user:
            flash('Login successful!')
            return redirect(url_for('home'))
        else:
            flash('Invalid username or password.')

    app.logger.debug('Login page accessed')
    return render_template('login.html')

if __name__ == '__main__':
    app.run(debug=True)

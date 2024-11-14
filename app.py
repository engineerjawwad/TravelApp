from flask import Flask, render_template, request, redirect, url_for, flash
from pymongo import MongoClient
from amadeus import Client, ResponseError
import os
from datetime import datetime
from dotenv import load_dotenv
from bcrypt import hashpw, gensalt, checkpw
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")

amadeus = Client(
    client_id=os.getenv("AMADEUS_API_KEY"),
    client_secret=os.getenv("AMADEUS_API_SECRET")
)
if not amadeus.client_id or not amadeus.client_secret:
    app.logger.error("Amadeus API credentials are missing. Check your environment variables.")

def create_mongo_connection():
    client = MongoClient("mongodb://localhost:27017/")
    db = client["travel_booking"]
    return db

db = create_mongo_connection()

def validate_date_format(date_str):
    try:
        datetime.strptime(date_str, "%d/%m/%Y")
        return True
    except ValueError:
        return False

def convert_date_format(date_str):
    try:
        date_obj = datetime.strptime(date_str, "%d/%m/%Y")
        return date_obj.strftime("%Y-%m-%d")
    except ValueError:
        return None

@app.route('/')
def home():
    app.logger.debug('Home page accessed')
    return render_template('index.html')

@app.route('/flights', methods=['GET', 'POST'])
def flights():
    flights_list = []
    if request.method == 'POST':
        departure_city = request.form.get('departure')
        arrival_city = request.form.get('arrival')
        departure_date = request.form.get('departure_date')
        return_date = request.form.get('return_date')

        if not (validate_date_format(departure_date) and (not return_date or validate_date_format(return_date))):
            flash("Please enter dates in the correct format (dd/mm/yyyy).")
        else:
            departure_date = convert_date_format(departure_date)
            return_date = convert_date_format(return_date) if return_date else None

            if departure_date:
                flights_list = search_flights_amadeus(departure_city, arrival_city, departure_date, return_date)
                if flights_list is None:
                    flash("Error fetching flight data. Please try again.")
            else:
                flash("Invalid date format.")

    return render_template('flights.html', flights=flights_list)

def search_flights_amadeus(departure_city, arrival_city, departure_date, return_date=None):
    try:
        response = amadeus.shopping.flight_offers_search.get(
            originLocationCode=departure_city,
            destinationLocationCode=arrival_city,
            departureDate=departure_date,
            returnDate=return_date,
            adults=1
        )
        return response.data
    except ResponseError as error:
        app.logger.error(f"Amadeus API error: {error}")
        return None

@app.route('/book/<flight_id>', methods=['GET'])
def book(flight_id):
    flights_collection = db.flights
    flight = flights_collection.find_one({"id": flight_id})

    if flight:
        bookings_collection = db.bookings
        booking_result = bookings_collection.insert_one({
            "flight_id": flight_id,
            "user_id": "example_user_id",
            "status": "confirmed",
            "date": datetime.now()
        })

        if booking_result.acknowledged:
            flash(f"Flight {flight_id} booked successfully!")
        else:
            flash(f"Failed to book flight {flight_id}. Please try again.")
    else:
        flash(f"Flight {flight_id} not found.")

    return redirect(url_for('flights'))

@app.route('/hotels', methods=['GET', 'POST'])
def hotels():
    hotels_list = []
    if request.method == 'POST':
        city_code = request.form.get('city_code')
        check_in_date = request.form.get('check_in_date')
        check_out_date = request.form.get('check_out_date')

        if not (validate_date_format(check_in_date) and validate_date_format(check_out_date)):
            flash("Please enter dates in the correct format (dd/mm/yyyy).")
        else:
            check_in_date = convert_date_format(check_in_date)
            check_out_date = convert_date_format(check_out_date)

            hotels_list = search_hotels_amadeus(city_code, check_in_date, check_out_date)
            if hotels_list is None:
                flash("Error fetching hotel data. Please try again.")

    return render_template('hotels.html', hotels=hotels_list)

def search_hotels_amadeus(city_code, check_in_date, check_out_date):
    try:
        response = amadeus.shopping.hotel_offers.get(
            cityCode=city_code,
            checkInDate=check_in_date,
            checkOutDate=check_out_date,
            adults=1
        )
        return response.data
    except ResponseError as error:
        app.logger.error(f"Amadeus API error: {error}")
        return None

@app.route('/book_hotel/<hotel_id>', methods=['POST'])
def book_hotel(hotel_id):
    hotels_collection = db.hotels
    hotel = hotels_collection.find_one({"id": hotel_id})

    if hotel:
        bookings_collection = db.bookings
        booking_result = bookings_collection.insert_one({
            "hotel_id": hotel_id,
            "user_id": "example_user_id",
            "status": "confirmed",
            "date": datetime.now()
        })

        if booking_result.acknowledged:
            flash(f"Hotel {hotel_id} booked successfully!")
        else:
            flash(f"Failed to book hotel {hotel_id}. Please try again.")
    else:
        flash(f"Hotel {hotel_id} not found.")

    return redirect(url_for('hotels'))

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
            password_hash = hashpw(password.encode('utf-8'), gensalt())

            result = users_collection.insert_one({
                "username": username,
                "email": email,
                "password": password_hash
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
        user = users_collection.find_one({"username": username})

        if user and checkpw(password.encode('utf-8'), user['password']):
            flash('Login successful!')
            return redirect(url_for('home'))
        else:
            flash('Invalid username or password.')

    app.logger.debug('Login page accessed')
    return render_template('login.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

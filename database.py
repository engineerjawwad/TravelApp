# database.py

from pymongo import MongoClient

def create_mongo_connection():
    client = MongoClient("mongodb://localhost:27017/")
    db = client["travel_booking"]
    return db

def initialize_db(db):
    if "flights" not in db.list_collection_names():
        db.create_collection("flights")

def insert_flight(db, departure_city, destination, departure_date, return_date):
    flights_collection = db.flights
    flight = {
        "departure_city": departure_city,
        "destination": destination,
        "departure_date": departure_date,
        "return_date": return_date
    }
    flights_collection.insert_one(flight)

def get_flights(db, departure_city=None, destination=None, departure_date=None, return_date=None):
    flights_collection = db.flights
    query = {}

    if departure_city:
        query['departure_city'] = departure_city
    if destination:
        query['destination'] = destination
    if departure_date:
        query['departure_date'] = departure_date
    if return_date:
        query['return_date'] = return_date

    flights = flights_collection.find(query)
    return list(flights)

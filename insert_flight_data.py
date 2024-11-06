from pymongo import MongoClient
from datetime import datetime

def create_mongo_connection():
    client = MongoClient("mongodb://localhost:27017/")
    db = client["travel_booking"]
    return db

def initialize_db(db):
    if "flights" not in db.list_collection_names():
        db.create_collection("flights")

def insert_flight(db, departure_city, destination, departure_date, return_date):
    # Convert dates to dd-mm-yyyy format
    try:
        formatted_departure_date = datetime.strptime(departure_date, '%d-%m-%Y').strftime('%d-%m-%Y')
        formatted_return_date = datetime.strptime(return_date, '%d-%m-%Y').strftime('%d-%m-%Y')
    except ValueError:
        print("Invalid date format. Please use dd-mm-yyyy.")
        return

    flights_collection = db.flights
    flight = {
        "departure_city": departure_city,
        "destination": destination,
        "departure_date": formatted_departure_date,
        "return_date": formatted_return_date
    }
    result = flights_collection.insert_one(flight)
    if result.acknowledged:
        print("Flight successfully inserted.")
    else:
        print("Failed to insert flight.")

if __name__ == "__main__":
    db = create_mongo_connection()
    initialize_db(db)

    departure_city = input("Enter departure city: ")
    destination = input("Enter destination city: ")
    departure_date = input("Enter departure date (dd-mm-yyyy): ")
    return_date = input("Enter return date (dd-mm-yyyy): ")
    price = input("Enter price: ")

    insert_flight(db, departure_city, destination, departure_date, return_date)

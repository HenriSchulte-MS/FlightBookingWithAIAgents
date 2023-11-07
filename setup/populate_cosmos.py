from azure.identity import DefaultAzureCredential
from azure.cosmos import CosmosClient
from dotenv import load_dotenv
import uuid
import datetime as dt
import random
import pandas as pd
import os

# Determine script location irrespective of current working directory
script_dir = os.path.dirname(os.path.realpath(__file__))

# Load dotenv
env_path = os.path.join(script_dir, '../app/.env')
load_dotenv(env_path)

# Read airports file
airports_path = os.path.join(script_dir, 'airports.csv')
airports = pd.read_csv(airports_path, sep=';')

# Get airport count
airport_count = len(airports)

# Select departure random row from file
departure_idx = random.randint(0, airport_count - 1)

# Select arrival random row from file
arrival_idx = random.randint(0, airport_count - 1)
while departure_idx == arrival_idx:
  arrival_idx = (arrival_idx + 1) % airport_count

# Populate flight dict
flight = {
  'departure_city': airports.iloc[departure_idx]['City'],
  'departure_airport': airports.iloc[departure_idx]['IATA Code'],
  'arrival_city': airports.iloc[arrival_idx]['City'],
  'arrival_airport': airports.iloc[arrival_idx]['IATA Code']
}

# Get default azure credential
credential = DefaultAzureCredential()

# Create a CosmosClient
conn_str = os.getenv('COSMOS_CONNECTION_STRING')
cosmos_client = CosmosClient.from_connection_string(conn_str=conn_str)
database_client = cosmos_client.get_database_client('AirlineBooking')
container_client = database_client.get_container_client('Flights')

for i in range(3):
  # Add id to flight
  flight['id'] = str(uuid.uuid4())

  # Add a random price
  flight['price'] = random.randint(100, 500)

  # Add a random date
  future_days = random.randint(8, 15)  # choose a random number of days in the future up to a week
  future_date = dt.datetime.now() + dt.timedelta(days=future_days)
  flight['date'] = future_date.strftime("%Y-%m-%d")

  # Add a random time
  flight['departure_time'] = dt.time(random.randint(0, 23), random.randint(0, 59)).strftime("%H:%M")

  # Add a random number of free seats, 50% will be 0
  free_seats = random.randint(-50, 50)
  flight['free_seats'] = max(free_seats, 0)

  # Add a random airline
  airline_idx = random.randint(0, 3)
  airlines = ['Contoso Air', 'Wide World Airlines', 'Adventure Works', 'Adatum Air']
  flight['airline'] = airlines[airline_idx]

  # Create item
  container_client.create_item(body=flight)
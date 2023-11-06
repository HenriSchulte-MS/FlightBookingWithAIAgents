from azure.identity import DefaultAzureCredential
from azure.cosmos import CosmosClient
from semantic_kernel.skill_definition import sk_function
import json


class FlightsPlugin:

    def __init__(self, conn_str) -> None:
        
        # Get default azure credential
        credential = DefaultAzureCredential()

        # Create a CosmosClient
        cosmos_client = CosmosClient.from_connection_string(conn_str=conn_str)
        database_client = cosmos_client.get_database_client('AirlineBooking')
        self.container_client = database_client.get_container_client('Flights')

    @sk_function(
        description='Get flights from CosmosDB with a departure and arrival city.',
        name='GetFlights',
        input_description='Two comma-separated values: departure city, arrival city.'
    )
    def get_flights(self, input: str) -> str:

        # Extract the departure and arrival city from the input
        departure_city, arrival_city = input.split(',')        

        # Trim potential whitespace
        departure_city = departure_city.strip()
        arrival_city = arrival_city.strip()

        query = f"SELECT * FROM c WHERE c.departure_city = '{departure_city}' AND c.arrival_city = '{arrival_city}'"

        flights = list(self.container_client.query_items(
            query=query,
            enable_cross_partition_query=True
        ))

        # Only return the following properties: departure_city, arrival_city, departure_airport, arrival_airport, id, price, date
        return_props = ['departure_city', 'arrival_city', 'departure_airport', 'arrival_airport', 'id', 'price', 'date']
        flights = [{k: v for k, v in flight.items() if k in return_props} for flight in flights]

        return json.dumps(flights, indent=True)
    

    @sk_function(
        description='Book flight.',
        name='BookFlight',
        input_description='Flight id.'
    )
    def book_flight(self, input: str) -> str:
            
            # Extract the flight id from the input
            flight_id = input
    
            # Trim potential whitespace
            flight_id = flight_id.strip()
    
            query = f"SELECT * FROM c WHERE c.id = '{flight_id}'"
    
            flights = list(self.container_client.query_items(
                query=query,
                enable_cross_partition_query=True
            ))
    
            # Check if free seats are available
            if flights[0]['free_seats'] > 0:
                 return "Flight successfully booked."
            else:
                return "Flight could not be booked. There are no free seats available."

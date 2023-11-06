from azure.identity import DefaultAzureCredential
from azure.cosmos import CosmosClient
from semantic_kernel.skill_definition import sk_function
import json


class CosmosPlugin:

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
        input_description='Two somma-separated values: departure city, arrival city.'
    )
    def get_flights(self, input: str) -> str:

        # Extract the departure and arrival city from the input
        departure_city, arrival_city = input.split(',')        

        # Trim potential whitespace
        departure_city = departure_city.strip()
        arrival_city = arrival_city.strip()

        query = f"SELECT * FROM c WHERE c.departure_city = '{departure_city}' AND c.arrival_city = '{arrival_city}'"

        items = list(self.container_client.query_items(
            query=query,
            enable_cross_partition_query=True
        ))

        return json.dumps(items, indent=True)

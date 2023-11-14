# 🛫 Airline Booking Demo with AutoGen and Semantic Kernel

![Two pilots smiling](/app/static/img/banner.png)<br>
<small>*Image generated with DALLE-3 in [Bing Image Creator](https://bing.com/images/create)*</small>

A small demo on combining [AutoGen](https://github.com/microsoft/autogen) and [Semantic Kernel](https://github.com/microsoft/semantic-kernel) to create a simple flight booking system that's powered by AI agents.
The application allows users to provide booking instructions once, e.g., "*Book the cheapest flight from Tokyo to Toronto*", and then lets AI agents determine how to complete the task without any additional user input. 

The demo includes two agents: An LLM-powered assistant and a worker agent that is capable of executing Semantic Kernel plugins (formerly known as skills). In addition to the built-in `TimeSkill` that gives the agent access to time and date operations, the agent also has access to a custom `FlightsPlugin` that enables looking up flights between two cities and to issue a (simulated) booking request.

To make the agents' thought process transparent, the app visualizes their back-and-forth in a chat format. The interactions of the agents depend on the flights data and user instructions. An example:

| Role | Message |
| -------- | -------- |
| 👤 User   | Book the cheapest flight from Tokyo to Toronto   |
| 🤖 Assistant   | *Making a call to GetFlights function with input "Tokyo, Toronto"*   |
| 🖥️ GetFlights | *List of flights from Tokyo to Toronto, incl. details like time and price* |
| 🤖 Assistant | *Making a call to BookFlights function with the flight ID of the cheapest flight* |
| 🖥️ BookFlight | The flight could not be booked. There are no free seats available. |
| 🤖 Assistant | I regret to inform you that the cheapest flight from Tokyo to Toronto is currently fully booked. Let's try to book the next available option for you. <br>*Making a call to BookFlights function with the flight ID of the next cheapest flight* |
| 🖥️ BookFlight | Flight successfully booked. |
| 🤖 Assistant | Great news! I've successfully booked your flight from Tokyo to Toronto. This is your flight detail: [...]

## Running the app locally
This app utilizes Azure OpenAI for Large Language Models and Azure CosmosDB for data storage. You can run the application itself locally by following the steps below.

### Setting up your environment
1. Clone this repo to your machine.
1. Create a Python virtual environment and activate it.
1. Install the libraries listed in [requirements.txt](app/requirements.txt). ? `Semantic Kernel 0.3.14.dev` does not currently support `openai 1.0`, so you might see dependency conflicts. Force the installations of the exact versions mentioned.
1. Rename the [.env.example](/app/.env.example) file to `.env`. You will populate it in the next section.

### Setting up your Azure resources
1. Create an Azure OpenAI resource and deploy a `gpt-35-turbo` or `gpt-4` model.
1. Add the deployment name, resource endpoint, and key to the `.env` file.
1. Create an Azure CosmosDB resource. Within, create a database `AirlineBooking` and a container `Flights`.
1. Add the read-write connection string for your CosmosDB resource to the `.env` file.
1. To populate the database, run [populate_cosmos.py](/setup/populate_cosmos.py) a few times. You might have to install `pandas` if it's not present in your virtual environment. Every time you run it, the script adds three new flights to the database. 

## Running the application
1. In your terminal, switch to the `app` directory. 
1. Run `flask run` to start the app.
1. Click the link in your terminal or navigate to `http://127.0.0.1:5000` in your browser to view the application.
1. Enter your instructions and click **Send**. The agents will react to your instructions and the final result is displayed. To see intermediate steps, click **Show intermediate steps**. You can try a new instruction by clicking **Start over** in the bottom of the page.
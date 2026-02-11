import requests
import dotenv
import os
from pprint import pprint

dotenv.load_dotenv()


url = f"https://api.tomorrow.io/v4/weather/history/recent?location=51.47398329464333,-0.1828879798975107&timestamp=1h&apikey={os.getenv('tomorrow_apikey')}"


response = requests.request("GET", url)

pprint(response.json())

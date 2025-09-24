import os
import requests
from dotenv import load_dotenv

load_dotenv()

WEATHERAPI_KEY = os.getenv("WEATHERAPI_KEY")

def get_weather_and_location_data(location_name: str):
    """
    Fetches both location coordinates and weather forecast from WeatherAPI.com
    in a single call.
    """
    if not location_name or not WEATHERAPI_KEY:
        return None, None

    url = f"http://api.weatherapi.com/v1/forecast.json?key={WEATHERAPI_KEY}&q={location_name}&days=1&aqi=no&alerts=no"

    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        location_data = {
            "lat": data['location']['lat'],
            "lon": data['location']['lon']
        }

        weather_info = {
            "description": data['current']['condition']['text'],
            "cloud_cover_percent": data['current']['cloud'],
            "visibility_km": data['current'].get('vis_km', 'N/A'),
            "temperature_celsius": data['current']['temp_c']
        }

        return location_data, weather_info
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from WeatherAPI.com: {e}")

    return None, None
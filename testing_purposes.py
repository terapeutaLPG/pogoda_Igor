import requests
from pprint import pprint
API_key = '4254316d1ccf131f81e76d7ec009f94c'


def get_weather(api_key, city):
    base_url = "http://api.openweathermap.org/data/2.5/weather"
    params = {
        "q": city,
        "appid": api_key,
        "units": "metric"
    }

    response = requests.get(base_url, params=params)
    weather_data = response.json()

    pprint(weather_data
           )

    return weather_data


get_weather(API_key, 'Warsaw')
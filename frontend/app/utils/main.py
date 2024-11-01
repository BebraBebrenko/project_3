import requests
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv
import os

# Загрузка переменных окружения из .env файла
load_dotenv()

# Получение API_KEY
API_KEY = os.getenv("API_KEY")
print(API_KEY)


def get_weather_data(city, days):
    location_key = get_location_key(city)
    url = f"http://dataservice.accuweather.com/forecasts/v1/daily/5day/{location_key}?apikey={API_KEY}&metric=true&details=true"
    response = requests.get(url)

    if response.status_code != 200:
        print(
            f"Error: get_weather_data {response.status_code}"
        )
        return None

    forecast_data = response.json()["DailyForecasts"]

    dates = []
    temperatures = []
    wind_speeds = []
    precipitations = []

    for day in forecast_data:
        date = datetime.strptime(day["Date"][:10], "%Y-%m-%d")
        temperature = day["Temperature"]["Maximum"]["Value"]
        wind_speed = day["Day"]["Wind"]["Speed"]["Value"]
        precipitation = day["Day"].get("PrecipitationProbability", 0)
        if len(dates) < days:
            dates.append(date)
            temperatures.append(temperature)
            wind_speeds.append(wind_speed)
            precipitations.append(precipitation)

    data = {
        "date": dates[:days:],
        "temperature": temperatures[:days:],
        "wind_speed": wind_speeds[:days:],
        "precipitation": precipitations[:days:],
    }

    return pd.DataFrame(data)


import requests


def get_city_coordinates(city_name):

    url = f"http://dataservice.accuweather.com/locations/v1/cities/search?apikey={API_KEY}&q={city_name}"
    print(url)

    response = requests.get(url)

    if response.status_code != 200:
        print(
            f"Error: get_city_coordinates {response.status_code}"
        )
        return None

    location_data = response.json()

    if not location_data:
        print("Город не найден")
        return None

    latitude = location_data[0]["GeoPosition"]["Latitude"]
    longitude = location_data[0]["GeoPosition"]["Longitude"]

    return (latitude, longitude)


def get_location_key(city):
    url = f"http://dataservice.accuweather.com/locations/v1/cities/search?apikey={API_KEY}&q={city}"
    response = requests.get(url)
    if response.status_code in (401, 403, 501, 503):
        return "connection_error"
    try:
        data = response.json()
        if data:
            return data[0]["Key"]
    except:
        return None

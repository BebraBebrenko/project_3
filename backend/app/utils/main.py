import requests
import pandas as pd

import os

api_key = ""
#print(f'Ваш API ключ: {api_key}')


def IsWeatherGood(temperature, humidity, wind_speed, visibility):
    '''
    The weather is good while
    temperature in [0, 35]*C
    humidity in [30, 60]%
    wind_speed <= 50km/h
    visibility >= 10km
    '''

    return  0 <= temperature <= 35 and 30 <= humidity <= 60 \
        and wind_speed <= 50 and visibility >= 10


def GetLocationKeyByName(city : str):
    # Get location key by city name

    url = 'http://dataservice.accuweather.com/locations/v1/cities/search'
    params = {
        'apikey': api_key,
        'q': city
    }
    response = requests.get(url, params=params)

    location_key = None
    if response.status_code == 200:
        try:
            data = response.json()[0]
            #print(json.dumps(data, indent=4, ensure_ascii=False))
            location_key = data['Key']
        except:
            location_key = None
    else:
        print(f'Error: {response.status_code}')
    
    return (location_key, response.status_code)


def GetWeatherData(location_key):
    # Get weather information by location key

    url = f'http://dataservice.accuweather.com/currentconditions/v1/{location_key}'
    params = {
        'apikey': api_key,
        'details': 'true'
    }

    response = requests.get(url, params=params)
    data = None
    if response.status_code == 200:
        try:
            data = response.json()[0]
            #print(json.dumps(data, indent=4, ensure_ascii=False))
        except:
            data = None
    else:
        print(f'Error: {response.status_code}')
    
    return (data, response.status_code)


def Parse(data):
    res = None
    try:
        res = {
            'temperature': data['Temperature']['Metric']['Value'],
            'humidity': data['RelativeHumidity'],
            'wind_speed': data['Wind']['Speed']['Metric']['Value'],
            'visibility': data['Visibility']['Metric']['Value']
        }
    except:
        res = None

    return res


from enum import Enum, auto


class Response(Enum):
    GOOD = auto()
    BAD = auto()
    USER_ERROR = auto()
    SERVER_ERROR = auto()


def GetRecommendation(city1 : str, city2 : str):
    res1 = GetLocationKeyByName(city1)
    res2 = GetLocationKeyByName(city2)
    location_key1 = res1[0]
    location_key2 = res2[0]

    if not location_key1 or not location_key2:
        if res1[1] != 200 or res2[1] != 200:
            return Response.SERVER_ERROR
        else:
            return Response.USER_ERROR

    res1 = GetWeatherData(location_key1)
    res2 = GetWeatherData(location_key2)
    json1 = res1[0]
    json2 = res2[0]

    if not json1 or not json2:
        if res1[1] != 200 or res2[1] != 200:
            return Response.SERVER_ERROR
        else:
            return Response.USER_ERROR
    
    try:
        data1 = Parse(json1)
        data2 = Parse(json2)
    except:
        return Response.ERROR
    
    print(data1)
    print(data2)

    flag1 = IsWeatherGood(**data1)
    flag2 = IsWeatherGood(**data2)

    if flag1 and flag2:
        return Response.GOOD
    else:
        return Response.BAD


from datetime import datetime, timedelta
import random

def get_weather_data(start_point, end_point):
    # Имитация данных о погоде для семи дней
    dates = [datetime.now() + timedelta(days=i) for i in range(7)]
    data = {
        'date': dates,
        'temperature': [random.randint(15, 30) for _ in dates],
        'wind_speed': [random.uniform(0, 15) for _ in dates],
        'precipitation': [random.uniform(0, 100) for _ in dates]
    }
    return pd.DataFrame(data)


def get_city_coordinates(city_name):
    """
    Возвращает случайные координаты для тестирования.

    Args:
        city_name (str): Название города (для этой функции не используется).

    Returns:
        tuple: Кортеж (широта, долгота) со случайными координатами.
    """
    latitude = random.uniform(-90, 90)   # Случайная широта от -90 до 90
    longitude = random.uniform(-180, 180) # Случайная долгота от -180 до 180
    return (latitude, longitude)

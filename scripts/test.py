import os
import requests
import json

API_KEY = "kH9kvBtyOYJ9qTwVY06ZZ5a9QlzZ0L45"

def get_location_key(city):
    url = f"http://dataservice.accuweather.com/locations/v1/cities/search?apikey={API_KEY}&q={city}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        if data:
            return data[0]['Key']
        return None
    except requests.exceptions.RequestException as e:
        print(f"Error fetching location key: {e}")
        return None

def get_weather(location_key):
    url = f"http://dataservice.accuweather.com/currentconditions/v1/{location_key}?apikey={API_KEY}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        weather_data = response.json()
        script_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(script_dir, 'response.json')

        with open(file_path, 'w') as f:
            json.dump(weather_data, f, indent=4)
        return weather_data
    except requests.exceptions.RequestException as e:
        print(f"Error fetching weather data: {e}")
        return None

if __name__ == "__main__":
    city = "Moscow"
    location_key = get_location_key(city)

    if location_key:
        weather = get_weather(location_key)
        if weather:
            print("Данные сохранены в 'response.json'.")
        else:
            print("Ошибка при получении данных.")
    else:
        print("Ошибка при получении ключа локации.")

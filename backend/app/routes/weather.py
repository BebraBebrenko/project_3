from flask import Blueprint, render_template, request
import requests


API_KEY = "kH9kvBtyOYJ9qTwVY06ZZ5a9QlzZ0L45"
bp = Blueprint('weather', __name__, url_prefix='/weather')


@bp.route('/route', methods=['GET', 'POST'])
def weather_route():
    if request.method == 'POST':
        start_city = request.form.get('start')
        end_city = request.form.get('end')

        start_key = get_location_key(start_city)
        end_key = get_location_key(end_city)
        if start_key == "connection_error" or end_key == "connection_error":
            return render_template('error.html', error="Не удалось подключиться к API")
        
        if not start_key or not end_key:
            return render_template('error.html', error="Ошибка при получении данных о городах")

        start_weather = get_weather(start_key)
        end_weather = get_weather(end_key)

        if start_weather == "connection_error" or end_weather == "connection_error":
            return render_template('error.html', error="Не удалось подключиться к API")
        if not start_weather or not end_weather:
            return render_template('error.html', error="Ошибка при получении данных о погоде")

        start_temp = start_weather[0]['Temperature']['Metric']['Value']
        end_temp = end_weather[0]['Temperature']['Metric']['Value']
        
        start_wind_speed = get_wind_speed(start_weather[0])
        end_wind_speed = get_wind_speed(end_weather[0])
        
        start_precipitation_probability = get_precipitation_probability(start_weather[0])
        end_precipitation_probability = get_precipitation_probability(end_weather[0])
        start_precipitation = get_precipitation(start_weather[0])
        end_precipitation = get_precipitation(end_weather[0])

        start_assessment = check_bad_weather(start_temp, start_wind_speed, start_precipitation_probability, start_precipitation)
        end_assessment = check_bad_weather(end_temp, end_wind_speed, end_precipitation_probability, end_precipitation)

        return render_template(
            'result.html', 
            start=start_city, 
            end=end_city, 
            start_weather=start_weather[0],  
            end_weather=end_weather[0],
            start_assessment=start_assessment,
            end_assessment=end_assessment
        )
    return render_template('index.html')

def get_location_key(city):
    url = f"http://dataservice.accuweather.com/locations/v1/cities/search?apikey={API_KEY}&q={city}"
    response = requests.get(url)
    if response.status_code in (401, 403, 501, 503):
        return "connection_error"
    try:
        data = response.json()
        if data:
            return data[0]['Key']
    except:
        return None

def get_weather(location_key):
    url = f"http://dataservice.accuweather.com/currentconditions/v1/{location_key}?apikey={API_KEY}&details=true"
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except:
        if response.status_code in (401, 403, 501, 503):
            return "connection_error"
        return None

    
def check_bad_weather(temperature, wind_speed, precipitation_prob, has_precipitation):
    if temperature < 0 or temperature > 35:
        return "Неблагоприятные условия - температура"
    if wind_speed > 50:
        return "Неблагоприятные условия - ветер"
    if precipitation_prob > 70 or has_precipitation:
        return "Неблагоприятные условия - осадки"
    return "Благоприятные условия"


def get_wind_speed(weather_data):
    try:
        return weather_data['Wind']['Speed']['Metric']['Value']
    except KeyError:
        return 0
    
def get_precipitation_probability(weather_data):
    try:
        return weather_data['PrecipitationProbability']
    except KeyError:
        return 0
    
def get_precipitation(weather_data):
    try:
        return weather_data['HasPrecipitation']
    except KeyError:
        return 0
from datetime import datetime
import logging
import requests
import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters.command import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.dispatcher.router import Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from dotenv import load_dotenv
import os

load_dotenv()

API_KEY = os.getenv("API_KEY")
API_TOKEN = os.getenv("API_TOKEN")

ACCUWEATHER_LOCATION_URL = "http://dataservice.accuweather.com/locations/v1/cities/geoposition/search"
ACCUWEATHER_FORECAST_URL = "http://dataservice.accuweather.com/forecasts/v1/daily/"

bot = Bot(token=API_TOKEN)
dp = Dispatcher()
router = Router()
dp.include_router(router)
logging.basicConfig(level=logging.INFO)
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

def get_weather_data(city, days):
    location_key = get_location_key(city)
    url = f"http://dataservice.accuweather.com/forecasts/v1/daily/5day/{location_key}?apikey={API_KEY}&metric=true&details=true"
    response = requests.get(url)
    
    if response.status_code != 200:
        print(f"Ошибка: get_weather_data не удалось получить данные (код {response.status_code})")
        return None
    
    forecast_data = response.json()['DailyForecasts']
    
    dates = []
    temperatures = []
    wind_speeds = []
    precipitations = []
    

    for day in forecast_data:
        date = datetime.strptime(day['Date'][:10], '%Y-%m-%d').strftime('%d.%m.%Y')
        temperature = day['Temperature']['Maximum']['Value']
        wind_speed = day['Day']['Wind']['Speed']['Value']
        precipitation = day['Day'].get('PrecipitationProbability', 0)
        if len(dates) < days:
            dates.append(date)
            temperatures.append(temperature)
            wind_speeds.append(wind_speed)
            precipitations.append(precipitation)

    forecast_message = "Прогноз погоды:\n\n"
    for date, temp, wind, precip in zip(dates, temperatures, wind_speeds, precipitations):
        forecast_message += (
            f"Дата: {date}\n"
            f"Температура: {temp} °C\n"
            f"Скорость ветра: {wind} км/ч\n"
            f"Вероятность осадков: {precip}%\n\n"
        )
    headline = response.json()['Headline']

    forecast_message += f"Подробнее: {headline['Link']}"
    return forecast_message

@router.message(Command("start"))
async def send_welcome(message: types.Message):
    welcome_text = (
        "Привет! Я погодный бот.\n"
        "Я могу помочь вам получить прогноз погоды для маршрута.\n"
        "Чтобы узнать, как использовать команды, введите /help."
    )
    await message.reply(welcome_text)


@router.message(Command("help"))
async def send_help(message: types.Message):
    help_text = (
        "Доступные команды:\n"
        "/start - Приветственное сообщение\n"
        "/help - Показать это сообщение\n"
        "/weather - Получить прогноз погоды для маршрута\n\n"
        "Для получения прогноза погоды используйте команду /weather, "
        "введите начальную и конечную точки маршрута и выберите временной интервал."
    )
    await message.reply(help_text)

class RouteForm(StatesGroup):
    start_point = State()
    end_point = State()
    duration = State() 

@dp.message(Command('weather'))
async def cmd_weather(message: Message, state: FSMContext):
    await message.answer("Введите начальную точку маршрута:")
    await state.set_state(RouteForm.start_point)

@dp.message(RouteForm.start_point)
async def process_start_point(message: Message, state: FSMContext):
    await state.update_data(start_point=message.text)
    await message.answer("Введите конечную точку маршрута:")
    await state.set_state(RouteForm.end_point)

@dp.message(RouteForm.end_point)
async def process_end_point(message: Message, state: FSMContext):
    await state.update_data(end_point=message.text)
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="Прогноз на 3 дня", callback_data="3"),
            InlineKeyboardButton(text="Прогноз на 5 дней", callback_data="5")
        ]
    ])
    
    await message.answer(
        "Выберите временной интервал прогноза:",
        reply_markup=keyboard
    )
    await state.set_state(RouteForm.duration)

@dp.callback_query(RouteForm.duration)
async def process_duration(callback_query: CallbackQuery, state: FSMContext):
    duration = int(callback_query.data)
    await state.update_data(duration=duration)
    data = await state.get_data()
    start_point = data['start_point']
    end_point = data['end_point']
    start_weather = get_weather_data(start_point, duration)
    end_weather = get_weather_data(end_point, duration)

    if start_weather is None or end_weather is None:
        await callback_query.message.answer("Произошла ошибка при получении прогноза погоды.")
        return
    msg = start_weather + "\n\n" + end_weather
    await callback_query.message.answer(
        f"Прогноз погоды для маршрута:\n"
        f"Начальная точка: {start_point}\n"
        f"Конечная точка: {end_point}\n"
        f"\n\n{msg}"
    )
    await state.clear()

    await callback_query.answer() 



async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())

import json
import os
import requests
import time
from celery import Celery, Task, exceptions
from .util import CITIES_IDS


REDIS_URL = os.environ.get('REDIS_URL', 'redis://redis:6379')
DATA_PATH = os.environ.get('DATA_PATH', '/opt/app/data')

OPEN_WEATHER_API_URL = os.environ.get('OPEN_WEATHER_API_URL')
OPEN_WEATHER_API_KEY = os.environ.get('OPEN_WEATHER_API_KEY')

app = Celery(__name__, broker=REDIS_URL, backend=REDIS_URL)


def get_user_object(user_id):
    user_object = None

    os.makedirs(DATA_PATH, exist_ok=True)
    filename = f'{DATA_PATH}/{user_id}.json'
    if not os.path.exists(filename):
        open(filename, 'w').close()

    with open(filename, 'r') as file:
        content = file.read()
        if content:
            user_object = json.loads(content)

    return user_object


def save_user_object(user_object):

    filename = f"{DATA_PATH}/{user_object['user_id']}.json"

    with open(filename, 'w') as file:
        json.dump(user_object, file, indent=2)


def get_weather_capture_progress(user_id):

    user_object = get_user_object(user_id)

    if not user_object:
        return None

    return (len(user_object['cities']) / len(CITIES_IDS)) * 100


def request_and_fill_weather_info(city_id, user_object):

    api_url = f"{OPEN_WEATHER_API_URL}/weather?id={city_id}&appid={OPEN_WEATHER_API_KEY}&units=metric"
    response = requests.get(api_url)
    response.raise_for_status()

    data = response.json()

    user_object['cities'].append({
        'city_id': city_id,
        'temp': data['main']['temp'],
        'humidity': data['main']['humidity'],
    })


@app.task(rate_limit='60/m')
def capture_weather_info(user_id, datetime):

    user_object = get_user_object(user_id)

    if not user_object:
        user_object = {
            'user_id': user_id,
            'request_datetime': datetime,
            'cities': []
        }

    for city_id in CITIES_IDS:

        try:

            request_and_fill_weather_info(city_id, user_object)

            save_user_object(user_object)

        except Exception as e:
            print(f'Error when getting weather data for city {city_id}:{e}')

# DevGrid Open Weather Challenge

This service collects data from an Open Weather API and store it as a JSON data.

## Build and Run

Configure .env file with the following data:

```env
REDIS_URL=redis://redis:6379
DATA_PATH=/opt/app/data
OPEN_WEATHER_API_URL=https://api.openweathermap.org/data/2.5
OPEN_WEATHER_API_KEY=<your open weather api key>
```

Then, run with docker.

```bash
docker-compose up -d
```

## API

Start a new user request for scrapping the cities data.

```bash
curl -X POST -d "user_id=123" http://localhost:8000/weather
```

Get the progress of the scrapping.

```bash
curl http://localhost:8000/weather/progress?user_id=123
```

## TESTS

```bash
docker-compose up test
```

# DevGrid Open Weather Challenge

## Build and Run

Configure .env file with the following data:

```env
REDIS_URL=redis://redis:6379
DATA_PATH=/opt/app/data
OPEN_WEATHER_API_URL=https://api.openweathermap.org/data/2.5
OPEN_WEATHER_API_KEY=<your open weather api key>
```

Then, build and run with docker.

```bash
docker-compose build && docker-compose up -d && docker-compose logs -f
```

## API

Start a new user request for crawling the cities data.

```bash
curl -X POST -d "user_id=123" http://localhost:8000/weather
```

Get the progress of the crawling.

```bash
curl http://localhost:8000/weather/progress?user_id=123
```
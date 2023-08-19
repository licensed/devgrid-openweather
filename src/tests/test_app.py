import json
from unittest import main, TestCase
from unittest.mock import patch, Mock, mock_open
from src.app.app import app
from src.app.tasks import (
    get_user_object,
    save_user_object,
    request_and_fill_weather_info,
    OPEN_WEATHER_API_URL,
    OPEN_WEATHER_API_KEY,
    capture_weather_info,
)


@patch("src.app.tasks.capture_weather_info.apply_async")
def test_start_capturing_weather_info(mock_apply_async):
    client = app.test_client()

    response = client.post("/weather", data={"user_id": "123"})

    assert response.status_code == 200
    assert json.loads(response.data) == {"status": "Ok, starting weather info capture."}
    mock_apply_async.assert_called_once()


@patch("src.app.tasks.get_user_object")
def test_show_weather_capture_progress(mock_user_object):
    user_object = {
        "user_id": "123",
        "request_datetime": "2023-08-18 16:18:43.781950",
        "cities": [
            {"city_id": 3439525, "temp": 13.07, "humidity": 90},
            {"city_id": 3439781, "temp": 18.75, "humidity": 84},
        ],
    }
    mock_user_object.return_value = user_object
    client = app.test_client()

    response = client.get("/weather/progress?user_id=123")

    assert response.status_code == 200
    # Should return 2 (cities) / 167 (cities_ids) * 100
    assert json.loads(response.data) == {"progress": 1.1976047904191618}


@patch("src.app.tasks.get_user_object")
def test_show_weather_capture_progress_with_no_user_id(mock_user_object):
    mock_user_object.return_value = None
    client = app.test_client()

    response = client.get("/weather/progress")
    assert response.status_code == 400
    assert json.loads(response.data) == {"error": 'Param "user_id" is required'}


def test_start_capturing_weather_info_missing_user_id():
    client = app.test_client()

    response = client.post("/weather", data={})

    assert response.status_code == 400
    assert json.loads(response.data) == {"error": 'Param "user_id" is required'}


@patch("requests.get")
@patch("src.app.tasks.request_and_fill_weather_info")
def test_request_and_fill_weather_info(mock_weather_info, mock_get):
    response_mock = Mock()
    mock_get.return_value = response_mock
    result = mock_weather_info(3439525, "dummy_user")
    assert result.ok


def test_get_user_object_with_existing_file(monkeypatch):
    mock_file = mock_open(read_data='{"key": "value"}')
    monkeypatch.setattr("builtins.open", mock_file)

    user_id = "123"
    result = get_user_object(user_id)

    mock_file.assert_called_with(f"/tmp/{user_id}.json", "r")
    assert result == {"key": "value"}


def test_save_user_object(monkeypatch):
    mock_file = mock_open(read_data='{"key": "value"}')
    monkeypatch.setattr("builtins.open", mock_file)
    user_object = {
        "user_id": "123",
    }
    save_user_object(user_object)

    mock_file.assert_called_with(f'/tmp/{user_object["user_id"]}.json', "w")


class TestRequestAndFillWeatherInfo(TestCase):
    @patch("requests.get")
    def test_request_and_fill_weather_info(self, mock_get):
        city_id = 123
        user_object = {"user_id": "456", "cities": []}

        # Simulate the API response
        api_response = {
            "main": {"temp": 20.5, "humidity": 65}
            # Other fields...
        }

        # Create a mock response
        mock_response = Mock()
        mock_response.json.return_value = api_response
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        # Call the function
        request_and_fill_weather_info(city_id, user_object)

        expected_entry = {
            "city_id": city_id,
            "temp": api_response["main"]["temp"],
            "humidity": api_response["main"]["humidity"],
        }
        self.assertEqual(user_object["cities"], [expected_entry])
        mock_get.assert_called_once_with(
            f"{OPEN_WEATHER_API_URL}/weather?id={city_id}&appid={OPEN_WEATHER_API_KEY}&units=metric"
        )


class TestCaptureWeatherInfo(TestCase):
    @patch("src.app.tasks.get_user_object", return_value=None)
    def test_capture_weather_info_new_user(
        self, mock_get_user
    ):
        user_id = "123"
        datetime = "2023-08-18 12:00:00"

        capture_weather_info(user_id, datetime)

        mock_get_user.assert_called_once_with(user_id)


if __name__ == "__main__":
    main()

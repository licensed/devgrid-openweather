import json
from unittest import main
from unittest.mock import patch, Mock
from urllib.parse import quote_plus
from src.app.app import app


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
    result = mock_weather_info(3439525, 'dummy_user')
    assert result.ok


if __name__ == "__main__":
    main()

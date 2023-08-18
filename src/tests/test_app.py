import json
from datetime import datetime
from flask import Flask
from unittest.mock import patch


@patch('app.capture_weather_info.apply_async')
def test_start_capturing_weather_info(mock_apply_async):
    client = app.test_client()

    response = client.post('/weather', data={'user_id': '123'})

    assert response.status_code == 200
    assert json.loads(response.data) == {'status': 'Ok, starting weather info capture.'}
    mock_apply_async.assert_called_once()


@patch('app.get_weather_capture_progress')
def test_show_weather_capture_progress(mock_capture_progress):
    mock_capture_progress.return_value = 50

    client = app.test_client()

    response = client.get('/weather/123/progress')

    assert response.status_code == 200
    assert json.loads(response.data) == {'progress': 50}


def test_start_capturing_weather_info_missing_user_id():
    client = app.test_client()

    response = client.post('/weather', data={})

    assert response.status_code == 400
    assert json.loads(response.data) == {'error': 'Param "user_id" is required'}


if __name__ == '__main__':
    unittest.main()

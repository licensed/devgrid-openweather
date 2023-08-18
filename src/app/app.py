from datetime import datetime
from flask import Flask, jsonify, request
from .tasks import capture_weather_info, get_weather_capture_progress
from celery.exceptions import Retry

app = Flask(__name__)


@app.route('/weather', methods=['POST'])
def start_capturing_weather_info():
    user_id = request.form.get('user_id', None)
    if not user_id:
        return jsonify({
            'error': 'Param "user_id" is required'
        }), 400
    now = str(datetime.now())
    try:
        capture_weather_info.delay(user_id, now)
        return jsonify({
            'status': 'Ok, starting weather info capture.'
        }), 200
    except Retry:
        return jsonify({
            'error': 'Weather capture task failed. Retrying...'
        }), 500


@app.route('/weather/progress', methods=['GET'])
def show_weather_capture_progress():
    user_id = request.args.get('user_id')
    if not user_id:
        return jsonify({
            'error': 'Param "user_id" is required'
        }), 400    
    percent = get_weather_capture_progress(user_id)
    return jsonify({
        'progress': percent
    }), 200

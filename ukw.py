from uptime_kuma_api import UptimeKumaApi
from flask import Flask, jsonify
import os
from dotenv import load_dotenv
from flask import url_for

load_dotenv()  # read environment variables from .env

def are_all_up():
    uk_url = os.getenv('UPTIME_KUMA_URL', 'http://127.0.0.1:3001')
    uk_api = UptimeKumaApi(uk_url)

    # no login supported/required, run behind tailscale ;-)

    # https://uptime-kuma-api.readthedocs.io/en/latest/api.html#uptime_kuma_api.UptimeKumaApi.get_monitors
    monitors = uk_api.get_monitors()
    result = True
    for monitor in monitors:
        if monitor['active']:
            # https://uptime-kuma-api.readthedocs.io/en/latest/api.html#uptime_kuma_api.UptimeKumaApi.get_monitor_status
            status = uk_api.get_monitor_status(monitor['id'])
            # https://uptime-kuma-api.readthedocs.io/en/latest/api.html#uptime_kuma_api.MonitorStatus
            if status != 1:  # 1 means "up"
                result = False
                break

    uk_api.disconnect()
    return result


def get_active_monitors():
    uk_url = os.getenv('UPTIME_KUMA_URL', 'http://127.0.0.1:3001')
    uk_api = UptimeKumaApi(uk_url)

    monitors = uk_api.get_monitors()
    result = {}
    for monitor in monitors:
        if monitor['active']:
            status = uk_api.get_monitor_status(monitor['id'])
            result[monitor['name']] = "up" if status == 1 else "down"

    uk_api.disconnect()
    return result


app = Flask(__name__)

@app.route('/favicon.ico')
def favicon():
    return url_for('static', filename='image/favicon.ico')

@app.route("/version", methods=["GET"])
def version():
    version = os.getenv('UKW_VERSION', '0.1.0')
    return jsonify({"version": version}), 200

@app.route("/status/monitors", methods=["GET"])
def monitors():
    try:
        monitors = get_active_monitors()
        return jsonify(monitors), 200
    except Exception as e:
        print(f"Error fetching active monitors: {e}")
        return jsonify({"error message": str(e)},{"return code": 500}), 500

@app.route("/status/all", methods=["GET"])
def status_all():
    try:
        if are_all_up():
            return jsonify({"message": "all up"}), 200
        else:
            return jsonify({"message": "not all up"}), 503
    except Exception as e:
        print(f"Error checking status all: {e}")
        return jsonify({"error message": str(e)},{"return code": 500}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000) # TODO: use 127.0.0.1
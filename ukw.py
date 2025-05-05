from uptime_kuma_api import UptimeKumaApi
from flask import Flask, jsonify
import os
from dotenv import load_dotenv

load_dotenv()  # read environment variables from .env

def check_monitor_status():
    try:
        uk_url = os.getenv('UPTIME_KUMA_URL', 'http://127.0.0.1:3001')
        api = UptimeKumaApi(uk_url)

        # no login supported/required, run behind tailscale ;-)

        # https://uptime-kuma-api.readthedocs.io/en/latest/api.html#uptime_kuma_api.UptimeKumaApi.get_monitors
        monitors = api.get_monitors()
        all_up = True
        for monitor in monitors:
            if monitor['active']:
                # https://uptime-kuma-api.readthedocs.io/en/latest/api.html#uptime_kuma_api.UptimeKumaApi.get_monitor_status
                status = api.get_monitor_status(monitor['id'])
                # https://uptime-kuma-api.readthedocs.io/en/latest/api.html#uptime_kuma_api.MonitorStatus
                if status != 1:  # 1 means "up"
                    all_up = False
                    break

        api.disconnect()
        return all_up
    
    except Exception as e:
        print(f"Error checking monitor status: {e}")
        return False


app = Flask(__name__)

@app.route("/status/all", methods=["GET"])
def status():
    if check_monitor_status():
        return jsonify({"message": "all up"}), 200
    else:
        return jsonify({"message": "not all up"}), 503


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000) # TODO: use 127.0.0.1
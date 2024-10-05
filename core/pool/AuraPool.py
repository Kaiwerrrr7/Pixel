import requests
import json

def update_pool(server_hash, worker_name, app_name, data):
    try:
        url = "https://dash.aurateam.org/v1/api/dashboard"

        payload = {
            "event": "update",
            "server_hash": server_hash,
            "worker_name": worker_name,
            "app_name": app_name,
            "data": data
        }
        headers = {"Content-Type": "application/json"}

        response = requests.request("POST", url, json=payload, headers=headers, timeout=5)

        return response
    except:
        return None
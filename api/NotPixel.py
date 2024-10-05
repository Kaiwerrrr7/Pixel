import base64
import math
import random
import urllib.parse
import json
import requests
from utils.Utils import get_formatted_datetime
from rich.console import Console
import json
import threading
from core import InvalidAccountExcept

console = Console()

class NotPixel:

    def __init__(self, query_id, user_agent, proxies=None):
        self.query_id = query_id
        self.access_token = ""
        self.session = requests.Session()
        self.session.headers.update({
            "accept": "application/json, text/plain, */*",
            "accept-language": "en-US,en;q=0.9,vi;q=0.8",
            "authorization": f"initData {query_id}",
            "cache-control": "no-cache",
            "origin": "https://app.notpx.app",
            "referer": "https://app.notpx.app/",
            "User-Agent": user_agent
        })
        if proxies is not None:
            self.session.proxies.update(proxies)

        console.print(f"{get_formatted_datetime()} [green]{threading.current_thread().name} use ip address[/green]: [yellow]{self.get_ip()}[/yellow]  | {user_agent}")
        
        if not self.get_user_info():
            raise Exception("Invalid account!")

    def get_ip(self):
        url = "http://api.ipify.org?format=json"
        res = self.session.get(url)
        if res.status_code == 200:
            return res.json().get("ip")
        else:
            return None
        
    def get_user_info(self):
        for _ in range(3):
            try:
                req = self.session.get("https://notpx.app/api/v1/users/me", timeout=15)
                if req.status_code == 200:
                    return req.json()
            except Exception:
                return False

        return False
        
    def get_status(self):
        try:
            req = self.session.get("https://notpx.app/api/v1/mining/status", timeout=15)
            if req.status_code == 200:
                return req.json()
            return False
        except Exception:
            return False
        
    def random_paint(self, random_point, hex_color):
        try:
            req = self.session.post("https://notpx.app/api/v1/repaint/start", json={
                "newColor": hex_color,
                "pixelId": random_point
            }, timeout=15)
            if req.status_code == 200:
                return req.json()
            return False
        except Exception:
            return False
        
    def mining_claim(self):
        try:
            req = self.session.get("https://notpx.app/api/v1/mining/claim", timeout=15)
            if req.status_code == 200:
                return req.json()
            return False
        except Exception:
            return False
        
    def upgrade(self, type):
        try:
            req = self.session.get(f"https://notpx.app/api/v1/mining/boost/check/{type}", timeout=15)
            if req.status_code == 200:
                return req.json()
            return False
        except Exception:
            return False
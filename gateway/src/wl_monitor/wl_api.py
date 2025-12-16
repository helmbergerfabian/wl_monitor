# gateway/src/wl_monitor/wl_api.py

import requests
from typing import List, Dict, Optional
from cachetools import TTLCache
from typing import List, Dict
import requests
from datetime import datetime

import os
CACHE_SIZE = int(os.environ.get("cache_size"))
FETCH_INTERVAL_SEC = os.environ.get("fetch_interval_sec")


class WienerLinienAPI:
    BASE_URL = "https://www.wienerlinien.at/ogd_realtime/monitor"

    def __init__(self, sender: str = "", cache_ttl: int = CACHE_SIZE, max_cache_size: int = 5):
        self.sender = sender
        self.cache = TTLCache(maxsize=max_cache_size, ttl=cache_ttl)


    def fetch_departures(self, stop_id: int) -> List[Dict]:
        if stop_id in self.cache:
            print(f"[{datetime.now()}]: using cached data")
            return self.cache[stop_id]

        params = {
            "stopId": stop_id,
            "activateTrafficInfo": ["stoerungkurz", "stoerunglang", "aufzugsinfo"]
        }
        if self.sender:
            params["sender"] = self.sender

        try:
            response = requests.get(self.BASE_URL, params=params, headers={"Accept": "application/json"})
            response.raise_for_status()
            parsed = self._parse_response(response.json())
            self.cache[stop_id] = parsed
            print(f"[{datetime.now()}]: fetched new data")
            return parsed

        except Exception as e:
            print(f"[{datetime.now()}]: [ERROR] Failed to fetch departures for stopId={stop_id}: {e}")
            return []
        
    def _parse_response(self, json_data: Dict) -> List[Dict]:
        """
        Parse API JSON response and extract simplified departure info.

        Returns:
            List[Dict]: Simplified list of departures
        """
        results = []
        monitors = json_data.get("data", {}).get("monitors", [])

        for monitor in monitors:
            stop_title = monitor.get("locationStop", {}).get("properties", {}).get("title", "unknown")
            for line in monitor.get("lines", []):
                line_name = line.get("name")
                direction = line.get("towards")
                departures = line.get("departures", {}).get("departure", [])

                for dep in departures:
                    countdown = dep.get("departureTime", {}).get("countdown")
                    if countdown is not None:
                        results.append({
                            "stop": stop_title,
                            "line": line_name,
                            "towards": direction,
                            "minutes": countdown
                        })
        return results

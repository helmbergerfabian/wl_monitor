
import yaml
with open("../../config/config.yaml") as f:
    config = yaml.safe_load(f)

import os
os.environ["fetch_interval_sec"] = str(config.get("fetch_interval_sec", 5))
os.environ["cache_size"] = str(config.get("cache_size", 2))

stations = config["stations"]
mqtt_cfg = config["mqtt"]
sender = config.get("wienerlinien", {}).get("sender", "")

from wl_monitor.wl_api import WienerLinienAPI
from wl_monitor.mqtt_client import get_mqtt_client
from wl_monitor.publisher import publish_departures



api = WienerLinienAPI(sender=sender)
client = get_mqtt_client(mqtt_cfg["address"], mqtt_cfg["port"], "publ")
client.loop_start()

import time
deps_old = [None, None]
deps = [None, None]

while True: 
    changed = False
    
    for idx, station in enumerate(stations):
        deps[idx] = api.fetch_departures(station["rbl"])
        if deps[idx] != deps_old[idx]:
            changed = True
    
    if changed:
        for idx, station in enumerate(stations):
            publish_departures(
                client,
                station["name"],
                deps[idx],
                mqtt_cfg["topic_prefix"],
                idx=idx
            )

    deps_old = deps.copy()
    time.sleep(int(os.environ["fetch_interval_sec"]))
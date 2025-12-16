import time
import json
import paho.mqtt.client as mqtt
from datetime import datetime


def extract_departures(api_response):
    """
    Normalize Wiener Linien API data into a flat list of
    { "towards": str, "minutes": int }
    """
    result = []

    try:
        monitors = api_response["data"]["monitors"]
        if not monitors:
            return result

        monitor = monitors[0]
        lines = monitor.get("lines", [])
        if not lines:
            return result

        line = lines[0]
        line_towards = line.get("towards", "")
        departures = line.get("departures", {}).get("departure", [])

        for dep in departures:
            dtime = dep.get("departureTime", {})
            minutes = dtime.get("countdown")

            vehicle = dep.get("vehicle", {})
            print(vehicle.get("towards"))
            towards = vehicle.get("towards") or line_towards

            # We assume data correctness from here on
            result.append({
                "towards": towards,
                "minutes": minutes,
            })

    except Exception as e:
        print(f"[{datetime.now()}]: ⚠️ Failed to parse API response:", e)

    return result


def publish_departures(
    mqtt_client: mqtt.Client,
    station_name: str,
    departures,
    topic_prefix="ubahn",
    idx=0
):
    payload = {
        "stop": station_name,
        "departures": departures[:3],
        "idx": idx,
    }

    topic = f"{topic_prefix}/{station_name}"
    mqtt_client.publish(topic, json.dumps(payload), retain=True)
    print(f"[{datetime.now()}]: 📡 Published to {topic} (idx={idx})")


def run_publisher(api, stations, mqtt_cfg, client):
    client.connect(mqtt_cfg["address"], mqtt_cfg["port"], 60)
    client.loop_start()

    deps_old = [None, None]
    deps = [None, None]

    while True:
        changed = False

        for idx, station in enumerate(stations):
            raw = api.fetch_departures(station["rbl"])
            deps[idx] = extract_departures(raw)

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
            deps_old = [list(d) for d in deps]
        else:
            print(f"[{datetime.now()}]: no changes!")

        time.sleep(10)
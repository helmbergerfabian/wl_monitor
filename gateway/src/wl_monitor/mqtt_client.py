import paho.mqtt.client as mqtt
from typing import Literal, Optional

MQTTType = Literal["subs", "publ"]

def get_mqtt_client(
    address: str,
    port: int,
    mode: MQTTType,
    on_message_callback: Optional[callable] = None
) -> mqtt.Client:
    def on_message(client, userdata, msg):  
        print(f"{msg.topic}: {msg.payload.decode()}")

    def on_connect(client, userdata, flags, rc):
        print(f"Connected to MQTT broker with result code {rc}")

    def on_disconnect(client, userdata, rc):
        print(f"Disconnected from MQTT broker with result code {rc}")

    def on_publish(client, userdata, mid):
        print(f"Published message with mid {mid}")

    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect

    if mode == "subs":
        client.on_message = on_message_callback or on_message
    elif mode == "publ":
        client.on_publish = on_publish
    else:
        raise ValueError(f"Invalid MQTT type: {mode}")

    client.connect(address, port, 60)
    return client

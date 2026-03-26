import ssl
import paho.mqtt.client as mqtt
import time
import json
import requests
import random
import string
import threading

# ==========================================
# FILL IN THESE VARIABLES
# ==========================================
MQTT_ENDPOINT = f"mqtt-{int(time.time())}.ioref.io"  # e.g., "mqtt.pushy.me" (Do not include "ssl://" or "tcp://")
MQTT_PORT = 443                # 
KEEP_ALIVE_INTERVAL = 60      # e.g., 60 (Seconds)
APP_KEEPALIVE_INTERVAL = 300        # Seconds between sending the custom "keepalive" publish (e.g., 300 = 5 minutes)
MY_CITY_ID = "CHANGE_ME"                      # e.g. "5000899". Your city ID, can look it up at:
# https://dist-android.meser-hadash.org.il/smart-dist/services/anonymous/segments/android?instance=1544803905&locale=en_US
# ==========================================

# --- Callbacks (Equivalent to mqttClient.setCallback(this)) ---

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Successfully connected to the broker.")
        # Equivalent to: subscribeToTopic(this.mClient.getClientId());
        client.subscribe(DEVICE_TOKEN)
        print(f"Subscribed to topic: {DEVICE_TOKEN}")
    else:
        print(f"Failed to connect, return code: {rc}")

def on_message(client, userdata, msg):

    if(MY_CITY_ID not in msg.payload.decode('utf-8')):
        return
    
    print(f"Message received on {msg.topic}: {msg.payload.decode('utf-8')}")

    """ Change this to do some actions when you get an alert or the evenet has ended.
    if("האירוע הסתיים" in msg.payload.decode('utf-8')):
        # Do something

    elif(("ירי רקטות וטילים" in msg.payload.decode('utf-8') or "חדירת כלי טיס עוין" in msg.payload.decode('utf-8'))):
        # Do something
    
    elif("בדקות הקרובות צפויות להתקבל" in msg.payload.decode('utf-8'))":
        #Do something
    """

def on_disconnect(client, userdata, rc):
    print("Disconnected from the broker.")

# --- Main Connection Logic ---

def on_log(client, userdata, level, buf):
    print(f"MQTT LOG: {buf}")

def connect_and_listen():
    client = mqtt.Client(client_id=DEVICE_TOKEN, clean_session=False)

    client.on_connect = on_connect
    client.on_message = on_message
    client.on_disconnect = on_disconnect
    #client.on_log = on_log UNCOMMENT IF YOU WANT TO VIEW MQTT LOGS

    client.username_pw_set(username=DEVICE_TOKEN, password=DEVICE_AUTH_KEY)

    context = ssl.create_default_context()
    context.check_hostname = True
    context.verify_mode = ssl.CERT_REQUIRED
    client.tls_set_context(context)

    try:
        client.connect(host=MQTT_ENDPOINT, port=MQTT_PORT, keepalive=KEEP_ALIVE_INTERVAL)
        
        # Start the network loop in a background thread
        client.loop_start() 
        
        # --- Our Custom Application Keepalive Loop ---
        while True:
            # Wait for the specified interval
            time.sleep(APP_KEEPALIVE_INTERVAL)
            
            # Publish our device token to the "keepalive" topic
            #print(f"Sending application keepalive for token: {DEVICE_TOKEN[:10]}...")
            
            # QoS=1 (Quality of Service level 1) ensures the message is delivered at least once. 
            # The Java code references PushyMQTT.MQTT_QUALITY_OF_SERVICE, which is usually 1 for this.
            client.publish("keepalive", DEVICE_TOKEN, qos=1)

    except KeyboardInterrupt:
        print("Script stopped by user.")
        client.loop_stop()
        client.disconnect()
    except Exception as e:
        print(f"An error occurred: {e}")

def register_and_subscribe(city_id):
    base_url = "https://pushy.ioref.app"
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    # 1. Generate a random 16-character hex string for the Android ID
    hex_chars = ''.join(random.choices(string.hexdigits.lower(), k=16))
    dummy_android_id = f"{hex_chars}-Dummy-Python-Script"

    # 2. Register the Dummy Device
    print("[API] Registering new dummy device...")
    register_payload = {
        "androidId": dummy_android_id,
        "app": None,
        "appId": "66c20ac875260a035a3af7b2",
        "platform": "android",
        "sdk": 10117
    }
    
    reg_response = requests.post(f"{base_url}/register", json=register_payload, headers=headers)
    
    if reg_response.status_code != 200:
        raise Exception(f"Registration HTTP Error: {reg_response.status_code}")
        
    reg_data = reg_response.json()
    token = reg_data.get("token")
    auth = reg_data.get("auth")
    
    if not token or not auth:
        raise Exception(f"Registration failed. Server returned: {reg_data}")
        
    print(f"[API] Success! Generated Token: {token[:10]}...")

    # 3. Subscribe to the City ID
    print(f"[API] Subscribing token to City ID: {city_id}...")
    subscribe_payload = {
        "auth": auth,
        "token": token,
        "topics": [str(city_id), "1"] 
    }
    
    sub_response = requests.post(f"{base_url}/devices/subscribe", json=subscribe_payload, headers=headers)
    
    if sub_response.json().get("success"):
        print("[API] Successfully subscribed to areas of interest!")
    else:
        print(f"[API] Subscription failed: {sub_response.text}")
        
    return token, auth

# Fetch fresh credentials from the API!
DEVICE_TOKEN, DEVICE_AUTH_KEY = register_and_subscribe(MY_CITY_ID)

if __name__ == "__main__":
    connect_and_listen()

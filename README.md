# Home Front Command MQTT Alert Listener

A Python script that securely connects to the Israeli Home Front Command (Pikud HaOref) backend to listen for real-time rocket and emergency alerts in specific geographical zones.

This project reverse-engineers the official mobile app's Pushy MQTT implementation. It automatically registers a dummy device, grabs the necessary authentication tokens, bypasses dynamic DNS load-balancing, and subscribes to your specific area of interest to receive raw alert JSON payloads the exact second they are published.

> **⚠️ CRITICAL DISCLAIMER ⚠️** > **This project is for educational and research purposes only.** It is not affiliated with, endorsed by, or connected to the Israeli Home Front Command (Pikud HaOref) or Pushy. 
> 
> **DO NOT** rely on this script as your primary source for life-saving alerts. Network connections drop, APIs change, and community-built scripts fail. Always rely on the official physical sirens and the official Pikud HaOref mobile applications for your safety.

## 🚀 Features
* **Zero-Setup Registration:** Automatically generates a fake Android device ID and registers it with the Pushy backend to get fresh tokens.
* **Keepalive Spoofing:** Sends application-level heartbeats (`/keepalive`) to prevent the backend from dropping the connection.
* **Raw Payload Access:** Intercepts the raw JSON alert data, giving you a blank canvas to build your own automations.

## 📋 Prerequisites

* Python 3.7 or higher
* Internet connection capable of connecting to MQTT over SSL (Port 443)

## 🛠️ Installation

1. Clone this repository:
   ```bash
   git clone [https://github.com/etamar211/oref_alerts.git](https://github.com/etamar211/oref_alerts.git)
   cd oref_alerts
   ```
2. Install the required dependencies:
  ```Bash
  pip install -r requirements.txt 
  ```

## 🔍 Finding Your City ID (Segment ID)

Before running the script, you need to tell it which geographical zone you want to listen to. The Pikud HaOref API uses numeric Segment IDs for different cities and neighborhoods.

To find your exact City ID:
1. Open this official API endpoint in your browser:  
   [https://dist-android.meser-hadash.org.il/smart-dist/services/anonymous/segments/android?instance=1544803905&locale=en_US](https://dist-android.meser-hadash.org.il/smart-dist/services/anonymous/segments/android?instance=1544803905&locale=en_US)
2. This will output a large JSON file. Search for the English name of your city or neighborhood.
3. Look for the `"id"` field right next to your city's name.
4. Copy this ID.

## ⚙️ Configuration

Open the main Python script and update the `MY_CITY_ID` variable with the ID you just found:

```python
# ==========================================
# USER CONFIGURATION
# ==========================================
MY_CITY_ID = "REPLACE_ME"  # Replace with your specific City/Segment ID
# ==========================================
```

## ▶️ Usage

Run the script from your terminal:

```bash
python get_alerts.py
```

### What happens next?
1. The script will ping the API to register a new dummy device.
2. It will establish a secure TLS connection to the dynamic MQTT broker.
3. It will subscribe to your `MY_CITY_ID`.
4. It will sit quietly in the background.

When a real alert is triggered for your zone, the `on_message` function will fire, and you will receive the raw JSON payload in your console. 

### Bring Your Own Logic (BYOL)
The `on_message` function in this repository is intentionally left barebones. It simply parses and prints the incoming JSON. You can modify this function to trigger your own smart home automations, send a Telegram message, hit a Webhook, or turn your house lights red.

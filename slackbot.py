import os
import subprocess
import psutil
import re
import json
import threading
import time
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Path to configuration.json
config_path = os.path.join(BASE_DIR, "configuration.json")

# Load JSON file into a Python object (usually a dict)
with open(config_path, "r") as config_file:
    config = json.load(config_file)

SLACK_BOT_TOKEN = config["slack_bot_token"]
SLACK_APP_TOKEN = config["slack_app_token"]
SYSTEM_NAME = config["system_name"]
STATUS_KEYWORD = config["status_keyword"]

alerts_enabled = False
try:
    ALERT_CHANNEL_ID = config["alerts"]["channel_id"]
    ALERT_TIMEOUT = config["alerts"]["timeout"]
    ALERT_DISKS_THRESHOLDS = config["alerts"]["disk_thresholds"]
    MONITORED_DISKS = list(ALERT_DISKS_THRESHOLDS.keys())
    RETURN_STATUS_ON_ALERT=config["alerts"]["return_status_on_alert"]
    alerts_enabled = True
except Exception:
    print("Alerts are not enabled.")

disk_filter = False
try:
    DISKS = config["disks"]
    disk_filter = True
except Exception:
    print("Disk filter is not enabled.")


seen_events = set()

# === Initialize Slack App ===
app = App(token=SLACK_BOT_TOKEN)

def disk_alert_monitor():
    while True:
        alert_message = ""
        for part in psutil.disk_partitions():
            if not alerts_enabled or part.mountpoint not in MONITORED_DISKS:
                continue
            if 'rw' in part.opts and part.fstype != "":
                usage = psutil.disk_usage(part.mountpoint)
                if usage.percent > ALERT_DISKS_THRESHOLDS[part.mountpoint]:
                    disk_info = (
                        f"*Disk usage alert ({part.mountpoint}):*\n"
                        f"> {usage.used / (1024**3):.2f}GB / {usage.total / (1024**3):.2f}GB ({usage.percent}%)\n\n"
                    )
                    print(disk_info)
                    alert_message += disk_info

        if alert_message:
            app.client.chat_postMessage(channel=ALERT_CHANNEL_ID, text=alert_message)

        if RETURN_STATUS_ON_ALERT:
            app.client.chat_postMessage(channel=ALERT_CHANNEL_ID, text=get_system_status())

        time.sleep(ALERT_TIMEOUT * 60) 

def get_system_status():
    # CPU
    cpu_percent = psutil.cpu_percent(interval=1)

    # RAM
    ram = psutil.virtual_memory()
    ram_used = ram.used / (1024 ** 3)
    ram_total = ram.total / (1024 ** 3)
    ram_percent = ram.percent

    # Speedtest
    try:
        result = subprocess.run(
                [
                    "speedtest",
                    "--accept-license",
                    "--accept-gdpr",
                    "-f",
                    "json"
                ],
                capture_output=True,
                text=True,
                check=True,
            )

        data = json.loads(result.stdout)

        ping = data["ping"]["latency"]  # ms
        download = data["download"]["bandwidth"] * 8 / 1_000_000  # Mbps
        upload = data["upload"]["bandwidth"] * 8 / 1_000_000      # Mbps

        speedtest_info = (
            f"> Ping: {ping:.0f} ms\n"
            f"> Download: {download:.2f} Mbps\n"
            f"> Upload: {upload:.2f} Mbps"
        )
    except Exception:
        speedtest_info = "> Speedtest failed to run."

    # Disks
    disk_info = ""
    for part in psutil.disk_partitions():
        if disk_filter and part.mountpoint not in DISKS:
            continue

        if 'rw' in part.opts and part.fstype != "":
            usage = psutil.disk_usage(part.mountpoint)
            used = usage.used / (1024 ** 3)
            total = usage.total / (1024 ** 3)
            percent = usage.percent
            disk_info += (
                f"*Disk ({part.mountpoint}):*\n"
                f"> {used:.2f}GB / {total:.2f}GB ({percent}%)\n\n"
            )

    # Final status message
    return (
        f"*System Status: {SYSTEM_NAME}*\n\n"
        "*CPU:*\n"
        f"> {cpu_percent}%\n\n"
        "*RAM:*\n"
        f"> {ram_used:.2f}GB / {ram_total:.2f}GB ({ram_percent}%)\n\n"
        "*Speedtest:*\n"
        f"{speedtest_info}\n\n"
        f"{disk_info}"
    )

@app.message(re.compile(STATUS_KEYWORD))
def handle_status_command(message, say):
    event_id = message.get("client_msg_id") or message.get("ts")
    if event_id in seen_events:
        return  # ignore duplicate
    seen_events.add(event_id)
    print(f"Received status command: {STATUS_KEYWORD}")
    say(get_system_status())

if __name__ == "__main__":
    thread = threading.Thread(target=disk_alert_monitor, daemon=True)
    thread.start()

    handler = SocketModeHandler(app, SLACK_APP_TOKEN)
    handler.start()
   
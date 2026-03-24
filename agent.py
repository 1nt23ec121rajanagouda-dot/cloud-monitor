import psutil
import requests
import time

SERVER_URL = "https://cloud-monitor-2tzf.onrender.com/data"

while True:
    data = {
        "node": "PC-3",   # 👈 change this for each system
        "cpu": psutil.cpu_percent(), 
        "memory": psutil.virtual_memory().percent,
        "disk": psutil.disk_usage('/').percent
    }

    try:
        requests.post(SERVER_URL, json=data)
        print("Sent:", data)
    except:
        print("Error sending data")

    time.sleep(5)
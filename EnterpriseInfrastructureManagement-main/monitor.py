import psutil
import socket
import time
import requests
hostname=socket.gethostname()
print("Monitoring Agent Started")
while True:
	cpu=psutil.cpu_percent(interval=1)
	ram=psutil.virtual_memory().percent
	disk=psutil.disk_usage('/').percent
	payload = {
	    "hostname": hostname,
	    "cpu": cpu,
	    "ram": ram,
	    "disk": disk
	}

	response = requests.post(
	    "http://127.0.0.1:5000/api/metrics",
	    json=payload
	)

	print(response.json())
	print(f"Saved->CPU:{cpu}% RAM:{ram}% Disk:{disk}%")
	time.sleep(5)


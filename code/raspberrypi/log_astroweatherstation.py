#!/usr/bin/env python3

from urllib import request
from bs4 import BeautifulSoup as BS
from influxdb import InfluxDBClient
import datetime
import numpy as np
import matplotlib.pyplot as plt

# Get data from HTML
html = request.urlopen("http://10.42.0.126/index.hmtl") # Change this as necessary

# Get current time
time = datetime.datetime.utcnow()
str_time = time.strftime('%Y-%m-%dT%H-%M-%S')

# Parse data in dictionary
soup = BS(html, 'html.parser')
body = soup.body
data = {}
for elem in body:
	string = str(elem)
	try: #Field with data
		str_data = string.split('=')
		key = str_data[0][1:]
		value = str_data[1][:-1]
		if not (key in ['timestamp']):
			value = float(value)
		data[key] = value
	except:
		continue

# Parse IR image
try:
	ir_image = soup.ir_image
	ir_image = ir_image.contents[0][22:-3].split(', ')
	ir_image = np.array(ir_image).astype(float).reshape((24,32))
	# Save IR data
	with open(f'/home/aurel/Astro/log/log_ir.log', 'a') as f:
		f.write(f'{str_time}, ' + ', '.join([f'{v:.3f}' for v in ir_image.flatten()]) + '\n')
	# Save IR image
	fig, ax = plt.subplots(figsize=(8,6))
	im = ax.imshow(ir_image, cmap='seismic', vmin=-20, vmax=20, interpolation='bicubic')
	fig.colorbar(im)
	fig.tight_layout()
	fig.savefig(f'/home/aurel/Astro/log/ir_image_{str_time}.png', dpi=100)
	plt.close()
except:
    pass

# Send data to InfluxDB
host = '127.0.0.1'  # Change this as necessary
port = 8086
username = 'grafana'  # Change this as necessary
password = 'grafana'  # Change this as necessary
db = 'weatherstation'  # Change this as necessary
client = InfluxDBClient(host, port, username, password, db)
data.pop('timestamp') # Remove timestamp from data logged to InfluxDB
print(data)
payload = [{"measurement": "astroweatherstation",
	        "time": time,
            "fields": data
          }]
client.write_points(payload)

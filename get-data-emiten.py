import json, os
import pandas as pd
from time import sleep
from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException

# Create directory if not exists
import os
if not os.path.exists('data/List Emiten'):
	os.makedirs('data/List Emiten')
if not os.path.exists('data/Saham/Semua'):
	os.makedirs('data/Saham/Semua')
if not os.path.exists('data/Saham/LQ45'):
	os.makedirs('data/Saham/LQ45')

from datetime import datetime
date_format = "%Y-%m-%d"

# Read info about the dataset
# Check if the file exists
if os.path.isfile('data/info.json'):
	with open('data/info.json') as f:
		info = json.load(f)

		# Count days from last update
		last_update = datetime.strptime(info['last_update'], date_format)
		delta = datetime.today() - last_update

		# Use delta.days + 1 to determine the length
		length = delta.days + 1
else:
	# Get full year data
	length = 365

# http client
http = Chrome("C:/selenium/chromedriver.exe")

# list emiten
emiten = pd.read_csv('data/List Emiten/all.csv')
lq45 = pd.read_csv('data/List Emiten/LQ45.csv')

# get kode-kode emiten
kode_emiten = emiten['code'].values
kode_lq45 = lq45['code'].values

for code in kode_emiten:
	# link
	link = f"https://idx.co.id/umbraco/Surface/ListedCompany/GetTradingInfoSS?code={code}&length={length}"

	# send request
	# always try to repeat
	# request whenever failed
	while True:
		try:
			# send request
			http.get(link)

			# Get data
			result = http.find_element(By.CSS_SELECTOR, "pre").text
			result = json.loads(result)

			# success, we stop the while loop
			break
		except NoSuchElementException:
			print(f"Failed to get data for {code}")
			print(http.page_source)
			break
		except:
			# error, we sleep for 2 minutes
			sleep(2*60)

	# ada isinya?
	if result["replies"] == []:
		# tidak ada, print
		print(f"Tidak ada emiten dengan kode {code}")

		# loop diloncati
		continue
	else:
		try:
			# load data lama
			history = pd.read_csv(f"data/Saham/Semua/{code}.csv")
		except:
			# ga ada data lama, baru IPO
			history = pd.DataFrame({
				'date': [],
				'previous': [],
				'high': [],
				'low': [],
				'close': [],
				'change': [],
				'volume': [],
				'value': [],
				'frequency': [],
			})

	# data-data
	date = []
	previous = []
	high = []
	low = []
	close = []
	change = []
	volume = []
	value = []
	frequency = []
	

	# simpan data-data
	for data in result["replies"][::-1]:
		# hari kerja?
		if data['Date'] not in history.date.values:
			# ya
			date.append(data['Date'])
			previous.append(data['Previous'])
			high.append(data['High'])
			low.append(data['Low'])
			close.append(data['Close'])
			change.append(data['Change'])
			volume.append(data['Volume'])
			value.append(data['Value'])
			frequency.append(data['Frequency'])
			

	# data beres, simpan dalam CSV
	hari_ini = pd.DataFrame({
			'date': date,
			'previous': previous,
			'high': high,
			'low': low,
			'close': close,
			'change': change,
			'volume': volume,
			'value': value,
			'frequency': frequency,
			
		})

	# jadikan satu dgn yang lama
	new_data = pd.concat([history, hari_ini], ignore_index=True)

	# simpan
	new_data.to_csv(f"data/Saham/Semua/{code}.csv", index=False)

	# Saham LQ45?
	if code in kode_lq45:
		new_data.to_csv(f"data/Saham/LQ45/{code}.csv", index=False)

	# bobo dulu biar ga kena ban
	sleep(15)

# Update dataset info
with open('data/info.json', 'w+') as f:
	f.write(json.dumps({
		"last_update": str(datetime.now().strftime("%Y-%m-%d"))
	}))
import requests
from geopy.distance import geodesic

def AQImonitor(lon,lat):
	url = 'https://quality.data.gov.tw/dq_download_json.php?nid=40448&md5_url=05c834d071ad5b62eaf85658de4d2e6f'
	r = requests.get(url).json()
	placeTuple = (lat,lon)
	distance = 10000000
	for station in r:
		stationTuple = (station['Latitude'],station['Longitude'])
		if station['Status'] != '設備維護':
			if geodesic(placeTuple,stationTuple).km < distance:
				distance = geodesic(placeTuple,stationTuple).km
				station['AQI'] = int(station['AQI']) #轉型成數值
				if station['AQI'] <= 50:
					station['AQI'] = '綠色'
				elif 51 <= station['AQI'] <= 100:
					station['AQI'] = '黃色'
				elif 101 <= station['AQI'] <= 150:
					station['AQI'] = '橘色'
				elif 151 <= station['AQI'] <= 200:
					station['AQI'] = '紅色'
				elif 201 <= station['AQI'] <= 250:
					station['AQI'] = '紫色'
				elif 251 <= station['AQI']:
					station['AQI'] = '棗紅色'
					
				#避免空白資料
				if station['PM2.5'] == '':
					station['PM2.5'] = '無資料'
				if station['PM10'] == '':
					station['PM10'] = '無資料'

				result = [station['AQI'],station['PM2.5'],station['PM10']]

	result = '{}警戒\nPM2.5為{}\nPM10為{}'.format(result[0],result[1],result[2])

	return result
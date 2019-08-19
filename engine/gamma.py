import requests
import csv
from geopy.distance import geodesic

def gammamonitor(lon,lat):
	
	url = 'http://www.aec.gov.tw/open/gammamonitor.csv'
	r = requests.get(url)
	r.encoding = 'big5'
	rows = csv.DictReader(r.text.splitlines())
	distance = 1000000

	placeTuple = (lat,lon) #觀光地點的經緯度
	for row in rows:
		stationTuple = (row['GPS緯度'], row['GPS經度']) #監測站的經緯度
		if geodesic(placeTuple,stationTuple).km < distance:
			distance = geodesic(placeTuple,stationTuple).km
			result = [row['監測值(微西弗/時)'],row['監測站']]

	result = '監測值：{}(微西弗/時)\n在{}監測站'.format(result[0],result[1])
	return result
import requests
import time

def OWMLonLatsearch(lon,lat):
	'''
	輸入英文城市名
	以字串型別輸出特定城市天氣資訊
	'''
	URL = 'https://api.openweathermap.org/data/2.5/weather?APPID=bb1a7088074c5ed9d2e88cc9ae6d340b&lon={}&lat={}&units=metric&lang=zh_tw'.format(lon,lat)
	try:
		r = requests.get(URL).json()
		result = ''
		if r['cod'] == 200:
			result += ('經度：{}\t緯度：{}\n'.format(r['coord']['lon'],r['coord']['lat']))
			result += ('天氣狀況：{}\n'.format(r['weather'][0]['description']))
			result += ('溫度：{}\n最高溫：{}\t最低溫：{}\n'.format(r['main']['temp'],r['main']['temp_max'],r['main']['temp_min']))
			result += ('風速：{}\n'.format(r['wind']['speed']))
			#result += '日出時間：{}\n'.format(time.strftime('%H:%M:%S', time.localtime(r['sys']['sunrise'])))
			#result += '日落時間：{}\n'.format(time.strftime('%H:%M:%S', time.localtime(r['sys']['sunset'])))
			result += '日出時間：{}\n'.format(time.strftime('%H:%M:%S', time.gmtime(r['sys']['sunrise']+r['timezone'])))
			result += '日落時間：{}\n'.format(time.strftime('%H:%M:%S', time.gmtime(r['sys']['sunset']+r['timezone'])))
		elif r['cod'] == '404':
			result += r['message']
	except:
		result = '連不上伺服器'

	return result
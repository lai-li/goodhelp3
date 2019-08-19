import requests
import random
from bs4 import BeautifulSoup
from linebot.models import *

def bigImgLink(songlink):
	songContent = requests.get(songlink)
	soup = BeautifulSoup(songContent.text,'html.parser')
	newImglink = 'https:'+soup.select('.cover-art-image')[0]['style'].split('url(')[1].split(')')[0]
	return newImglink

def scrapSpotify():
	url='https://spotifycharts.com/regional'
	webContent = requests.get(url)

	soup = BeautifulSoup(webContent.text, 'html.parser')
	#因為回傳是串列，所以用for迭代器來取值
	songReplyList = []
	songList = soup.select('.chart-table tbody tr')
	for index,song in enumerate(songList):
		artist = song.select('.chart-table-track span')[0].text[3:]
		songName = song.select('.chart-table-track strong')[0].text
		songlink = song.select('.chart-table-image a')[0]['href']
		imglink = ''
		songReplyList.append([artist,songName,songlink])

		if index == 29:
			break

	random.shuffle(songReplyList)
	columnReply = []
	textReply = ''
	for song in songReplyList[0:5]:
		columnReply.append(
			ImageCarouselColumn(
				image_url=bigImgLink(song[2]),
				action=URIAction(
					label='listen',
					uri=song[2]
				)
			)
		)
		textReply += '⭐{} by {}\n💽{}\n'.format(song[1],song[0],song[2])

	return columnReply,textReply

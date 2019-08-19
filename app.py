from flask import Flask, request, abort

from linebot import (LineBotApi, WebhookHandler)
from linebot.exceptions import (InvalidSignatureError)
from linebot.models import *

from engine.currencySearch import currencySearch
from engine.AQI import AQImonitor
from engine.gamma import gammamonitor
from engine.OWM import OWMLonLatsearch
from engine.SpotifyScrap import scrapSpotify
import gspread
from oauth2client.service_account import ServiceAccountCredentials

scope=['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name('好幫手.json',scope)

client = gspread.authorize(creds)
LineBotSheet = client.open('好幫手')
userStatusSheet = LineBotSheet.worksheet('userStatus')
userInfoSheet = LineBotSheet.worksheet('userInfo')

app = Flask(__name__)

# 設定你的Channel Access Token
line_bot_api = LineBotApi('zT/x0Dp81QA2Wp781ummtpycl3OxZk0M65BPz8SoCF1H6N93cSR50LMu8beeZ5jj9iM3C2hRBBk/4meraFGsJawJa3foM4c7tTf7tDTtudwlcDIFVyfHVhJIM67FyrOrVMgoe5J1X8dFf2m2X9P6fwdB04t89/1O/w1cDnyilFU=')
# 設定你的Channel Secret
handler = WebhookHandler('e4fdbb0acac692e6c47353219f9657ea')

# 監聽所有來自 /callback 的 Post Request
@app.route("/callback", methods=['POST'])
def callback():
	# get X-Line-Signature header value
	signature = request.headers['X-Line-Signature']
	# get request body as text
	body = request.get_data(as_text=True)
	app.logger.info("Request body: " + body)
	# handle webhook body
	try:
		handler.handle(body, signature)
	except InvalidSignatureError:
		abort(400)
	return 'OK'

@app.route("/web")
def showWeb():
	return '<h1>Hello Every one</h1>'

#處理訊息
#當訊息種類為TextMessage時，從event中取出訊息內容，藉由TextSendMessage()包裝成符合格式的物件，並貼上message的標籤方便之後取用。
#接著透過LineBotApi物件中reply_message()方法，回傳相同的訊息內容
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):

	userSend = event.message.text
	userID = event.source.user_id
	try:
		cell = userStatusSheet.find(userID)
		userRow = cell.row
		userCol = cell.col
		status = userStatusSheet.cell(cell.row,2).value
	except:
		userStatusSheet.append_row([userID])
		cell = userStatusSheet.find(userID)
		userRow = cell.row
		userCol = cell.col
		status = ''
	if status == '':
		message = TextSendMessage(text='你尚未註冊,請填資料,\n請複製以下的註册碼來填寫資料')
		line_bot_api.push_message(userID,message)
		message = TextSendMessage(text=userID)
		line_bot_api.push_message(er,message)
		message = TextSendMessage(text='https://forms.gle/Dd3vT4aqd37Fdhvk6')
		userStatusSheet.update_cell(userRow, 2, '註冊中')
	elif status == '註冊中':
		try:
			infoCell = userInfoSheet.find(userID)
			userStatusSheet.update_cell(userRow, 2, '已註冊')
			message = TextSendMessage(text='Hi,{}'.format(userInfoSheet.cell(infoCell.row,3).value))
		except:
			message = TextSendMessage(text='你尚未註冊,請填資料,\n請複製以下的註册碼來填寫資料')
			line_bot_api.push_message(userID,message)
			message = TextSendMessage(text=userID)
			line_bot_api.push_message(er,message)
			message = TextSendMessage(text='https://forms.gle/KH523xXrdh66wZiV9')
			userStatusSheet.update_cell(userRow, 2, '註冊中')
	elif status == '已註冊':
		if userSend == '你好':
			userName = userInfoSheet.cell(cell.row,2).value
			message = TextSendMessage(text='Hello, ' + userName)
		elif userSend == '天氣':
			userStatusSheet.update_cell(userRow, 2, '天氣查詢')
			message = TextSendMessage(text='請傳送你的座標')
		elif userSend in ['CNY', 'THB', 'SEK', 'USD', 'IDR', 'AUD', 'NZD', 'PHP', 'MYR', 'GBP', 'ZAR', 'CHF', 'VND', 'EUR', 'KRW', 'SGD', 'JPY', 'CAD', 'HKD']:
			message = TextSendMessage(text=currencySearch(userSend))
		elif userSend == '高師大':
			message = TemplateSendMessage(
				alt_text='這是個按鈕選單',
				template=ButtonsTemplate(
					thumbnail_image_url='https://w3.nknu.edu.tw/images/sampledata/imageshow/_20190102-4.jpg',
					title='國立高雄師範大學',
					text='請選擇動作',
					actions=[
						MessageAction(
							label='美金',
							text='USD'
						),
						MessageAction(
							label='日幣',
							text='JPY'
						),
						MessageAction(
							label='你好',
							text='你好'
						),
						URIAction(
							label='帶我去高師大',
							uri='https://w3.nknu.edu.tw'
						)
					]
				)
			)
		elif userSend in ['spotify','音樂','music']:
			columnReply,textReply = scrapSpotify()
			message = TemplateSendMessage(
				alt_text=textReply,
				template=ImageCarouselTemplate(
				columns=columnReply
			)
		)
	else:
		message = TextSendMessage(text=userSend)

	line_bot_api.reply_message(event.reply_token, message)

@handler.add(MessageEvent, message=LocationMessage)
def handle_message(event):
	userID = event.source.user_id
	try:
		cell = userStatusSheet.find(userID)
		userRow = cell.row
		userCol = cell.col
		status = userStatusSheet.cell(cell.row,2).value
	except:
		userStatusSheet.append_row([userID])
		cell = userStatusSheet.find(userID)
		userRow = cell.row
		userCol = cell.col
		status = ''
	if status == '天氣查詢':
		userAddress = event.message.address
		userLat = event.message.latitude
		userLon = event.message.longitude

		weatherResult = OWMLonLatsearch(userLon,userLat)
		AQIResult = AQImonitor(userLon,userLat)
		gammaResult = gammamonitor(userLon,userLat)
		userStatusSheet.update_cell(userRow, 2, '已註冊')
		message = TextSendMessage(text='🌤天氣狀況：\n{}\n🚩空氣品質：\n{}\n\n🌌輻射值：\n{}'.format(weatherResult,AQIResult,gammaResult))
	else:
		message = TextSendMessage(text='傳地址幹嘛?')
	line_bot_api.reply_message(event.reply_token, message)

@handler.add(MessageEvent, message=StickerMessage)
def handle_message(event):
	message = TextSendMessage(text='我看不懂貼圖')
	line_bot_api.reply_message(event.reply_token, message)

import os
if __name__ == "__main__":
	port = int(os.environ.get('PORT', 5000))
	app.run(host='0.0.0.0', port=port)
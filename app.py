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
		#文字提示
		message = TextSendMessage(text='你尚未註冊,請填資料,\n請複製以下的註册碼來填寫資料')
		line_bot_api.push_message(userID,message)
		#傳送使用者ID
		message = TextSendMessage(text=userID)
		line_bot_api.push_message(userID,message)
		#傳送確認表單
		message = TemplateSendMessage(
			alt_text='註冊表單',
			template=ConfirmTemplate(
				text='請選擇【填寫表單】來註冊，完成後請點擊【完成】按鈕',
				actions=[
					URIAction(
						label='填寫表單',
						uri='line://app/1609239460-ZEJqMXl0'
					),
					MessageAction(
					label='完成',
					text='完成'
					)
				]
			)
		)
		userStatusSheet.update_cell(userRow, 2, '註冊中')
	elif status == '註冊中':
		try:
			infoCell = userInfoSheet.find(userID)
			userStatusSheet.update_cell(userRow, 2, '已註冊')
			message = TextSendMessage(text='Hi,{}您好,已註冊成功'.format(userInfoSheet.cell(infoCell.row,3).value))
		except:
			#文字提示
			message = TextSendMessage(text='你尚未註冊,請填資料,\n請複製以下的註册碼來填寫資料')
			line_bot_api.push_message(userID,message)
			#傳送使用者ID
			message = TextSendMessage(text=userID)
			line_bot_api.push_message(userID,message)
			#傳送確認表單
			message = TemplateSendMessage(
				alt_text='註冊表單',
				template=ConfirmTemplate(
					text='請選擇【填寫表單】來註冊，完成後請點擊【完成】按鈕',
					actions=[
						URIAction(
							label='填寫表單',
							uri='line://app/1609239460-ZEJqMXl0'
						),
						MessageAction(
						label='完成',
						text='完成'
						)
					]
				)
			)
			userStatusSheet.update_cell(userRow, 2, '註冊中')
	elif status == '已註冊':
		if userSend == '你好':
			userName = userInfoSheet.cell(cell.row,2).value
			message = TextSendMessage(text='Hello, ' + userName)
		elif userSend == '天氣':
			userStatusSheet.update_cell(userRow, 2, '天氣查詢')
			message = TextSendMessage(text='請傳送你的座標,請按下列的+號選項')
		elif userSend in ['CNY', 'THB', 'SEK', 'USD', 'IDR', 'AUD', 'NZD', 'PHP', 'MYR', 'GBP', 'ZAR', 'CHF', 'VND', 'EUR', 'KRW', 'SGD', 'JPY', 'CAD', 'HKD']:
			message = TextSendMessage(text=currencySearch(userSend))
		elif userSend == 'SOS':
			message = TemplateSendMessage(
				alt_text='這是個按鈕選單',
				template=ButtonsTemplate(
					thumbnail_image_url='https://i.imgur.com/Fpusd5M.png',
					title='這是您的選單按鈕',
					text='請選擇以下的項目,另有貨幣查詢功能,需輸入貨幣代碼3位大寫英文',
					actions=[
						MessageAction(
							label='醫生',
							text='醫生'
						),
						MessageAction(
							label='家人',
							text='家人'
						),
						MessageAction(
							label='報警',
							text='112'
						),
						URIAction(
							label='修改連絡資料',
							uri='https://forms.gle/J8UL7uPCJabMuWvV6'
						)
					]
				)
			)
		elif userSend == '氣候':
			message = TemplateSendMessage(
				alt_text='這是個按鈕選單',
				template=ButtonsTemplate(
					thumbnail_image_url='https://i.imgur.com/iKYedf6.png',
					title='查詢天氣',
					text='請選擇地點',
					actions=[
						MessageAction(
							label='查詢其他地方',
							text='天氣'
						),
						URIAction(
							label='你所在位置',
							uri='https://watch.ncdr.nat.gov.tw/townwarn/'
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
		elif userSend == '便當店':
			infoCell = userInfoSheet.find(userID)
			message = TextSendMessage(text='{}'.format(userInfoSheet.cell(infoCell.row,4).value))
		elif userSend == '醫生':
			infoCell = userInfoSheet.find(userID)
			message = TextSendMessage(text='{}'.format(userInfoSheet.cell(infoCell.row,6).value))
		elif userSend == '家人':
			infoCell = userInfoSheet.find(userID)
			message = TextSendMessage(text='{}'.format(userInfoSheet.cell(infoCell.row,7).value))
		elif userSend == '水電行':
			infoCell = userInfoSheet.find(userID)
			message = TextSendMessage(text='{}'.format(userInfoSheet.cell(infoCell.row,5).value))			
		else:
			message = TextSendMessage(text=userSend)
	elif status == '天氣查詢':
		message = TemplateSendMessage(
			alt_text='是否取消查詢',
			template=ConfirmTemplate(
				text='是否取消查詢？',
				actions=[
					URIAction(
							label='傳送位置資訊',
							uri='line://nv/location'
					),
					MessageAction(
						label='取消查詢',
						text='取消'
					)
				]
			)
		)
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
	elif status == '':
		#文字提示
		message = TextSendMessage(text='你尚未註冊，請填基本資料！\n請複製以下註冊碼來填寫表單')
		line_bot_api.push_message(userID,message)
		#傳送使用者ID
		message = TextSendMessage(text=userID)
		line_bot_api.push_message(userID,message)
		#傳送確認表單
		message = TemplateSendMessage(
			alt_text='註冊表單',
			template=ConfirmTemplate(
				text='請選擇[填寫表單]來註冊, 完成後請點擊[完成]按鈕',
				actions=[
					URIAction(
							label='填寫表單',
							uri='line://app/1609239460-ZEJqMXl0'
					),
					MessageAction(
						label='填寫完成',
						text='完成'
					)
				]
			)
		)				
		userStatusSheet.update_cell(userRow, 2, '註冊中')		
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

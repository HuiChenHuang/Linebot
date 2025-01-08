"""
linebot too old >>> use linebot v3
test the acho connection to linebot v3
ngrok have to update, add ...., test for 8080 port. dead of connection for webhook 
在端口 5000 不行但 8080 可以，是因為端口 5000 可能被占用或被防火牆/網絡限制。
MySQL 無法直接比較只有月份和日期的格式
mysql error:
    自動重連機制：ensure_connection 函數在每次執行查詢前檢查並重連 MySQL。
    autocommit=True：啟用自動提交，減少手動提交的問題。
    reconnect(attempts=3, delay=2)：在連線中斷時嘗試重連 3 次，每次間隔 2 秒。
    錯誤處理：使用 try-except 捕獲例外情況並回應錯誤訊息，避免程式中斷。
    這樣的修改應該能夠解決 MySQL server has gone away 的問題，並提高程式的穩定性。
圖片太大 (base64) mysql/excel value字元限制>>降相素 >> import value (base64) 
-----------------------------
run python file
cmd folder path >>>
ngrok config add-authtoken 2F5CeU3i8VMfZn3DNaX1dmN490H_7uzAnFdMkMEm2FMZq2wEY
ngrok http http://localhost:8080

"""
import base64 #圖片轉代碼
from io import BytesIO


import os
import pyimgur
from PIL import Image #pillow
import requests
import re
from flask import Flask, request, abort
from datetime import datetime
import mysql.connector
# LINEBOT 3
from linebot.v3 import WebhookHandler
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.messaging import Configuration, ApiClient, MessagingApi
from linebot.v3.messaging import ReplyMessageRequest, TextMessage, ImageMessage
from linebot.v3.webhooks import MessageEvent, TextMessageContent
from linebot.v3.webhooks.models.image_message_content import ImageMessageContent
from linebot.v3.webhooks.models.image_set import ImageSet
from linebot.v3.webhooks.models.message_content import MessageContent
app = Flask(__name__)
# Linebot webhook & API 串接
configuration = Configuration(access_token="C56ATiqV/wGsPnldACk/NzkVn+zX0eRVe0zpJ4o6BFcCoDMyvM43+hakuKdozDXxr6bIf4E61mXLqy4qYD1e7pYPidLJOOn7rON7RCnKHDvlcdnspyGrisn3CO4dpF0JX0ldbecX5TbruBgUoE44WQdB04t89/1O/w1cDnyilFU=")
handler = WebhookHandler("58f543c62c2e098c9d621a823c7c486d")
#接收 LINE 的資訊 #設定LineBot的Webhook路由
@app.route('/callback', methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature'] 
    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info('Request body: ' + body)
    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        # app.logger.info("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)
    return 'OK', 200 # Webhook驗證 

import pyimgur
#設定pyimgur
client_id="9289c3d5da76916"
def glucose_graph(client_id, imgpath):
    im = pyimgur.Imgur(client_id)
    upload_image = im.upload_image(imgpath, title="Uploaded with PyImgur")
    return upload_image.link

# Mysql 連線資訊
MYSQL_HOST  = '127.0.0.1'#127.0.0.1
MYSQL_USER = 'root'
MYSQL_PASSWORD = 'root'
MYSQL_DATABASE = 'generate_ai'

# 連接到MySQL資料庫
db_connection = mysql.connector.connect(
    host = MYSQL_HOST,
    user = MYSQL_USER,
    password = MYSQL_PASSWORD,
    database = MYSQL_DATABASE,
    autocommit=True
    )
# db_cursor = db_connection.cursor()
db_cursor = db_connection.cursor(dictionary=True, buffered=True)
# 檢查並確保 MySQL 連線有效
def ensure_connection():
    if not db_connection.is_connected():
        try:
            db_connection.reconnect(attempts=3, delay=2)
            db_cursor = db_connection.cursor(dictionary=True, buffered=True)
        except mysql.connector.Error as err:
            print(f"Error reconnecting to MySQL: {err}")
            raise

#linebot對話功能
@handler.add(MessageEvent, message=TextMessageContent)
def handle_text_A(event): #定義handle_message函數，該函數接收的資訊，貼上event的標籤，
    with ApiClient(configuration) as api_client:
        linebot_message = event.message.text
        user_id = event.source.user_id
        line_bot_api = MessagingApi(api_client)
        
        image_base64 = ''
        check_in_time = ''
        check_in_img =''
        # check_in_time (取得打卡日期時間)
        timestamp = event.timestamp / 1000  # 轉秒
        check_in_time = datetime.fromtimestamp(timestamp).strftime('%Y/%m/%d %H:%M:%S')

        # 請輸入您的生日和性別(男/女)
        if  linebot_message[0] == 'A':
            try:
                line_bot_api.reply_message_with_http_info(ReplyMessageRequest(reply_token = event.reply_token, messages = [TextMessage(text = '請輸入"*" + 您的生日+ 空一格 + 性別(男/女), 如果是8月3日女生, 請依照此格式(個位數請補0,)-> \r\n*08/03 女')]))
            except:
                line_bot_api.reply_message_with_http_info(ReplyMessageRequest(reply_token = event.reply_token, messages = [TextMessage(text = '請輸入"A" 由 "占星師"為您提供專屬服務~ ')]))
        # if linebot_message[:-2] == "%m/%d" and (linebot_message[-1] == "女" or linebot_message[-1] == "男"):
        # if re.match(r"^\d{1,2}/\d{1,2}$", linebot_message[:-2].strip()) and (linebot_message[-1].strip() == "女" or linebot_message[-1].strip() == "男"):
        if linebot_message[0]== "6": 
            line_bot_api.reply_message(ReplyMessageRequest(reply_token = event.reply_token, messages=[TextMessage(text='000000000')]))
                
        if linebot_message[0]== "*": 
            #找到user input 日期對應mysql date columns 的 星座中文
            linebot_message_date = linebot_message[1:6] #user date (input)
            # print(linebot_message_date)
            linebot_message_gender = linebot_message[-1] #user gender (input)
            # print(linebot_message_gender)
            try:
                ensure_connection()
                user_chinese_Zodiac_Sign_query = """
                    SELECT Zodiac_Sign, Generated_Zodiac_Image
                    FROM generate_ai.data 
                    WHERE Start_Date <= %s 
                    AND End_Date >= %s
                """
                db_cursor.execute(user_chinese_Zodiac_Sign_query, (linebot_message_date, linebot_message_date))
                result = db_cursor.fetchone()

                if result:
                    zodiac_sign = result['Zodiac_Sign']
                    output_analysis_query = """
                        SELECT Generated_Zodiac_Analysis, Generated_Zodiac_Image
                        FROM generate_ai.data 
                        WHERE Zodiac_Sign = %s 
                        AND Gender = %s
                    """
                    db_cursor.execute(output_analysis_query, (zodiac_sign, linebot_message_gender))
                    analysis_result = db_cursor.fetchone()
                    print(analysis_result)#user星座面向分析(dict)

                        #抓文字
                    if analysis_result:
                        analysis_text = analysis_result['Generated_Zodiac_Analysis']#dict 2 str(text)
                        print('5555555555555555555555555')
                        print(type(analysis_text))
                        print(analysis_text)
                        print('-----------------------------')
                        text_result = [TextMessage(text=analysis_text)] #生成文字
                        
                        #抓圖片
                        img_base64 = analysis_result['Generated_Zodiac_Image'] #img_base64 (str)
                        print(img_base64)
                        url_list = []
                        # image解碼 (base64 2 PIL.Image )
                        jiema = base64.b64decode(img_base64) 
                        image = BytesIO(jiema)
                        img = Image.open(image) #讀取圖片
                        # img.show() #顯示圖片

                        #save img to folder
                        img.save('./image/'+ user_id + '.png') #存到image folder 中 
                        img_path = './image/'+ user_id + '.png'#.jpg
                        img_url = glucose_graph(client_id, img_path)#img 2 url
                        # print(img_url) #https://i.imgur.com/N9KdYfp.jpg
                        text_result.append(ImageMessage(originalContentUrl=img_url, previewImageUrl=img_url))
                        # output: imgs & text 
                        line_bot_api.reply_message_with_http_info(ReplyMessageRequest(replyToken = event.reply_token, messages = text_result))

                        #刪除資料夾內的圖片(暫存產生url用)
                        folder_path = "C://中興大學//物聯網應用與資料分析//code//linebot//image"
                        files = os.listdir(folder_path)
                        for file in files:
                            if file.endswith(".jpg") or file.endswith(".png"):
                                file_path = os.path.join(folder_path, file)
                                os.remove(file_path)
                        print("資料夾中的圖片已刪除完畢")

                    else:
                        line_bot_api.reply_message_with_http_info(ReplyMessageRequest(
                            reply_token=event.reply_token,
                            messages=[TextMessage(text="未找到符合條件的分析結果。")]))
                else:
                    line_bot_api.reply_message_with_http_info(ReplyMessageRequest(
                        reply_token=event.reply_token,
                        messages=[TextMessage(text="未找到符合條件的星座。")]))

            except Exception as e:
                line_bot_api.reply_message_with_http_info(ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[TextMessage(text=f"發生錯誤：{str(e)}")]))

if __name__ == '__main__':
    app.run(port=8080, debug=True)

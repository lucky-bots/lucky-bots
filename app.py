q`#!/usr/bin/python
#-*-coding: utf-8 -*-
##from __future__ import absolute_import
###
from flask import Flask, jsonify, render_template, request
import json
import numpy as np
import pandas as pd
import xlsxwriter
import requests
import geopy.distance as ps
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,TemplateSendMessage,ImageSendMessage, StickerSendMessage, AudioSendMessage, FlexSendMessage
)
from linebot.models.template import *
from linebot import (
    LineBotApi, WebhookHandler
)

app = Flask(__name__)

lineaccesstoken = 'M2tzdziVlf46MB7CHWAoYyz0pS28eJCwkh6gwBu+4eNK1wWrORt19vgQYTi+/a0ptcU1y8ThXwfnRFVtUGyVGQH0IZUfvu6bJXwp9EAS/Y0WwnTaHTS949SFVxXdc/QDnPD+OodIW6nnUX6iKahkRwdB04t89/1O/w1cDnyilFU='
line_bot_api = LineBotApi(lineaccesstoken)

casedata = pd.read_excel('casedata.xlsx')

####################### new ########################
@app.route('/')
def index():
    return "Hello World!"


@app.route('/webhook', methods=['POST'])
def callback():
    json_line = request.get_json(force=False,cache=False)
    json_line = json.dumps(json_line)
    decoded = json.loads(json_line)
    no_event = len(decoded['events'])
    for i in range(no_event):
        event = decoded['events'][i]
        event_handle(event)
    return '',200


def event_handle(event):
    print(event)
    try:
        userId = event['source']['userId']
    except:
        print('error cannot get userId')
        return ''

    try:
        rtoken = event['replyToken']
    except:
        print('error cannot get rtoken')
        return ''
    if 'message' in event.keys():
       
        try:
            msgType = event["message"]["type"]
            msgId = event["message"]["id"]
        except:
            print('error cannot get msgID, and msgType')
            sk_id = np.random.randint(1,17)
            replyObj = StickerSendMessage(package_id=str(1),sticker_id=str(sk_id))
            line_bot_api.reply_message(rtoken, replyObj)
            return ''
    if 'postback' in event.keys():
        msgType = 'postback'

    #if msgType == "text":
    #    msg = str(event["message"]["text"])
    #    replyObj = handle_text(msg)
    #    line_bot_api.reply_message(rtoken, replyObj)
    

    # สร้าง DataFrame ที่มี 1 คอลัมน์ชื่อ 'Data'
    if msgType == "text":
       msg = event["message"]["text"]
       replyObj = handle_text(msg)
       ben = "ok"
       
       if 'x ' in msg:
          sep = msg.replace('x ','')
         # pesan = msg.replace(sep[0] + " ","")
          dataframe = pd.DataFrame({'Data' :[sep]})
          # สร้าง Pandas Excel Writer เพื่อใช้เขียนไฟล์ Excel โดยใช้ Engine เป็น xlsxwriter
          # โดยตั้งชื่อไฟล์ว่า 'simple_data.xlsx'
          writer = pd.ExcelWriter('simple_data.xlsx', engine='xlsxwriter')
          # นำข้อมูลที่สร้างไว้ในตัวแปร dataframe เขียนลงไฟล์
          dataframe.to_excel(writer, sheet_name='หน้าที่1')
 
          # จบการทำงาน Pandas Excel writer และเซฟข้อมูลออกมาเป็นไฟล์ Excel
          writer.save()  
          line_bot_api.reply_message(rtoken, ben)                              
       else:         
          line_bot_api.reply_message(rtoken, replyObj)

    if msgType == "postback":
        msg = str(event["postback"]["data"])
        replyObj = handle_postback(msg)
        line_bot_api.reply_message(rtoken, replyObj)

    if msgType == "location":
        lat = event["message"]["latitude"]
        lng = event["message"]["longitude"]
        #txtresult = handle_location(lat,lng,casedata,3)
        result = getcaseflex(lat,lng)
        replyObj = FlexSendMessage(alt_text='Flex Message alt text', contents=result)
        line_bot_api.reply_message(rtoken, replyObj)
    else:
        sk_id = np.random.randint(1,17)
        replyObj = StickerSendMessage(package_id=str(1),sticker_id=str(sk_id))
        line_bot_api.reply_message(rtoken, replyObj)
    return ''


dat = pd.read_excel('adb.xlsx')
def getdata(query):
    res = dat[dat['QueryWord']==query]
    if len(res)==0:
        return 'nodata'
    else:
        productName = res['ProductName'].values[0]
        imgUrl = res['ImgUrl'].values[0]
        #desc = res['Description'].values[0]
        #cont = res['Contact'].values[0]
        return productName,imgUrl #,desc,cont

def flexmessage(query):
    res = getdata(query)
    if res == 'nodata':
        return 'nodata'
    else:
        productName,imgUrl = res #,desc,cont = res
    flex = '''
    {
  "type": "bubble",
  "hero": {
    "type": "image",
    "url": "%s",
    "size": "full",
    "aspectRatio": "20:17",
    "aspectMode": "cover",
    "action": {
      "type": "uri",
      "uri": "https://liff.line.me/1656633739-NjWEVAWZ"
    },
    "animated": true
  },
  "body": {
    "type": "box",
    "layout": "horizontal",
    "contents": [
      {
        "type": "text",
        "text": "%s",
        "size": "xl",
        "weight": "bold",
        "color": "#cc4466",
        "align": "center"
      }
    ],
    "backgroundColor": "#000000"
  },
  "footer": {
    "type": "box",
    "layout": "horizontal",
    "spacing": "sm",
    "contents": [
      {
        "type": "button",
        "style": "primary",
        "height": "sm",
        "action": {
          "type": "uri",
          "label": "แชร์ คลิ๊ก",
          "uri": "https://liff.line.me/1656633739-NjWEVAWZ"
        }
      }
    ],
    "flex": 0,
    "backgroundColor": "#000000"
  }
}
    '''%(imgUrl,productName)#,desc,cont)
    return flex

from linebot.models import (TextSendMessage,FlexSendMessage)
import json

def handle_text(inpmessage):
    flex = flexmessage(inpmessage)
    if flex == 'nodata':
        replyObj = TextSendMessage(text=inpmessage)
    else:
        flex = json.loads(flex)
        replyObj = FlexSendMessage(alt_text='Flex Message alt text', contents=flex)
    return replyObj

def handle_postback(inpmessage):
    replyObj = TextSendMessage(text=inpmessage)
    return replyObj


def handle_location(lat,lng,cdat,topK):
    result = getdistace(lat, lng,cdat)
    result = result.sort_values(by='km')
    result = result.iloc[0:topK]
    txtResult = ''
    for i in range(len(result)):
        kmdistance = '%.1f'%(result.iloc[i]['km'])
        newssource = str(result.iloc[i]['News_Soruce'])
        txtResult = txtResult + 'ห่าง %s กิโลเมตร\n%s\n\n'%(kmdistance,newssource)
    return txtResult[0:-2]


def getcaseflex(lat,lng):
    url = 'http://botnoiflexapi.herokuapp.com/getnearcase?lat=%s&long=%s'%(lat,lng)
    res = requests.get(url).json()
    return res

def getdistace(latitude, longitude,cdat):
  coords_1 = (float(latitude), float(longitude))
  ## create list of all reference locations from a pandas DataFrame
  latlngList = cdat[['Latitude','Longitude']].values
  ## loop and calculate distance in KM using geopy.distance library and append to distance list
  kmsumList = []
  for latlng in latlngList:
    coords_2 = (float(latlng[0]),float(latlng[1]))
    kmsumList.append(ps.vincenty(coords_1, coords_2).km)
  cdat['km'] = kmsumList
  return cdat


if __name__ == '__main__':
    app.run(debug=True)

from django.shortcuts import render
from django.conf import settings
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt
# Create your views here.

from linebot import LineBotApi, WebhookHandler, WebhookParser
from linebot.exceptions import InvalidSignatureError, LineBotApiError
from linebot.models import MessageEvent, TextSendMessage, ImageSendMessage
from bs4 import BeautifulSoup
import requests

line_bot_api = LineBotApi(settings.LINE_CHANNEL_ACCESS_TOKEN)
parse = WebhookParser(settings.LINE_CHANNEL_SECRET)


def get_biglottery():
    try:
        url = 'https://www.taiwanlottery.com.tw/lotto/lotto649/history.aspx'
        resp = requests.get(url)
        soup = BeautifulSoup(resp.text, 'lxml')
        trs = soup.find('table', class_="table_org td_hm").find_all('tr')
        data1 = [td.text.strip() for td in trs[0].find_all('td')]
        data2 = [td.text.strip() for td in trs[1].find_all('td')]
        numbers = [td.text.strip() for td in trs[4].find_all('td')][1:]
        data = ''
        for i in range(len(data1)):
            data += f'{data1[i]}:{data2[i]}\n'
        data += ','.join(numbers[:-1])+' 特別號:'+numbers[-1]
        print(data)

        return data
    except Exception as e:
        print(e)
        return '取得大樂透號碼，請稍候再試……'


def lottery(request):
    text = get_biglottery().replace('\n', '<br>')
    return HttpResponse(f'<h1>{text}</h1>')


@csrf_exempt
def callback(request):
    if request.method == 'POST':
        signature = request.META['HTTP_X_LINE_SIGNATURE']
        body = request.body.decode('utf-8')
        try:
            events = parse.parse(body, signature)
        except InvalidSignatureError:
            return HttpResponseForbidden()
        except LineBotApiError:
            return HttpResponseBadRequest()
        for event in events:
            if isinstance(event, MessageEvent):
                text = event.message.text
                message = None
                print(text)
                if text == '1':
                    message = '早安'
                elif text == '2':
                    message = '午安'
                elif text == '3':
                    message = '晚安'
                elif '早安' in text:
                    message = '早安你好!'
                elif '捷運' in text:
                    # 台北/台中/高雄
                    mrts = {
                        '台北': 'https://web.metro.taipei/pages/assets/images/routemap2023n.png',
                        '台中': 'https://assets.piliapp.com/s3pxy/mrt_taiwan/taichung/20201112_zh.png?v=2',
                        '高雄': 'https://assets.piliapp.com/s3pxy/mrt_taiwan/kaohsiung/202210_zh.png',
                    }

                    # 以"台北捷運圖"為預設值，以防萬一沒有取到值，
                    image_url = 'https://web.metro.taipei/pages/assets/images/routemap2023n.png'

                    for mrt in mrts:  # mrts --> keys, mrt --> value
                        if mrt in text:
                            image_url = mrts[mrt]
                            print(image_url)  # 為了DEBUG用，可以把值印出來看一下
                            break
                elif '樂透' in text:
                    message = get_biglottery()
                else:
                    message = '抱歉，我不知道你說什麼?'

                if message is None:
                    message_obj = ImageSendMessage(image_url, image_url)
                else:
                    message_obj = TextSendMessage(text=message)
                # if event.message.text=='hello':
                line_bot_api.reply_message(event.reply_token, message_obj)
                #TextSendMessage(text='hello world')
        return HttpResponse()
    else:
        return HttpResponseBadRequest()


def index(request):
    return HttpResponse("<h1>您好，我是AI機器人</h1>")

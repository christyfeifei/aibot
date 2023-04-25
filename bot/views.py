from django.shortcuts import render
from django.conf import settings
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt
# Create your views here.

from linebot import LineBotApi, WebhookHandler, WebhookParser
from linebot.exceptions import InvalidSignatureError, LineBotApiError
from linebot.models import MessageEvent, TextSendMessage, ImageSendMessage

line_bot_api = LineBotApi(settings.LINE_CHANNEL_ACCESS_TOKEN)
parse = WebhookParser(settings.LINE_CHANNEL_SECRET)


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
                    image_url = 'https://web.metro.taipei/pages/assets/images/routemap2023n.png'
                else:
                    message = '抱歉，我不知道你說什麼?'

                if message is None:
                    message_obj = ImageSendMessage(image_url, image_url)
                else:
                    message_obj = ImageSendMessage(text=message)
                # if event.message.text=='hello':
                line_bot_api.reply_message(event.reply_token, message_obj)
                #TextSendMessage(text='hello world')
        return HttpResponse()
    else:
        return HttpResponseBadRequest()


def index(request):
    return HttpResponse("<h1>您好，我是AI機器人</h1>")

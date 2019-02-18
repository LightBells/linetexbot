# -*- coding: utf-8 -*-

#  Licensed under the Apache License, Version 2.0 (the "License"); you may
#  not use this file except in compliance with the License. You may obtain
#  a copy of the License at
#
#       https://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#  WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#  License for the specific language governing permissions and limitations
#  under the License.

import os
import sys
import urllib.parse
import traceback
from argparse import ArgumentParser
from flask import Flask, request, abort
from linebot import (LineBotApi, WebhookHandler)
from linebot.exceptions import (InvalidSignatureError)
from linebot.models import (MessageEvent, TextMessage, TextSendMessage,
                            ImageSendMessage)

app = Flask(__name__)

# get channel_secret and channel_access_token from your environment variable
channel_secret = os.getenv('LINE_CHANNEL_SECRET', None)
channel_access_token = os.getenv('LINE_CHANNEL_ACCESS_TOKEN', None)
if channel_secret is None:
    print('Specify LINE_CHANNEL_SECRET as environment variable.')
    sys.exit(1)
if channel_access_token is None:
    print('Specify LINE_CHANNEL_ACCESS_TOKEN as environment variable.')
    sys.exit(1)

line_bot_api = LineBotApi(channel_access_token)
handler = WebhookHandler(channel_secret)


@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    print(body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'


@handler.add(MessageEvent, message=TextMessage)
def message_text(event):
    image_base = "https://chart.apis.google.com/chart?cht=tx&chs=50&chl="
    if (event.source.type == "group" or event.source.type == "room"):
        text = event.message.text
        if text.startswith("t:") == 0 or text.startswith("T:") == 0:
            image_url = image_base + urllib.parse.quote("\\displaystyle " +
                                                        text[1:-1])
            try:
                line_bot_api.reply_message(
                    event.reply_token,
                    ImageSendMessage(
                        original_content_url=image_url,
                        preview_image_url=image_url))
            except Exception as e:
                except_str = traceback.format_exc()
                try:
                    line_bot_api.reply_message(event.reply_token,
                                               TextSendMessage(except_str))
                except Exception as e:
                    print(e)
    else:
        try:
            image_url = image_base + urllib.parse.quote("\\displaystyle " +
                                                        event.message.text)
            line_bot_api.reply_message(
                event.reply_token,
                ImageSendMessage(
                    original_content_url=image_url,
                    preview_image_url=image_url))
        except Exception as e:
            except_str = traceback.format_exc()
            try:
                line_bot_api.reply_message(event.reply_token,
                                           TextSendMessage(except_str))
            except Exception as e:
                print(e)


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
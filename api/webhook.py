#  -----------------------------------------------------------------------------
#   <webhook.py>
#    -
#  -----------------------------------------------------------------------------
#   Version 0 (2022/05/07 10:13)
#    -
#  -----------------------------------------------------------------------------
#   (C) 2022 masahiro nishimura. All rights reserved.
#  -----------------------------------------------------------------------------


import json
import requests

class Webhook():
    def __init__(self, body = None):
        with open('config.json', 'r') as f:
            config = json.load(f)
        self.__url = config["webhook_url"]

    @property
    def body(self):
        return self.__body

    @body.setter
    def body(self, val):
        self.__body = val

    @property
    def url(self):
        return self.__url

    def send(self, body):
        requests.post(self.url,json.dumps(body),headers={'Content-Type': 'application/json'})
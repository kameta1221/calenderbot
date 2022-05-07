#  -----------------------------------------------------------------------------
#   <webhookData.py>
#    - Messages from the Bot will be sent using the Discord Webhook.
#    - Using the Webhook makes it easy to change the avatar name and sender name for each message and format the embeds
#  -----------------------------------------------------------------------------
#   Version 0 (2022/05/07 10:08)
#    -
#  -----------------------------------------------------------------------------
#   (C) 2022 masahiro nishimura. All rights reserved.
#  -----------------------------------------------------------------------------


import json

class WebhookContent():
    def __init__(self):
        with open('config.json', 'r') as f:
            config = json.load(f)
            self.__config = config
            self.__userName = config["webhook"].get('user_name')
            self.__avatarUrl = config["webhook"].get('avatar_url')
            self.__color = config["webhook"].get('color')

    @property
    def config(self):
        return self.__config

    @property
    def userName(self):
        return self.__userName

    @userName.setter
    def userName(self, val):
        self.__userName = val

    @property
    def color(self):
        return self.__color

    @color.setter
    def color(self, val):
        self.__color = val

    @property
    def avatarUrl(self):
        return self.__avatarUrl

    @avatarUrl.setter
    def avatarUrl(self, val):
        self.__avatarUrl = val

    def createMessage(self, message):
        body = {
            "username": self.userName,
            "avatar_url": self.avatarUrl,
            "content" : message,
            "embeds": []
        }
        return  body

    def createEmbeds(self, data):
        embeds = {
            "title": data.summary,
            "description": f"{data.date} {data.time}",
            "color": int(self.color, 16),
            "footer": {
                "icon_url": self.avatarUrl,
                "text": data.eventId
            },
        }
        if data.description:
            fields = {
                "fields": [
                    {
                        "name": "詳細",
                        "value": data.description,
                    }
                ]
            }
            embeds.update(fields)
        return embeds

    def createLongEventEmbeds(self, data):
        embeds = {
            "title": data.summary,
            "description": f"{data.date} 〜 {data.endDate}",
            "color": int(self.color, 16),
            "footer": {
                "icon_url": self.avatarUrl,
                "text": data.eventId
            },
        }
        if data.description:
            fields = {
                "fields": [
                    {
                        "name": "詳細",
                        "value": data.description,
                    }
                ]
            }
            embeds.update(fields)
        return embeds

class WebhookData():
    @property
    def content(self):
        return self.__content

    @content.setter
    def content(self, val):
        self.__content = val

    @property
    def summary(self):
        return self.__summary

    @summary.setter
    def summary(self, val):
        self.__summary = val

    @property
    def description(self):
        return self.__description

    @description.setter
    def description(self, val):
        self.__description = val

    @property
    def date(self):
        return self.__date

    @date.setter
    def date(self, val):
        self.__date = val

    @property
    def time(self):
        return self.__time

    @time.setter
    def time(self, val):
        self.__time = val

    @property
    def eventId(self):
        return self.__eventId

    @eventId.setter
    def eventId(self, val):
        self.__eventId = val
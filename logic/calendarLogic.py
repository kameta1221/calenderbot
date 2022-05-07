#  -----------------------------------------------------------------------------
#   <calendarLogic.py>
#    -
#  -----------------------------------------------------------------------------
#   Version 0 (2022/05/07 10:22)
#    -
#  -----------------------------------------------------------------------------
#   (C) 2022 masahiro nishimura. All rights reserved.
#  -----------------------------------------------------------------------------


import json
from api.calendarApi import CalendarApi
from data.calendarData import CalendarData
from data.calendarData import CalendarContent
from api.webhook import Webhook
from data.webhookData import WebhookData
from data.webhookData import WebhookContent


class CalendarLogic():
    def __init__(self):
        with open('config.json', 'r') as f:
            config = json.load(f)
            self.__config = config
            self.__message = config['webhook'].get('message')

    @property
    def config(self):
        return self.__config

    @property
    def message(self):
        return self.__message

    # カレンダーのURLを返す
    def calendarUrl(self):
        webhook = Webhook()
        webhookContent = WebhookContent()

        message = self.message.get('calendar_message')
        calendarUrl = self.config['calendar'].get('calendar_url')
        body = webhookContent.createMessage(message + calendarUrl)
        webhook.send(body)

    # 一週間分の予定を返す
    def get(self):
        try:
            calendar = CalendarApi()
            result = calendar.get()

            # メッセージ送信処理
            webhook = Webhook()
            webhookData = WebhookData()
            webhookContent = WebhookContent()

            if result == []:
                message = self.message.get('event_none_message')
                body = webhookContent.createMessage(message)
            else:
                message = self.message.get('event_message')
                body = webhookContent.createMessage(message)

                for event in result:
                    webhookData.summary = event['summary']
                    webhookData.description = event.get('description', '')
                    webhookData.eventId = event['id']

                    # 終日予定と時間予定を区別しフォーマットを設定
                    start = event['start'].get('dateTime', '').split('T')
                    if start != ['']:
                        webhookData.date = start[0].replace('-', '/')
                        webhookData.time = start[1].replace(':00+09:00', '')
                        embeds = webhookContent.createEmbeds(webhookData)
                    else:
                        webhookData.date = event["start"].get("date").replace('-', '/')
                        webhookData.endDate = event["end"].get("date").replace('-', '/')
                        embeds = webhookContent.createLongEventEmbeds(webhookData)

                    body["embeds"].append(embeds)

            webhook.send(body)

        except Exception as e:
            print(e)
            webhook = Webhook()
            webhookData = WebhookData()
            webhookContent = WebhookContent()
            message = self.message.get('event_error_message')
            body = webhookContent.createMessage(message)

            webhook.send(body)

    def insert(self, event):
        try:
            calendar = CalendarApi()
            calData = CalendarData()
            calContent = CalendarContent()

            content = event.split(' ')
            calData.date = content[0]
            date = calData.date.split('/')
            calData.year = int(date[0])
            calData.month = int(date[1])
            calData.day = int(date[2])

            calData.time = content[1]
            time = calData.time.split(':')
            calData.hour = int(time[0])
            calData.minute = int(time[1])

            calData.summary = content[2]
            if len(content) == 4:
                calData.description = content[3]
            else:
                calData.description = ''

            body = calContent.createInsertData(calData)
            result = calendar.insert(body)
            calData.eventId = result["id"]

            # Webhookメッセージ送信部分
            webhook = Webhook()
            webhookData = WebhookData()
            webhookContent = WebhookContent()

            webhookData.summary = calData.summary
            webhookData.description = calData.description
            webhookData.eventId = calData.eventId
            webhookData.date = calData.date
            webhookData.time = calData.time

            message = self.config["webhook"].get('webhook').get('insert_message')
            body = webhookContent.createMessage(message)
            embeds = webhookContent.createEmbeds(webhookData)
            body["embeds"].append(embeds)

            webhook.send(body)

        except Exception as e:
            print(e)
            webhook = Webhook()
            webhookContent = WebhookContent()
            message = self.config["webhook"].get('insert_error_message')
            body = webhookContent.createMessage(message)

            webhook.send(body)

    def insertLongEvent(self, event):
        try:
            calendar = CalendarApi()
            calData = CalendarData()
            calContent = CalendarContent()

            content = event.split(' ')
            calData.date = content[0].replace('/', '-')

            calData.endDate = content[1].replace('/', '-')

            calData.summary = content[2]
            if len(content) == 4:
                calData.description = content[3]
            else:
                calData.description = ''

            body = calContent.createLongEventData(calData)
            result = calendar.insert(body)
            calData.eventId = result["id"]

            webhook = Webhook()
            webhookData = WebhookData()
            webhookContent = WebhookContent()

            message = self.message.get('insert_message')
            body = webhookContent.createMessage(message)

            webhookData.summary = calData.summary
            webhookData.description = calData.description
            webhookData.eventId = calData.eventId
            webhookData.date = calData.date.replace('-', '/')
            webhookData.endDate = calData.endDate.replace('-', '/')
            embeds = webhookContent.createLongEventEmbeds(webhookData)
            body["embeds"].append(embeds)

            webhook.send(body)

        except Exception as e:
            print(e)
            webhook = Webhook()
            webhookContent = WebhookContent()
            message = self.message.get('long_event_error_message')
            body = webhookContent.createMessage(message)

            webhook.send(body)

    def delete(self, event):
        try:
            calendar = CalendarApi()
            calendar.delete(event)

            webhook = Webhook()
            webhookContent = WebhookContent()

            message = self.message.get('delete_message')
            body = webhookContent.createMessage(message)
            webhook.send(body)
        except Exception as e:
            print(e)
            webhook = Webhook()
            webhookContent = WebhookContent()
            message = self.message.get('delete_error_message')
            body = webhookContent.createMessage(message)

            webhook.send(body)
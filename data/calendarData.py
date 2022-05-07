#  -----------------------------------------------------------------------------
#   <calendarData.py>
#    -
#  -----------------------------------------------------------------------------
#   Version 0 (2022/05/07 10:32)
#    -
#  -----------------------------------------------------------------------------
#   (C) 2022 masahiro nishimura. All rights reserved.
#  -----------------------------------------------------------------------------


import datetime

class CalendarContent():
    def createInsertData(self, data):
        body = {
            'summary':data.summary,
            'description': data.description,
            'start':{
                'dateTime': datetime.datetime(data.year, data.month, data.day, data.hour, data.minute).isoformat(),
                'timeZone': 'Japan'
            },
            'end': {
                'dateTime': datetime.datetime(data.year, data.month, data.day, data.hour+1, data.minute).isoformat(),
                'timeZone': 'Japan'
            },
        }
        return body

    def createLongEventData(self, data):
        body = {
            'summary':data.summary,
            'description': data.description,
            'start':{
                'date': data.date,
                'timeZone': 'Japan'
            },
            'end': {
                'date': data.endDate,
                'timeZone': 'Japan'
            },
        }
        return body

class CalendarData():
    @property
    def eventId(self):
        return self.__eventId

    @eventId.setter
    def eventId(self, val):
        self.__eventId = val

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
    def year(self):
        return self.__year

    @year.setter
    def year(self, val):
        self.__year = val

    @property
    def month(self):
        return self.__month

    @month.setter
    def month(self, val):
        self.__month = val

    @property
    def day(self):
        return self.__day

    @day.setter
    def day(self, val):
        self.__day = val

    @property
    def hour(self):
        return self.__hour

    @hour.setter
    def hour(self, val):
        self.__hour = val

    @property
    def minute(self):
        return self.__minute

    @minute.setter
    def minute(self, val):
        self.__minute = val

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
    def endDate(self):
        return self.__endDate

    @endDate.setter
    def endDate(self, val):
        self.__endDate = val
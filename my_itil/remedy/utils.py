#!/usr/bin/python
# -*- coding: utf-8 -*-

import datetime

def stamp_to_date(date_int):
    date_date = datetime.datetime(1970, 1, 1) + datetime.timedelta(seconds=date_int-1)
    return date_date.strftime('%Y-%m-%d %H:%M')

def date_to_stamp(date_date):
    date_int =  (date_date - datetime.datetime(1970, 1, 1)).total_seconds()
    return int(date_int)

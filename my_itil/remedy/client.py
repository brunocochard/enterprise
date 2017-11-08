#!/usr/bin/python
# -*- coding: utf-8 -*-

from pyars import erars, cars
from my_it.remedy.utils import stamp_to_date, date_to_stamp
import datetime

class Remedy_Client(object):
    def __init__(self, server, username, password):
        self.server='1.1.1.1'
        self.username = username
        self.session = erars.erARS()
        self.login(server=self.server, username=username, password=password)

    def get_entries(self, form, query, fields, sortList, maxRetrieve):
        try:
            print "get entries start"
            print query
            (entries, numMatches) = self.session.GetListEntryWithFields(form, query, fields, sortList=sortList, maxRetrieve=maxRetrieve)
            # print entries
            print "get entries done"
            return entries, numMatches
        except:
            print "Read error: "
            print self.session.statusText()
            raise

    def get_form_fields(self, form):
        try:
            return self.session.GetFieldTable(form)
        except:
            print "Read error: " + self.session.statusText()
            raise

    def create_entry(self, form, fieldValue):
        try:
            return self.session.createEntry(form, fieldValue)
        except:
            print "Create error: " + self.session.statusText()
            raise

    def get_entry(self, form, entry_id):
        try:
            return self.session.GetEntry(form, entry_id)
        except:
            print "Read error: " + self.session.statusText()
            raise

    def update_entry(form, entry_id, value):
        try:
            return self.session.SetEntry(form, entry_id, value)
        except:
            print "Update error: " + self.session.statusText()
            raise

    def login(self, server, username, password):
        try:
            self.session.Login(server=server, username=username, password=password, charSet='utf-8')
        except:
            print "Login error: " + self.session.statusText()
            raise

    def status(self):
        return self.session.statusText()

    def logoff(self):
        self.session.Logoff()

    def __enter__(self):
        """
            auto-logoff when object used with "with" e.g.
            > with Remedy_client(uname, pwd) as client: #do stuff, query, create...
        """
        return self

    def __exit__(self, type, value, traceback):
        """
            auto-logoff when object used with "with" e.g.
            > with Remedy_client(uname, pwd) as client: #do stuff, query, create...
        """
        self.logoff()

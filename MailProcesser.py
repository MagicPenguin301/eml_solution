"""
To sort mail texts according to their dates.
"""
import datetime
import MailGetter
import os

def sorted_mail(metadata_mails):
    return sorted(metadata_mails,key=lambda x: x[0]['date'])
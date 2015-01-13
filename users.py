# -*- coding: utf-8 -*-
"""
Synch the local MongoDB database with the Appcelerator Cloud Services used
by the Raduga mobile application. This way we import the user data.

Requires the accompagnying Cloud Services Key `ACS_KEY` in local_settings.py.
Find this in the management panel of Appcelerator.
In your Titanium Application, this corresponds to `acs-api-key-development` or
`acs-api-key-production` in your tiapp.xml.

Also requires a session key.
You should obtain a session key by logging in as a user through CURL (first create
the user in the management interface)
cf: http://docs.appcelerator.com/cloud/latest/#!/api/Users-method-login
    curl -b cookies.txt -c cookies.txt -F "login=mgoff@appcelerator.com" -F "password=food" https://api.cloud.appcelerator.com/v1/users/login.json?key=<YOUR APP APP KEY>&pretty_json=true
The session key will be part of the JSON response:

FIXME: this is something of a hack. Best not at all depend on Appcelerator Cloud Services
and just do user management in this EVE application.
"""

import json
import sys
import urllib2
from datetime import datetime

import pymongo
import pytz

from utils import logger

client = pymongo.MongoClient()
db = client.raduga

try:
    from settings import ACS_KEY
except ImportError:
    logger.error("no valid API key for the cloud back-end")
    sys.exit()

def synch_users():
    logger.debug("downloading user data from Apccelerator Cloud Services")
    
    npage = 1
    users = []
    
    while True:
        url = "https://api.cloud.appcelerator.com/v1/users/query.json?key=%s&page=%s" % (ACS_KEY, npage)
        f = urllib2.urlopen(url)
        data = json.load(f)
        
        users += data['response']['users']
        
        logger.debug("retrieved page %s of %s of user data" % (npage, data['meta']['total_pages']))
        if data['meta']['total_pages'] == npage:
            break
        
        npage += 1
    
    logger.debug("updating local mongodb database")
    for user in users:
        db.users.update({"id": user['id']}, user, upsert=True)
    
    db.meta.update({"subject": "users"}, {"updated": datetime.now(pytz.utc), "subject": "users"}, upsert=True)
    return True

def delayed_synch_users():
    """
    Only synch the database if the last synch is longer than 5 minutes ago
    """
    meta = db.meta.find_one({"subject": "users"})
    if not meta:
        return synch_users()
    updated = meta['updated'].replace(tzinfo=pytz.UTC)
    difference = datetime.now(pytz.utc) - updated
    if difference.total_seconds() > 300:
        return synch_users()
    
    logger.debug("requested to synch the database, but it was recently synched")

def slightly_delayed_synch_users():
    """
    Only synch the database if the last synch is longer than 2 seconds ago
    """
    meta = db.meta.find_one({"subject": "users"})
    if not meta:
        return synch_users()
    updated = meta['updated'].replace(tzinfo=pytz.UTC)
    difference = datetime.now(pytz.utc) - updated
    if difference.total_seconds() > 2:
        return synch_users()
    
    return False

if __name__ == "__main__":
    delayed_synch_users()

# -*- coding: utf-8 -*-
"""
Synch the local MongoDB database with the Appcelerator Cloud Services
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

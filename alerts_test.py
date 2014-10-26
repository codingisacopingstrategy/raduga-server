# -*- coding: utf-8 -*-

import pymongo
import sys

try:
    from settings import TEST_USER
except ImportError:
    sys.exit("Define a TEST_USER in local_settings.py")

from users import synch_users

synch_users()
client = pymongo.MongoClient()
db = client.raduga

from alerts import send_alert

user = db.users.find_one({"id" : TEST_USER})
photo = db.photos.find_one({})

if not 'badge' in user['custom_fields']:
    user['custom_fields']['badge'] = 0

if user['custom_fields']['language'] == 'ru':
    message = "%s обнаружил радугу возле %s" % (photo['user']['username'], photo['custom_fields']['name_ru'])
else:
    message = "%s spotted a rainbow near %s" % (photo['user']['username'], photo['custom_fields']['name_en'])

send_alert({
    "channel": "raduga_predictions",
    "to_ids": [user['id']],
    "payload": {
        "alert": message,
        "type": "rainbow_spotted",
        "sound": "default",
        "vibrate": True,
        "username": photo['user']['username'],
        "name_en": photo['custom_fields']['name_en'],
        "name_ru": photo['custom_fields']['name_ru'],
        "photo_id": photo['id'],
        "badge": user['custom_fields']['badge'] + 1
    }
 })

db.users.update({"id" : TEST_USER}, {'$inc': {'custom_fields.badge': 1}})

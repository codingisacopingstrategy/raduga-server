# -*- coding: utf-8 -*-

import json
import sys
import urllib2

import pymongo

from utils import logger
from settings import *
from users import synch_users

client = pymongo.MongoClient()
db = client.raduga

def send_alert(post_data):
    url = "https://api.cloud.appcelerator.com/v1/push_notification/notify.json?key=%s" % ACS_KEY
    req = urllib2.Request(url)
    req.add_header('Content-Type','application/json')
    req.add_header('Cookie', '_session_id=%s' % ACS_SESSION_ID)
    
    try:
        response = urllib2.urlopen(req, json.dumps(post_data))
        parsed_response = json.loads(response.read())
        logger.debug( (u"succesfully sent push notification no %s" % parsed_response['response']['push_notification']['id']).encode("utf-8") )
    except urllib2.URLError as e:
        error_response = json.loads(e.read())
        logger.warn("push notification failed with error code %s and message %s" % (e.code, error_response['meta']['message']))

def rainbow_prediction_alert(slug):
    cities = json.load(open(os.path.join(GFS_FOLDER, slug, '%s.rainbow_cities.json' % slug)))
    city_names = [city['name_en'] for city in cities]
    
    synch_users()
    
    users = db.users.find()
    rainbow_user_ids = []
    
    for user in users:
        if 'custom_fields' in user and 'name_en' in user['custom_fields']:
            if user['custom_fields']['name_en'] in city_names:
                rainbow_user_ids.append(user['id'])
    
    if len(rainbow_user_ids) > 0:
        logger.debug("%s users in rainbow areas for this forecast" % len(rainbow_user_ids))
        send_alert({
            "channel": "raduga_predictions",
            "to_ids": rainbow_user_ids,
            "payload": {
                "alert": "You have a large chance of rainbows!",
                "some_custom_property": "we can send custom properties"
            }
         })
    else:
        logger.debug("no people in rainbow areas for this forecast")

if __name__ == "__main__":
    
    # When used as: python alerts.py 2014052915
    if len(sys.argv) > 1:
        rainbow_prediction_alert(argv[1])
        sys.exit()
    
    forecasts = [forecast for forecast in get_forecast_info() if forecast['future'] == True]
    
    if len(forecasts) == 0:
        logger.debug("no future rainbow city predictions found, aborting. rainbow alerts only sent on future predictions. run the script with a specific slug as argument to override")
        sys.exit()
    
    slug = forecasts[-1]['slug']
    logger.debug("%s future rainbow city prediction(s) found, using the most recent one, %s" % (len(forecasts), slug))
    rainbow_prediction_alert(slug)
    
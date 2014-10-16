# -*- coding: utf-8 -*-

import json
import sys
import urllib2

import pymongo

from utils import logger
from settings import *
from users import synch_users, delayed_synch_users

client = pymongo.MongoClient()
db = client.raduga

cities = json.load(open(os.path.join(os.path.abspath(os.path.dirname(__file__)), "scrape", "cities.json")))

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
        logger.warn( ("push notification failed with error code %s and message %s" % (e.code, error_response['meta']['message'])).encode('utf8') )

def rainbow_spotted_alert(photo):
    global cities
    
    delayed_synch_users()
    
    city_name_en = photo['custom_fields']['name_en']
    cities_to_check = [ city_name_en ]
    
    for city in cities:
        if city['name_en'] == city_name_en:
            cities_to_check += city['nearby']
            break
    
    users = db.users.find({ "custom_fields.name_en" : { "$in": cities_to_check }, "custom_fields.notifications" : True, "user.username" : { "$ne" : photo['user']['username'] } })
    
    for user in users:
        if not 'badge' in user['custom_fields']:
            user['custom_fields']['badge'] = 0
        
        if user['custom_fields']['language'] == 'ru':
            message = u"%s обнаружил радугу возле %s" % (photo['user']['username'], photo['custom_fields']['name_ru'])
        else:
            message = "%s spotted a rainbow near %s" % (photo['user']['username'], photo['custom_fields']['name_en'])
    
        send_alert({
            "channel": "raduga_predictions",
            "to_ids": [user['id']],
            "payload": {
                "alert": message,
                "type": "rainbow_spotted",
                "username": photo['user']['username'],
                "name_en": city_name_en,
                "name_ru": photo['custom_fields']['name_ru'],
                "badge": user['badge'] + 1
            }
        })
        
        db.users.update({"id" : user['id']}, {'$inc': {'custom_fields.badge': 1}})
    
    logger.debug( ("after photo %s was uploaded, we found user %s in the same area" % (photo['id'], user['username']) ).encode('utf8'))


def rainbow_prediction_alert(slug):
    rainbow_cities = json.load(open(os.path.join(GFS_FOLDER, slug, '%s.rainbow_cities.json' % slug)))
    city_names = [city['name_en'] for city in rainbow_cities]
    
    synch_users()
    
    users = db.users.find()
    
    people = False
    for user in users:
        if 'custom_fields' in user and 'name_en' in user['custom_fields']:
            if user['custom_fields']['name_en'] in city_names:
                people = True
                
                if not 'badge' in user['custom_fields']:
                    user['custom_fields']['badge'] = 0
                
                if user['custom_fields']['language'] == 'ru':
                    message = u"Сегодня днем у вас есть большой шанс увидеть радугу!"
                else:
                    message = "You have a large chance of rainbows!"
            
                logger.debug("%s in rainbow area for this forecast" % user['user_name'])
                send_alert({
                    "channel": "raduga_predictions",
                    "to_ids": [user['id']],
                    "payload": {
                        "alert": message,
                        "type": "rainbow_prediction",
                    }
                 })
                
                db.users.update({"id" : user['id']}, {'$inc': {'custom_fields.badge': 1}})

    
    if not people:
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
    
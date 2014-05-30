# -*- coding: utf-8 -*-

import os
import sys
import math

from eve import Eve
from PIL import Image
from eve.auth import TokenAuth
from bson.objectid import ObjectId

from alerts import rainbow_spotted_alert
from settings import *
from utils import logger

from flask import request, Response, current_app as app
from functools import wraps


class SimpleTokenAuth(TokenAuth):
    """
    This uses the username from HTTP basic authentication as its token
    (Slightly confusing: I would have thought it would use the `Authorization`: header)
    
    So:
    
    `curl -i -d {"key":"value","key","value",etc...} -H 'Content-Type: application/json' --user 436641f6e1usertoken: http://127.0.0.1:5000/photos`
    
    """
    def check_auth(self, token, allowed_roles, resource, method):
        print "checking auth"
        accounts = app.data.driver.db['accounts']
        return accounts.find_one({'token': token})

# Uploaded photo info needs to correspond to this schema, or it will be rejected.
# Full example:
# curl -i -d '{"content_type":"image/jpeg","created_at":"2014-04-12T18:52:05+0000","custom_fields":{"coordinates":[[41.36667,56.85]],"name_en":"Shuya","name_ru":"\u0428\u0443\u044f"},"exif":{"create_date":"2005-07-20T20:08:38+0000","height":1600,"make":"Canon","model":"CanonPowerShotA60","shutter_speed":"1/800","width":1200},"filename":"upload_test_photo.jpg","md5":"0bfa85371e2d64f771b9209426827c74","processed":true,"size":203267,"updated_at":"2014-04-12T18:52:05+0000","urls":{"large_1024":"http://storage.cloud.appcelerator.com/X3Eaph9KUC6Z1Lga4YOq8lRY1DWESOZD/photos/7c/74/53498b54ed8cdc76d900019e/upload_test_photo_large_1024.jpg","medium_500":"http://storage.cloud.appcelerator.com/X3Eaph9KUC6Z1Lga4YOq8lRY1DWESOZD/photos/7c/74/53498b54ed8cdc76d900019e/upload_test_photo_medium_500.jpg","medium_640":"http://storage.cloud.appcelerator.com/X3Eaph9KUC6Z1Lga4YOq8lRY1DWESOZD/photos/7c/74/53498b54ed8cdc76d900019e/upload_test_photo_medium_640.jpg","original":"http://storage.cloud.appcelerator.com/X3Eaph9KUC6Z1Lga4YOq8lRY1DWESOZD/photos/7c/74/53498b54ed8cdc76d900019e/upload_test_photo_original.jpg","small_240":"http://storage.cloud.appcelerator.com/X3Eaph9KUC6Z1Lga4YOq8lRY1DWESOZD/photos/7c/74/53498b54ed8cdc76d900019e/upload_test_photo_small_240.jpg","square_75":"http://storage.cloud.appcelerator.com/X3Eaph9KUC6Z1Lga4YOq8lRY1DWESOZD/photos/7c/74/53498b54ed8cdc76d900019e/upload_test_photo_square_75.jpg","thumb_100":"http://storage.cloud.appcelerator.com/X3Eaph9KUC6Z1Lga4YOq8lRY1DWESOZD/photos/7c/74/53498b54ed8cdc76d900019e/upload_test_photo_thumb_100.jpg"},"user":{"username":"test_user"}}' --user 436641f6e1someusertokenandthenthecolon: -H 'Content-Type: application/json' http://127.0.0.1:5000/photos'
 
photos_schema = {
    "content_type": {
        "type": "string"
    },
    "created_at": {
        "type": "string"
    },
    "custom_fields": {
        "type": "dict",
        "schema": {
            "coordinates": {
                "type": "list",
                "schema": {
                    "type": "list",
                    "schema": {
                        "type": "float"
                    }
                }
            },
            "name_en": {
                "type": "string"
            },
            "name_ru": {
                "type": "string"
            }
        }
    },
    "exif": {
        "type": "dict",
        "schema": {
            "create_date": {
                "type": "string",
                "required": False
            },
            "width": {
                "type": "integer",
                "required": False
            },
            "height": {
                "type": "integer",
                "required": False
            },
            "make": {
                "type": "string",
                "required": False
            },
            "model": {
                "type": "string",
                "required": False
            },
            "shutter_speed": {
                "type": "string",
                "required": False
            }
        },
        "required": False
    },
    "filename": {
        "type": "string"
    },
    "id": {
        "type": "string",
        "required": False
    },
    "md5": {
        "type": "string",
        "required": False
    },
    "processed": {
        "type": "boolean"
    },
    "size": {
        "type": "integer"
    },
    "updated_at": {
        "type": "string"
    },
     "image": {
        "type": "media",
        "default": ""
    },
    "urls": {
        "type": "dict",
        "schema": {
            "large_1024": {
                "type": "string",
                "required": False
            },
            "medium_640": {
                "type": "string",
                "required": False
            },
            "medium_500": {
                "type": "string",
                "required": False
            },
            "small_240": {
                "type": "string",
                "required": False
            },
            "thumb_100": {
                "type": "string",
                "required": False
            },
            "square_75": {
                "type": "string",
                "required": False
            },
            "original": {
                "type": "string",
                "required": False
            }
        },
        "required": False
    },
    "user": {
        "type": "dict",
        "schema": {
            "username" : {
                "type": "string"
            }
        }
    }
}

eve_settings = {
    'SERVER_NAME': SERVER_NAME,
    'URL_PROTOCOL': 'http',
    'DOMAIN': {
        'photos': {
            'schema': photos_schema,
       },
    },
    'MONGO_DBNAME': 'raduga',
    'RESOURCE_METHODS': ['GET', 'POST'],
    'ITEM_METHODS': ['GET', 'PATCH'],
    'PUBLIC_METHODS': ['GET']
}

def write_photo_versions(id):
    def bounds(width):
        """
        The photos are viewed primarily in a scroll, on portrait devices.
        
        If the device is 240px wide, both landscape and portrait pictures will have a width of 240px
        The maximum height is then calculated given that 9:16 is probably the tallest format.
        """
        
        return (width, math.ceil(( width / 9.0 ) * 16))
    
    logger.debug("writing newly uploaded photo %s to disk" % str(id))
    photo = app.data.driver.db.photos.find_one(ObjectId(id))
    os.mkdir(os.path.join(PHOTO_FOLDER, id))
    
    im = Image.open(app.media.get(photo['image']))
    im.save(os.path.join(PHOTO_FOLDER, id, photo['filename']))
    
    basename, extension = os.path.splitext(photo['filename'])
    
    update = {"urls": {}}
    
    logger.debug("writing thumbnails of %s to disk" % str(id))
    for size, slug in [(240, "small_240"), (500, "medium_500"), (640, "medium_640"), (1024, "large_1024")]:
        im_small = im.copy()
        im_small.thumbnail(bounds(size), Image.ANTIALIAS)
        filename = "%s_%s%s" % (basename, slug, extension)
        im_small.save(os.path.join(PHOTO_FOLDER, id, filename ))
        
        update['urls'][slug] = 'http://' + SERVER_NAME + '/static/photos/' + id + '/' + filename
    
    # set the `url` fields for this photo in the database, so the app can display the photo
    app.data.driver.db.photos.update({"id": id}, { "$set": update})
    
def after_update_photos(request, payload):
    write_photo_versions(request.form['id'])

app = Eve(settings=eve_settings, auth=SimpleTokenAuth, static_folder=STATIC_FOLDER)

app.on_post_PATCH_photos += after_update_photos

if __name__ == '__main__':
    app.run(debug=True)

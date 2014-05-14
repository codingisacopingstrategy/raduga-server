import sys

from eve import Eve
from eve.auth import TokenAuth

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
        }
    },
    "filename": {
        "type": "string"
    },
    "id": {
        "type": "string",
        "required": False
    },
    "md5": {
        "type": "string"
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
        }
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
    'SERVER_NAME' : 'vps40616.public.cloudvps.com',
    'DOMAIN': {
        'photos': {
            'schema': photos_schema,
       },
    },
    'MONGO_DBNAME': 'photos',
    'RESOURCE_METHODS': ['GET', 'POST'],
    'PUBLIC_METHODS': ['GET']
}

if sys.platform == "darwin":
    eve_settings['SERVER_NAME'] = '127.0.0.1:5000'

app = Eve(settings=eve_settings, auth=SimpleTokenAuth)

if __name__ == '__main__':
    app.run(debug=True)

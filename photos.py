from eve import Eve
import sys


eve_settings = {
    'SERVER_NAME' : 'vps40616.public.cloudvps.com',
    'DOMAIN': {
        'photos': {},
    },
    'MONGO_DBNAME': 'photos'
}

if sys.platform == "darwin":
    settings['SERVER_NAME'] = '127.0.0.1:5000'

app = Eve(settings=eve_settings)

if __name__ == '__main__':
    app.run()

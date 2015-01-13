Raduga: server side components
==============================

Read online: <http://github.com/codingisacopingstrategy/raduga-server>

These are the serverside components for the Raduga app, the app that predicts rainbows over Russia.

If you want to follow along with the explanations, it is good to create a file with local settings (if it is not yet created). From the terminal, in the folder where you’ve downloaded/cloned raduga-server, run:

    [ ! -f local_settings.py ] &&  cp local_settings.py.example local_settings.py

Raduga-server consists of four parts.

### 1. A service to fetch meteorological data, and predict rainbows. 

This is written as a collection of Python scripts, that output JSON files. They are collected in the script [`predict.sh`][a1].

In general, by running this script every three hours the predictions should stay up to date. One can achieve this by making the script part of a [cronjob][a2].

For a description of how the rainbow prediction works, see: ‘[The rainbow algorithm][rainbow]’

When the scripts run, they log output into a MongoDB database to track progress. This is log is available through a web interface (#3). If you want to see the output of the various scripts directly into the terminal as you test them, run the following command:

    echo "DEBUG = True" >> local_settings.py

### 2. A service to send alerts to users

After the rainbows have been predicted, the file `alerts.py` serves to send push messages to users.

To keep track of the users and to provide authentication, we use Appcelerator Cloud Services. We also use this service to send the push messages. When we want to query the users, we first synch the local MongoDB database with the Appcelerator Cloud Services. This is the same service as used in the [Raduga Titanium mobile phone application][raduga].

To use the ACS, we will need to enter some account details into the `local_settings.py`. Please read the introduction of [`users.py`][a2b] for more info.

In general we will need to put the alerts.py in a cronjob, and run it every three hours, so that it is in synch with the rainbow predictions. A function from the alerts.py file is also called after a photo is uploaded, to alert a user of a spotted rainbow in its vicinity.


### 3. A web service that makes the predictions available to the mobile app

In [`app.py`][a3], we find a small python web application that provides the following web-addresses for the rainbow-predictions:

    /latest/elektro-l           redirects to the latest image of elektro l
    /latest/rainbows.json       redirects to the latest series of GEO-json features of rainbows
    /latest/clouds.json         redirects to the latest series of GEO-json features of clouds
    /latest/rainbow_cities.json redirects to a list of cities that are predicted to be in a rainbow zone
    /hq/                        consult a log of the prediction activities

The application uses the [Flask web framework][a4] and can be launched with `python app.py`. Consult the [Flask documentation][a5] on how to host this application on a web server.

### 4. A web service for rainbow spotting photos

In [photos.py][a6], we find a small API for retrieving and posting photos. It is intended for spotting rainbows through the Raduga mobile application.

    /photos/                    JSON feed of photos posted to Raduga

The API uses [Eve][a7], a Python REST API framework based on Flask. It requires Mongodb, and is otherwise hosted in the same way as the rainbow prediction web service.

Visit the url / do a GET request to get data about the most recent photos / spotted rainbows. For now, it is best to use the following URL:

    /photos/?where={"processed":true}&projection={"image":0} 

This way we only see photos whose thumbnails have been generated. Also, for the moment the photos are stored in the database as a string before being converted into thumbnails. `projection={"image":0}` makes sure we don’t download that whole string.

To upload a photo, use a POST request to `/photos/`. To update the data, do an UPDATE request to `/photos/idofthephoto/`. See the source code of the Raduga App for more info.

[a1]: https://github.com/codingisacopingstrategy/raduga-server/blob/master/predict.sh
[a2]: http://en.wikipedia.org/wiki/Cron "Cron - Wikipedia, the free encyclopedia"
[raduga]: https://github.com/codingisacopingstrategy/raduga
[a2b]: https://github.com/codingisacopingstrategy/raduga-server/blob/master/users.py
[a3]: https://github.com/codingisacopingstrategy/raduga-server/blob/master/app.py
[a4]: http://flask.pocoo.org/ "Welcome | Flask (A Python Microframework)"
[a5]: http://flask.pocoo.org/docs/0.10/deploying/ "Deployment Options &mdash; Flask Documentation (0.10)"
[a6]: https://github.com/codingisacopingstrategy/raduga-server/blob/master/photos.py
[a7]: http://python-eve.org/ "Python REST API Framework &mdash; Eve 0.5-dev documentation"
[rainbow]: https://github.com/codingisacopingstrategy/raduga-server/blob/master/RAINBOW-ALGORITHM.md

## Dependencies

The server-side components have been tested on Debian 7.

    sudo apt-get update
    # install system-wide dependencies (the jdk+maven is for grib2json):
    sudo apt-get install imagemagick potrace openjdk-7-jdk openjdk-7-jre maven python-imaging
    # install python dependencies
    sudo pip install -r requirements.txt

Then install MongoDB [following their instructions][d1] and install GRIB2JSON [from source][d2].

[d1]: http://docs.mongodb.org/manual/tutorial/install-mongodb-on-debian/ "Install MongoDB on Debian &mdash; MongoDB Manual 2.6.6"
[d2]: https://github.com/cambecc/grib2json

## Example crontab

    # Type `crontab -e` in the terminal to enter this crontab
    # It was not easy to set up cron in UTC time,
    # So this uses Brussels time
    # m h  dom mon dow   command

    55  5 * * * bash /path/to/raduga-server/predict.sh
    55  6 * * * python /path/to/raduga-server/alerts.py
    55  9 * * * python /path/to/raduga-server/alerts.py

    55 11 * * * bash /path/to/raduga-server/predict.sh
    55 12 * * * python /path/to/raduga-server/alerts.py
    55 15 * * * python /path/to/raduga-server/alerts.py

    55 17 * * * bash /path/to/raduga-server/predict.sh
    55 18 * * * python /path/to/raduga-server/alerts.py
    55 21 * * * python /path/to/raduga-server/alerts.py

    55 23 * * * bash /path/to/raduga-server/predict.sh
    55  0 * * * python /path/to/raduga-server/alerts.py
    55  3 * * * python /path/to/raduga-server/alerts.py

## License

    Copyright (C) 2014 Eric Schrijver and The Pink Pony Express

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.

Consult the source code: <http://github.com/codingisacopingstrategy/raduga-server>


"""
    Author: Will Smith
    (c) 2016 EventBoard

    This application should do the following:
        * Renew Access Token as needed.
        * Make EventBoard API calls
        * Check for events and populate as needed

    Large parts of this are used from FLASKR example app
    Flaskr functions are (c) 2015 by Armin Ronacher and Contributors
"""

import time
import requests
from datetime import datetime
from sqlite3 import dbapi2 as sqlite3
from flask import Flask, request, g

# Please change these variables to match your environment
DATABASE_LOCATION = ''  # Path to the DB file, without DB file name
DATABASE_NAME = 'eb_sensor_app.db'  # Name of DB File
ADHOC_EVENT_TITLE = "Quick Adhoc Reservation"  # String of meeting name
ADHOC_MEETING_DURATION = 1800  # Time in seconds of the meeting
# Do not change variables below here ##########################################
URLS = {
    'get': 'https://eventboard.io/api/v4/calendars/reservations/?room_id[]={}',
    'create':
        'https://eventboard.io/api/v4/calendars/reservations/?room_id={}',
    'edit': 'https://eventboard.io/api/v4/calendars/reservations/{}'
}


app = Flask(__name__)

app.config.update(dict(
            DATABASE=DATABASE_LOCATION + DATABASE_NAME,
            DEBUG=True,
            SECRET_KEY='',  # Change as would be appropriate
))
app.config.from_envvar('EB_SENSOR_APP_SETTINGS', silent=True)


# The following functions are about DB connection
def connect_db():
    """Connects to the DB"""
    rv = sqlite3.connect(app.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv


def init_db():
    """initializes the database."""
    db = get_db()
    with app.open_resource('schema.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()


def initdb_command():
    """Creates the DB tables"""
    init_db()
    print('Initialized the database.')


def get_db():
    """Opens db connection if there isn't one"""
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db


@app.teardown_appcontext
def close_db(error):
    """Closes DB connection at end of transaction"""
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()


# get_access_token keeps our OAUTH2.0 tokens up to date, but doesn't pound the
# EventBoard servers. This function will return the current access token to be
# used with EventBoard API requests.
def get_access_token():
    db = get_db()
    cursor = db.execute("SELECT * FROM credentials WHERE id = 1")
    creds = cursor.fetchone()
    updated_at = creds['update_datetime'] if creds['update_datetime'] else 0
    now = int(time.mktime(datetime.now().timetuple()))
    # Check access token for expiration. If it has expired, refresh it.
    if (now - updated_at) > (creds['expires_in'] - 60):
        # If we are here we need to update the access token
        data = {'client_id': creds['client_id'],
            'grant_type': 'refresh_token',
            'client_secret': creds['client_secret'],
            'refresh_token': creds['refresh_token']}
        r = requests.post('https://eventboard.io/oauth/token/', data=data)
        if r.status_code == 200:
            r_dict = r.json()
            db.execute('UPDATE credentials SET refresh_token=?,'
                       'access_token=?,expires_in=?,update_datetime=? '
                       'WHERE id=1',
                       [r_dict['refresh_token'], r_dict['access_token'],
                       r_dict['expires_in'], now])
            db.commit()
            return r_dict['access_token']
        else:
            return False
    else:
        # If we are here then the credentials are still valid
        return creds['access_token']


# The next functions deal with calendar events. These assume that the token
# type is bearer. TODO: change this to use the specified token type
# Get a list of calendar events for a specific room.
def get_calendar_events(room_id):
    headers = {'Authorization': 'Bearer {}'.format(get_access_token())}
    r = requests.get(URLS['get'].format(room_id), headers=headers)
    return r.json()


# Check available
def is_available(room_id):
    events = get_calendar_events(room_id)
    now = int(time.mktime(datetime.now().timetuple()))
    for event in events['reservations']:
        if int(event['starts_at']) <= now and int(event['ends_at']) >= now:
            return False
    return True


# Create calendar event
def create_calendar_event(room_id):
    headers = {'Authorization': 'Bearer {}'.format(get_access_token())}
    now = int(time.mktime(datetime.now().timetuple()))
    data = {
        "reservation": {
            "title": ADHOC_EVENT_TITLE,
            "starts_at": now,
            "ends_at": now + ADHOC_MEETING_DURATION
        }
    }
    r = requests.post(URLS['create'].format(room_id),
                      json=data, headers=headers)
    return r.json()


# Get and end current event
def get_and_end(room_id):
    events = get_calendar_events(room_id)
    now = int(time.mktime(datetime.now().timetuple()))
    headers = {'Authorization': 'Bearer {}'.format(get_access_token())}
    for event in events['reservations']:
        if int(event['starts_at']) <= now and int(event['ends_at']) >= now:
            # if we get here then we have an event and we can end it
            # This function assumes that there will only ever be one event that
            # meets the requirements of now. TODO parse all events and end
            # everything as needed.
            data = {
                "reservations": {
                    "ends_at": now
                }
            }
            r = requests.patch(URLS['edit'].format(event['id']),
                               json=data, headers=headers)
            return r.json()


# The following are the routes so that we can make HTTP requests
@app.route('/occupied', methods=['GET'])
def occupied():
    room_id = request.args.get('room_id')
    if is_available(room_id):
        response = create_calendar_event(room_id)
        return 'Request received, room booked with ID {}'\
            .format(response['reservation']['id'])
    else:
        return 'Request received, room already booked.'


@app.route('/empty', methods=['GET'])
def empty():
    room_id = request.args.get('room_id')
    get_and_end(room_id)
    return 'Request received'

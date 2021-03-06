# Project 2 - GeoTweet
# 
# @Author Jeffery Brown (daddyjab)
# @Date 3/27/19
# @File app.py


# import necessary libraries
import os
from flask import Flask, render_template, jsonify, request, redirect

# Import Flask_CORS extension to enable Cross Origin Resource Sharing (CORS)
# when deployed on Heroku
from flask_cors import CORS

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

# Enable Tracking of Flask-SQLAlchemy events for now (probably not needed)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

# Provide cross origin resource sharing
CORS(app)

#################################################
# Database Setup
#################################################

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql.expression import func

#Probably don't need these from SQLAlchemy: asc, desc, between, distinct, func, null, nullsfirst, nullslast, or_, and_, not_

# Local DB path for SQLite - default
db_path_flask_app = "sqlite:///data/twitter_trends.db"

# Local DB path for PostgreSQL - use only if login/password populated
try:
    # PostgreSQL Database Login/Password  
    # -- only needed if using a local PostgresSQL instance (vs. SQLite)
    from api_config import (postgres_geotweetapp_login, postgres_geotweetapp_password)

    # If the login and password is populated
    if (postgres_geotweetapp_login is not None) and (postgres_geotweetapp_password is not None):
        db_path_flask_app = f"postgresql://{postgres_geotweetapp_login}:{postgres_geotweetapp_password}@localhost/twitter_trends"
        print("Note: PostgreSQL database login/password is populated")

# If the api_config file is not available, then all we can do is flag an error
except ImportError:
    print("Note: PostgreSQL database login/password is *not* populated")

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', '') or db_path_flask_app

# Flask-SQLAlchemy database
db = SQLAlchemy(app)

# Import the schema for the Location and Trend tables needed for
# 'twitter_trends.sqlite' database tables 'locations' and 'trends'
from .models import (Location, Trend)

# Import database management functions needed# to update the
# 'twitter_trends.sqlite' database tables 'locations' and 'trends'
from .db_management import (
    api_calls_remaining, api_time_before_reset,
    update_db_locations_table, update_db_trends_table
    )

#********************************************************************************
# Default route - display the main page
# NOTE: Flask expects rendered templates to be in the ./templates folder
@app.route("/")
def home():
    return render_template("index.html")

#********************************************************************************
# Return information relevant to update
# of the 'locations' and 'trends' database tables
@app.route("/update")
def update_info():
    # Obtain remaining number of API calls for trends/place
    api_calls_remaining_place = api_calls_remaining( "place")

    # Obtain time before rate limits are reset for trends/available
    api_time_before_reset_place = api_time_before_reset( "place")

    # Obtain remaining number of API calls for trends/place
    api_calls_remaining_available = api_calls_remaining( "available")

    # Obtain time before rate limits are reset for trends/available
    api_time_before_reset_available = api_time_before_reset( "available")

    # Count the number of locations in the 'locations' table
    n_locations = db.session.query(Location).count()

    # Count the number of total trends in the 'trends' table
    n_trends = db.session.query(Trend).count()

    # Provide the average number of Twitter Trends provided per location
    # Use try/except to catch divide by zero
    try:
        n_trends_per_location_avg = n_trends / n_locations
    except ZeroDivisionError:
        n_trends_per_location_avg = None

    api_info = {
        'api_calls_remaining_place': api_calls_remaining_place,
        'api_time_before_reset_place': api_time_before_reset_place,
        'api_calls_remaining_available': api_calls_remaining_available,
        'api_time_before_reset_available': api_time_before_reset_available,
        'n_locations': n_locations,
        'n_trends': n_trends,
        'n_trends_per_location_avg' : n_trends_per_location_avg
    }

    return jsonify(api_info)

#********************************************************************************
# Update the 'locations' table via API calls
# Note: Typically requires less than 1 minute
@app.route("/update/locations")
def update_locations_table():
    # Update the locations table through API calls
    n_locations = update_db_locations_table()

    api_info = {
        'n_locations': n_locations
    }

    return jsonify(api_info)

#********************************************************************************
# Update the 'trends' table via API calls
# Note: Typically requires less than 1 minute if no rate limits
#       But require up to 15 minutes if rate limits are in effect
@app.route("/update/trends")
def update_trends_table():
    # Update the trends table through API calls
    n_location_trends = update_db_trends_table()

    api_info = {
        'n_location_trends': n_location_trends
    }

    return jsonify(api_info)


#********************************************************************************
# Return a list of all locations with Twitter Top Trend info
@app.route("/locations")
def get_all_locations():
    results = db.session.query(Location).all()

    loc_list = []
    for r in results:
        loc_info = {
            'woeid': r.woeid,
            'latitude': r.latitude,
            'longitude': r.longitude,
            'name_full': r.name_full,
            'name_only': r.name_only,
            'name_woe': r.name_woe,
            'county_name': r.county_name,
            'county_name_only': r.county_name_only,
            'county_woeid': r.county_woeid,
            'state_name': r.state_name,
            'state_name_only': r.state_name_only,
            'state_woeid': r.state_woeid,
            'country_name': r.country_name,
            'country_name_only': r.country_name_only,
            'country_woeid': r.country_woeid,
            'place_type': r.place_type,
            'timezone': r.timezone,
            'twitter_type': r.twitter_type,
            'twitter_country': r.twitter_country,
            'tritter_country_code': r.tritter_country_code,
            'twitter_name': r.twitter_name,
            'twitter_parentid': r.twitter_parentid
        }

        # loc_info = {
        #     'woeid': r.Location.woeid,
        #     'latitude': r.Location.latitude,
        #     'longitude': r.Location.longitude,
        #     'name_full': r.Location.name_full,
        #     'name_only': r.Location.name_only,
        #     'name_woe': r.Location.name_woe,
        #     'county_name': r.Location.county_name,
        #     'county_name_only': r.Location.county_name_only,
        #     'county_woeid': r.Location.county_woeid,
        #     'state_name': r.Location.state_name,
        #     'state_name_only': r.Location.state_name_only,
        #     'state_woeid': r.Location.state_woeid,
        #     'country_name': r.Location.country_name,
        #     'country_name_only': r.Location.country_name_only,
        #     'country_woeid': r.Location.country_woeid,
        #     'place_type': r.Location.place_type,
        #     'timezone': r.Location.timezone,
        #     'twitter_type': r.Location.twitter_type,
        #     'twitter_country': r.Location.twitter_country,
        #     'tritter_country_code': r.Location.tritter_country_code,
        #     'twitter_parentid': r.Location.twitter_parentid,

        #     'twitter_as_of': r.Trend.twitter_as_of,
        #     'twitter_created_at': r.Trend.twitter_created_at,
        #     'twitter_name': r.Trend.twitter_name,
        #     'twitter_tweet_name': r.Trend.twitter_tweet_name,
        #     'twitter_tweet_promoted_content': r.Trend.twitter_tweet_promoted_content,
        #     'twitter_tweet_query': r.Trend.twitter_tweet_query,
        #     'twitter_tweet_url': r.Trend.twitter_tweet_url,
        #     'twitter_tweet_volume': r.Trend.twitter_tweet_volume
        # }

        loc_list.append(loc_info)

    return jsonify(loc_list)

#********************************************************************************
# Return a list of one location  with Twitter Top Trend info with teh specified WOEID
@app.route("/locations/<a_woeid>")
def get_info_for_location(a_woeid):
    results = db.session.query(Location) \
                        .filter(Location.woeid == a_woeid) \
                        .all()
    loc_list = []
    for r in results:
        loc_info = {
            'woeid': r.woeid,
            'latitude': r.latitude,
            'longitude': r.longitude,
            'name_full': r.name_full,
            'name_only': r.name_only,
            'name_woe': r.name_woe,
            'county_name': r.county_name,
            'county_name_only': r.county_name_only,
            'county_woeid': r.county_woeid,
            'state_name': r.state_name,
            'state_name_only': r.state_name_only,
            'state_woeid': r.state_woeid,
            'country_name': r.country_name,
            'country_name_only': r.country_name_only,
            'country_woeid': r.country_woeid,
            'place_type': r.place_type,
            'timezone': r.timezone,
            'twitter_type': r.twitter_type,
            'twitter_country': r.twitter_country,
            'tritter_country_code': r.tritter_country_code,
            'twitter_name': r.twitter_name,
            'twitter_parentid': r.twitter_parentid
        }

        loc_list.append(loc_info)

    return jsonify(loc_list)


#********************************************************************************
# Return a list of all locations that have the specified tweet in its top trends
# and then sort the results by tweet volume in descending order (with NULLs last)
@app.route("/locations/tweet/<a_tweet>")
def get_locations_with_tweet(a_tweet):
    results = db.session.query(Trend, Location).join(Location) \
                        .filter(Trend.twitter_tweet_name == a_tweet ) \
                        .order_by( Trend.twitter_tweet_volume.desc().nullslast() ).all()

    loc_list = []
    for r in results:
        #print(f"Trend Information for {r.Trend.woeid} {r.Location.name_full}: {r.Trend.twitter_tweet_name} {r.Trend.twitter_tweet_volume}")
        loc_info = {
            'woeid': r.Location.woeid,
            'latitude': r.Location.latitude,
            'longitude': r.Location.longitude,
            'name_full': r.Location.name_full,
            'name_only': r.Location.name_only,
            'name_woe': r.Location.name_woe,
            'county_name': r.Location.county_name,
            'county_name_only': r.Location.county_name_only,
            'county_woeid': r.Location.county_woeid,
            'state_name': r.Location.state_name,
            'state_name_only': r.Location.state_name_only,
            'state_woeid': r.Location.state_woeid,
            'country_name': r.Location.country_name,
            'country_name_only': r.Location.country_name_only,
            'country_woeid': r.Location.country_woeid,
            'place_type': r.Location.place_type,
            'timezone': r.Location.timezone,
            'twitter_type': r.Location.twitter_type,
            'twitter_country': r.Location.twitter_country,
            'tritter_country_code': r.Location.tritter_country_code,
            'twitter_parentid': r.Location.twitter_parentid,

            'twitter_as_of': r.Trend.twitter_as_of,
            'twitter_created_at': r.Trend.twitter_created_at,
            'twitter_name': r.Trend.twitter_name,
            'twitter_tweet_name': r.Trend.twitter_tweet_name,
            'twitter_tweet_promoted_content': r.Trend.twitter_tweet_promoted_content,
            'twitter_tweet_query': r.Trend.twitter_tweet_query,
            'twitter_tweet_url': r.Trend.twitter_tweet_url,
            'twitter_tweet_volume': r.Trend.twitter_tweet_volume
        }

        loc_list.append(loc_info)

    return jsonify(loc_list)


#********************************************************************************
# Return the full list of all trends with Twitter Top Trend info
@app.route("/trends")
def get_all_trends():
    results = db.session.query(Trend).all()

    trend_list = []
    for r in results:
        trend_info = {
            'woeid': r.woeid,
            'twitter_as_of': r.twitter_as_of,
            'twitter_created_at': r.twitter_created_at,
            'twitter_name': r.twitter_name,
            'twitter_tweet_name': r.twitter_tweet_name,
            'twitter_tweet_promoted_content': r.twitter_tweet_promoted_content,
            'twitter_tweet_query': r.twitter_tweet_query,
            'twitter_tweet_url': r.twitter_tweet_url,
            'twitter_tweet_volume': r.twitter_tweet_volume
        }

        trend_list.append(trend_info)

    return jsonify(trend_list)

#********************************************************************************
# Return the full list of Twitter Top Trends for a specific location
# and then sort the results by tweet volume in descending order (with NULLs last)
@app.route("/trends/<a_woeid>")
def get_trends_for_location(a_woeid):
    results = db.session.query(Trend).filter(Trend.woeid == a_woeid) \
                        .order_by(Trend.twitter_tweet_volume.desc().nullslast() ) \
                        .all()

    trend_list = []
    for r in results:
        trend_info = {
            'woeid': r.woeid,
            'twitter_as_of': r.twitter_as_of,
            'twitter_created_at': r.twitter_created_at,
            'twitter_name': r.twitter_name,
            'twitter_tweet_name': r.twitter_tweet_name,
            'twitter_tweet_promoted_content': r.twitter_tweet_promoted_content,
            'twitter_tweet_query': r.twitter_tweet_query,
            'twitter_tweet_url': r.twitter_tweet_url,
            'twitter_tweet_volume': r.twitter_tweet_volume
        }

        trend_list.append(trend_info)

    return jsonify(trend_list)

#********************************************************************************
# Return the top 5 list of Twitter Top Trends for a specific location
# and then sort the results by tweet volume in descending order (with NULLs last)
@app.route("/trends/top/<a_woeid>")
def get_top_trends_for_location(a_woeid):
    results = db.session.query(Trend) \
                        .filter(Trend.woeid == a_woeid) \
                        .order_by(Trend.twitter_tweet_volume.desc().nullslast() ) \
                        .limit(10).all()

    trend_list = []
    for r in results:
        trend_info = {
            'woeid': r.woeid,
            'twitter_as_of': r.twitter_as_of,
            'twitter_created_at': r.twitter_created_at,
            'twitter_name': r.twitter_name,
            'twitter_tweet_name': r.twitter_tweet_name,
            'twitter_tweet_promoted_content': r.twitter_tweet_promoted_content,
            'twitter_tweet_query': r.twitter_tweet_query,
            'twitter_tweet_url': r.twitter_tweet_url,
            'twitter_tweet_volume': r.twitter_tweet_volume
        }

        trend_list.append(trend_info)

    return jsonify(trend_list)


if __name__ == "__main__":
    app.run()


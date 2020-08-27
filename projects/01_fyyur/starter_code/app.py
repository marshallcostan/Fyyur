#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from babel import dates
from flask import Flask, render_template, request, Response, flash, redirect, url_for, abort, jsonify
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
import time
import sys
from datetime import datetime


#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)

migrate = Migrate(app, db)
# TODO: connect to a local postgresql database

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#


class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    genres = db.Column(db.ARRAY(db.String))
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    website = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean)
    seeking_description = db.Column(db.String(120))
    show = db.relationship('Show', passive_deletes=True, backref='Venue', lazy=True)


class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    website = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean)
    seeking_description = db.Column(db.String(120))
    show = db.relationship('Show', passive_deletes=True, backref='Artist', lazy=True)


class Show(db.Model):
    __tablename__ = 'Show'

    id = db.Column(db.Integer, primary_key=True)
    artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id', ondelete='CASCADE'))
    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id', ondelete='CASCADE'))
    start_time = db.Column(db.DateTime)

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#


def format_datetime(value, format='medium'):
    date = dateutil.parser.parse(value)
    if format == 'full':
        format="EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format="EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format)


app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
    return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
    areas = db.session.query(Venue.city, Venue.state).distinct(Venue.city, Venue.state)
    data = []
    for area in areas:
        areas = Venue.query.filter_by(state=area.state).filter_by(city=area.city).all()
        venue_data = []
        data.append({
            'city': area.city,
            'state': area.state,
            'venues': venue_data
            })
    for venue in areas:
        venue_data.append({
            'id': venue.id,
            'name': venue.name,
            'upcoming_shows_count': len(db.session.query(Show).filter(Show.start_time > datetime.now()).all())
            })
    return render_template('pages/venues.html', areas=data)


@app.route('/venues/search', methods=['POST'])
def search_venues():
    search_term = request.form.get('search_term')
    results = Venue.query.filter(Venue.name.ilike('%{}%'.format(search_term)))
    venue_list = list(results)
    response = {
        "count": len(venue_list),
        "data": venue_list
        }

    return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    venue = db.session.query(Venue).filter(Venue.id == venue_id)
    past_shows_result = db.session.query(Show).filter(Show.venue_id == venue_id).filter(
        Show.start_time < datetime.now()).all()
    upcoming_shows_result = db.session.query(Show).filter(Show.venue_id == venue_id).filter(
        Show.start_time > datetime.now()).all()
    for v in venue:
        past_shows = []
        upcoming_shows = []
        data = {
            'id': v.id,
            'name': v.name,
            'genres': v.genres,
            'address': v.address,
            'city': v.city,
            'state': v.state,
            'phone': v.phone,
            'website': v.website,
            'facebook_link': v.facebook_link,
            'seeking_talent': v.seeking_talent,
            'seeking_description': v.seeking_description,
            'image_link': v.image_link,
            'upcoming_shows_count': len(upcoming_shows_result),
            'past_shows_count': len(past_shows_result),
            'past_shows': past_shows,
            'upcoming_shows': upcoming_shows
        }
        for show in past_shows_result:
            past_shows.append({
                'artist_id': show.Artist.id,
                'artist_name': show.Artist.name,
                'artist_image_link': show.Artist.image_link,
                'start_time': show.start_time.strftime("%m-%d-%Y %H:%M:%S"),
            })
        for show in upcoming_shows_result:
            upcoming_shows.append({
                'artist_id': show.Artist.id,
                'artist_name': show.Artist.name,
                'artist_image_link': show.Artist.image_link,
                'start_time': show.start_time.strftime("%m-%d-%Y %H:%M:%S"),
            })
        return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------


@app.route('/venues/create', methods=['GET'])
def create_venue_form():
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)


@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    error = False
    try:
        name = request.form['name']
        city = request.form['city']
        state = request.form['state']
        address = request.form['address']
        phone = request.form['phone']
        genres = request.form.getlist('genres')
        if 'seeking_talent' in request.form:
            seeking_talent = True
        else:
            seeking_talent = False
        seeking_description = request.form['seeking_description']
        website = request.form['website']
        image_link = request.form['image_link']
        facebook_link = request.form['facebook_link']
        new_venue = Venue(name=name, city=city, state=state, address=address, phone=phone,
                          genres=genres, seeking_talent=seeking_talent, seeking_description=seeking_description,
                          website=website, image_link=image_link, facebook_link=facebook_link)
        db.session.add(new_venue)
        db.session.commit()
        flash('Venue ' + request.form['name'] + ' was successfully listed!')
    except():
        db.session.rollback()
        error = True
        flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
        print(sys.exc_info)
    finally:
        db.session.close()
    if error:
        abort(500)
    return render_template('pages/home.html')


@app.route('/venues/<int:venue_id>', methods=['POST'])
def delete_venue(venue_id):
    try:
        venue = Venue.query.filter_by(id=venue_id).first_or_404()
        current_session = db.object_session(venue)
        current_session.delete(venue)
        current_session.commit()
        flash('The venue has been removed together with all of its shows.')
        return render_template('pages/home.html')
    except ValueError:
        flash('It was not possible to delete this Venue')
    return redirect(url_for('venues'))


#  Artists
#  ----------------------------------------------------------------


@app.route('/artists')
def artists():
    artists = Artist.query.all()
    data = []
    for artist in artists:
        data.append({
            'id': artist.id,
            'name': artist.name})
    return render_template('pages/artists.html', artists=data)


@app.route('/artists/search', methods=['POST'])
def search_artists():
    search_term = request.form.get('search_term')
    results = Artist.query.filter(Artist.name.ilike('%{}%'.format(search_term)))
    artist_list = list(results)
    response = {
      "count": len(artist_list),
      "data": artist_list
    }
    return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    artist = db.session.query(Artist).filter(Artist.id == artist_id)
    past_shows_result = db.session.query(Show).filter(Show.artist_id == artist_id).filter(
      Show.start_time < datetime.now()).all()
    upcoming_shows_result = db.session.query(Show).filter(Show.artist_id == artist_id).filter(Show.start_time > datetime.now()).all()
    for a in artist:
        past_shows = []
        upcoming_shows = []
        data = {
            'id': a.id,
            'name': a.name,
            'genres': a.genres,
            'city': a.city,
            'state': a.state,
            'phone': a.phone,
            'website': a.website,
            'facebook_link': a.facebook_link,
            'seeking_venue': a.seeking_venue,
            'seeking_description': a.seeking_description,
            'image_link': a.image_link,
            'upcoming_shows_count': len(upcoming_shows_result),
            'past_shows_count': len(past_shows_result),
            'past_shows': past_shows,
            'upcoming_shows': upcoming_shows
        }
        for show in past_shows_result:
            past_shows.append({
                'venue_id': show.Venue.id,
                'venue_name': show.Venue.name,
                'venue_image_link': show.Venue.image_link,
                'start_time': show.start_time.strftime("%m-%d-%Y %H:%M:%S"),
            })
        for show in upcoming_shows_result:
            upcoming_shows.append({
                'venue_id': show.Venue.id,
                'venue_name': show.Venue.name,
                'venue_image_link': show.Venue.image_link,
                'start_time': show.start_time.strftime("%m-%d-%Y %H:%M:%S"),
            })

    return render_template('pages/show_artist.html', artist=data)


@app.route('/artist/<int:artist_id>', methods=['POST'])
def delete_artist(artist_id):
    try:
        artist = Artist.query.filter_by(id=artist_id).first_or_404()
        current_session = db.object_session(artist)
        current_session.delete(artist)
        current_session.commit()
        flash('The artist has been removed together with all of its shows.')
        return render_template('pages/home.html')
    except ValueError:
        flash('It was not possible to delete this artist')
    return redirect(url_for('artist'))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)


@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    error = False
    try:
        name = request.form['name']
        city = request.form['city']
        state = request.form['state']
        phone = request.form['phone']
        genres = request.form.getlist('genres')
        if 'seeking_venue' in request.form:
          seeking_venue = True
        else:
          seeking_venue = False
        seeking_description = request.form['seeking_description']
        website = request.form['website']
        image_link = request.form['image_link']
        facebook_link = request.form['facebook_link']
        new_artist = Artist(name=name, city=city, state=state, phone=phone,
                        genres=genres, seeking_venue=seeking_venue, seeking_description=seeking_description,
                        website=website, image_link=image_link, facebook_link=facebook_link)
        db.session.add(new_artist)
        db.session.commit()
        flash('Artist ' + request.form['name'] + ' was successfully listed!')
    except():
        db.session.rollback()
        error = True
        flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')
        print(sys.exc_info)
    finally:
        db.session.close()
    if error:
        abort(500)
    return render_template('pages/home.html')

#  Update Artist--------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    artist = Artist.query.get(artist_id)
    form = ArtistForm(obj=artist)
    return render_template('forms/edit_artist.html', form=form, artist=artist)


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    artist = Artist.query.get(artist_id)
    error = False
    try:
        artist.name = request.form['name']
        artist.city = request.form['city']
        artist.state = request.form['state']
        artist.phone = request.form['phone']
        artist.genres = request.form.getlist('genres')
        if 'seeking_venue' in request.form:
            artist.seeking_venue = True
        else:
            artist.seeking_venue = False
        artist.seeking_description = request.form['seeking_description']
        artist.website = request.form['website']
        artist.image_link = request.form['image_link']
        artist.facebook_link = request.form['facebook_link']
        updated_artist = Artist(name=artist.name, city=artist.city, state=artist.state,
                                phone=artist.phone,
                                genres=artist.genres, seeking_venue=artist.seeking_venue,
                                seeking_description=artist.seeking_description, website=artist.website,
                                image_link=artist.image_link, facebook_link=artist.facebook_link)
        db.session.add(updated_artist)
        db.session.commit()
        flash('Artist ' + request.form['name'] + ' was successfully updated')
    except():
        db.session.rollback()
        error = True
        flash('An error occurred. Artist ' + request.form['name'] + ' could not be updated.')
        print(sys.exc_info)
    finally:
        db.session.close()
    if error:
        abort(500)
    return redirect(url_for('show_artist', artist_id=artist_id))

#  Update Venue--------------------------------------------------------

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    venue = Venue.query.get(venue_id)
    form = VenueForm(obj=venue)
    return render_template('forms/edit_venue.html', form=form, venue=venue)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    venue = Venue.query.get(venue_id)
    error = False
    try:
        venue.name = request.form['name']
        venue.city = request.form['city']
        venue.state = request.form['state']
        venue.address = request.form['address']
        venue.phone = request.form['phone']
        venue.genres = request.form.getlist('genres')
        if 'seeking_talent' in request.form:
            venue.seeking_talent = True
        else:
            venue.seeking_talent = False
        venue.seeking_description = request.form['seeking_description']
        venue.website = request.form['website']
        venue.image_link = request.form['image_link']
        venue.facebook_link = request.form['facebook_link']
        updated_venue = Venue(name=venue.name, city=venue.city, state=venue.state, address=venue.address, phone=venue.phone,
                        genres=venue.genres, seeking_talent=venue.seeking_talent, seeking_description=venue.seeking_description,
                        website=venue.website, image_link=venue.image_link, facebook_link=venue.facebook_link)
        db.session.add(updated_venue)
        db.session.commit()
        flash('Venue ' + request.form['name'] + ' was successfully updated')
    except():
        db.session.rollback()
        error = True
        flash('An error occurred. Venue ' + request.form['name'] + ' could not be updated.')
        print(sys.exc_info)
    finally:
        db.session.close()
    if error:
        abort(500)
    return redirect(url_for('show_venue', venue_id=venue_id))

#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
    data = []
    shows = Show.query.order_by(Show.start_time.asc()).all()
    for show in shows:
        venue = Venue.query.filter_by(id=show.venue_id).first_or_404()
        artist = Artist.query.filter_by(id=show.artist_id).first_or_404()
        data.extend([{
            "venue_id": venue.id,
            "venue_name": venue.name,
            "artist_id": artist.id,
            "artist_name": artist.name,
            "artist_image_link": artist.image_link,
            "start_time": show.start_time.strftime("%m/%d/%Y, %H:%M")
            }])
    return render_template('pages/shows.html', shows=data)


@app.route('/shows/create')
def create_shows():
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)


@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    error = False
    try:
        artist_id = request.form['artist_id']
        venue_id = request.form['venue_id']
        start_time = request.form['start_time']
        new_show = Show(artist_id=artist_id, venue_id=venue_id, start_time=start_time,)
        db.session.add(new_show)
        db.session.commit()
        flash('Show was successfully listed!')
    except():
        db.session.rollback()
        error = True
        flash('An error occurred. Show could not be listed.')
        print(sys.exc_info)
    finally:
        db.session.close()
    if error:
        abort(500)
    return render_template('pages/home.html')


@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404


@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''

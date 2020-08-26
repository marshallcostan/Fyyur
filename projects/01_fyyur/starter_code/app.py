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

    # TODO: implement any missing fields, as a database migration using Flask-Migrate

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
    artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'))
    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'))
    start_time = db.Column(db.DateTime)





    # TODO: implement any missing fields, as a database migration using Flask-Migrate

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.

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
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
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
    print(data)
   return render_template('pages/venues.html', areas=data)

  #
  #
  # data=[{
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "venues": [{
  #     "id": 1,
  #     "name": "The Musical Hop",
  #     "num_upcoming_shows": 0,
  #   }, {
  #     "id": 3,
  #     "name": "Park Square Live Music & Coffee",
  #     "num_upcoming_shows": 1,
  #   }]
  # }, {
  #   "city": "New York",
  #   "state": "NY",
  #   "venues": [{
  #     "id": 2,
  #     "name": "The Dueling Pianos Bar",
  #     "num_upcoming_shows": 0,
  #   }]
  # }]
  #
  # return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on ARTISTS!? with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"

  search_term = request.form.get('search_term')
  results = Venue.query.filter(Venue.name.ilike('%{}%'.format(search_term)))
  venue_list = list(results)
  response = {
    "count": len(venue_list),
    "data": venue_list
  }

  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

  # response={
  #   "count": 1,
  #   "data": [{
  #     "id": 2,
  #     "name": "The Dueling Pianos Bar",
  #     "num_upcoming_shows": 0,
  #   }]
  # }


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    # shows the venue page with the given venue_id
    # TODO: replace with real venue data from the venues table, using venue_id
    venue = db.session.query(Venue).filter(Venue.id == venue_id)
    # shows = db.session.query(Show).filter(Show.venue_id == venue_id).all()
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

  # TODO: insert form data as a new Venue record in the db, instead
  # # TODO: modify data to be the data object returned from db insertion
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
        image_link = request.form['image_link']
        facebook_link = request.form['facebook_link']
        new_venue = Venue(name=name, city=city, state=state, address=address, phone=phone,
                          genres=genres, seeking_talent=seeking_talent, seeking_description=seeking_description,image_link=image_link, facebook_link=facebook_link)
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
#   # TODO: replace with real data returned from querying the database
      artists = Artist.query.all()
      data = []
      for artist in artists:
          data.append({
              'id': artist.id,
              'name': artist.name})

      return render_template('pages/artists.html', artists=data)
  # data=[{
  #   "id": 4,
  #   "name": "Guns N Petals",
  # }, {
  #   "id": 5,
  #   "name": "Matt Quevedo",
  # }, {
  #   "id": 6,
  #   "name": "The Wild Sax Band",
  # }]
  #       return render_template('pages/artists.html', artists=data)


@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  search_term = request.form.get('search_term')
  results = Artist.query.filter(Artist.name.ilike('%{}%'.format(search_term)))
  artist_list = list(results)
  response = {
      "count": len(artist_list),
      "data": artist_list
  }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))
  # response={
  #   "count": 1,
  #   "data": [{
  #     "id": 4,
  #     "name": "Guns N Petals",
  #     "num_upcoming_shows": 0,
  #   }]
  # }
  # return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
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
      print(data)
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


#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    artist = Artist.query.get(artist_id)
    form = ArtistForm(obj=artist)
  # TODO: populate form with fields from artist with ID <artist_id>
    return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  users.update().values({"name": "some new name"})




  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    venue = Venue.query.get(venue_id)
    form = VenueForm(obj=venue)
  # TODO: populate form with values from venue with ID <venue_id>
    return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
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
      venue.image_link = request.form['image_link']
      venue.facebook_link = request.form['facebook_link']
      updated_venue = Venue(name=venue.name, city=venue.city, state=venue.state, address=venue.address, phone=venue.phone,
                        genres=venue.genres, seeking_talent=venue.seeking_talent, seeking_description=venue.seeking_description,
                        image_link=venue.image_link, facebook_link=venue.facebook_link)
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

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # # called upon submitting the new artist listing form
  # # TODO: insert form data as a new Venue record in the db, instead
  # # TODO: modify data to be the data object returned from db insertion
  #
  # # on successful db insert, flash success
  # flash('Artist ' + request.form['name'] + ' was successfully listed!')
  # # TODO: on unsuccessful db insert, flash an error instead.
  # # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  # return render_template('pages/home.html')
  users.update().values({"name": "some new name"})

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
      image_link = request.form['image_link']
      facebook_link = request.form['facebook_link']
      new_artist = Artist(name=name, city=city, state=state, phone=phone,
                        genres=genres, seeking_venue=seeking_venue, seeking_description=seeking_description,
                        image_link=image_link, facebook_link=facebook_link)
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


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  # #       num_shows should be aggregated based on number of upcoming shows per venue.
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


  # data=[{
  #   "venue_id": 1,
  #   "venue_name": "The Musical Hop",
  #   "artist_id": 4,
  #   "artist_name": "Guns N Petals",
  #   "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
  #   "start_time": "2019-05-21T21:30:00.000Z"
  # }, {
  #   "venue_id": 3,
  #   "venue_name": "Park Square Live Music & Coffee",
  #   "artist_id": 5,
  #   "artist_name": "Matt Quevedo",
  #   "artist_image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
  #   "start_time": "2019-06-15T23:00:00.000Z"
  # }, {
  #   "venue_id": 3,
  #   "venue_name": "Park Square Live Music & Coffee",
  #   "artist_id": 6,
  #   "artist_name": "The Wild Sax Band",
  #   "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #   "start_time": "2035-04-01T20:00:00.000Z"
  # }, {
  #   "venue_id": 3,
  #   "venue_name": "Park Square Live Music & Coffee",
  #   "artist_id": 6,
  #   "artist_name": "The Wild Sax Band",
  #   "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #   "start_time": "2035-04-08T20:00:00.000Z"
  # }, {
  #   "venue_id": 3,
  #   "venue_name": "Park Square Live Music & Coffee",
  #   "artist_id": 6,
  #   "artist_name": "The Wild Sax Band",
  #   "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #   "start_time": "2035-04-15T20:00:00.000Z"
  # }]
  # return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead

  # on successful db insert, flash success
  flash('Show was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
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










@app.cli.command("bootstrap")
def bootstrap_data():
    db.session.add(Venue(name="The Musical Hop",
                         genres=["Jazz", "Reggae", "Swing", "Classical", "Folk"],
                         address="1015 Folsom Street",
                         city="San Francisco",
                         state="CA",
                         phone="123-123-1234",
                         website="https://www.themusicalhop.com",
                         facebook_link="https://www.facebook.com/TheMusicalHop",
                         seeking_talent=True,
                         seeking_description="We are on the lookout for a local artist to play every two weeks. Please call us.",
                         image_link="https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60"))
    # past_shows= [{
    #   "artist_id": 4,
    #   "artist_name": "Guns N Petals",
    #   "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
    #   "start_time": "2019-05-21T21:30:00.000Z"))
    db.session.add(Venue(
        name="The Dueling Pianos Bar",
        genres=["Classical", "R&B", "Hip-Hop"],
        address="335 Delancey Street",
        city="New York",
        state="NY",
        phone="914-003-1132",
        website="https://www.theduelingpianos.com",
        facebook_link="https://www.facebook.com/theduelingpianos",
        seeking_talent=False,
        image_link="https://images.unsplash.com/photo-1497032205916-ac775f0649ae?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=750&q=80"))
    # past_shows=[],
    # upcoming_shows= [],
    # "past_shows_count": 0,
    # "upcoming_shows_count": 0,))
    db.session.add(Venue
                   (name="Park Square Live Music & Coffee",
                    genres=["Rock n Roll", "Jazz", "Classical", "Folk"],
                    address="34 Whiskey Moore Ave",
                    city="San Francisco",
                    state="CA",
                    phone="415-000-1234",
                    website="https://www.parksquarelivemusicandcoffee.com",
                    facebook_link="https://www.facebook.com/ParkSquareLiveMusicAndCoffee",
                    seeking_talent=False,
                    image_link="https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
                    ))
    db.session.add(Venue(
        name="Rock on Cafe",
        genres=["Rock n Roll", "Jazz", "Classical", "Folk"],
        address="1213 5th Avenue",
        city="New York",
        state="NY",
        phone="800-900-1234",
        website="https://www.parksquarelivemusicandcoffee.com",
        facebook_link="https://www.facebook.com/ParkSquareLiveMusicAndCoffee",
        seeking_talent=False,
        image_link="https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80", ))
    db.session.commit()


@app.cli.command("bootstrap-artist")
def bootstrap_data():
    db.session.add(Artist(
        name="Guns N Petals",
        genres=["Rock n Roll"],
        city="San Francisco",
        state="CA",
        phone="326-123-5000",
        website="https://www.gunsnpetalsband.com",
        facebook_link="https://www.facebook.com/GunsNPetals",
        seeking_venue=True,
        seeking_description="Looking for shows to perform at in the San Francisco Bay Area!",
        image_link="https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80"))
    db.session.add(Artist(
        name="Matt Quevedo",
        genres=["Jazz"],
        city="New York",
        state="NY",
        phone="300-400-5000",
        facebook_link="https://www.facebook.com/mattquevedo923251523",
        seeking_venue=False,
        image_link="https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80"))
    db.session.add(Artist(
        name="The Wild Sax Band",
        genres=["Jazz", "Classical"],
        city="San Francisco",
        state="CA",
        phone="432-325-5432",
        seeking_venue=False,
        image_link="https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80"))
    db.session.commit()


@app.cli.command("bootstrap-show")
def bootstrap_data():
    db.session.add(Show(
        venue_id=1,
        artist_id=1,
        start_time= "2019-05-21T21:30:00.000Z"))
    db.session.add(Show(
        venue_id=3,
        artist_id=5,
        start_time="2019-06-15T23:00:00.000Z"))
    db.session.add(Show(
        venue_id=3,
        artist_id=6,
        start_time= "2035-04-01T20:00:00.000Z"))
    db.session.add(Show(
        venue_id=3,
        artist_id=6,
        start_time="2035-04-08T20:00:00.000Z"))
    db.session.add(Show(
        venue_id=3,
        artist_id=6,
        start_time="2035-04-15T20:00:00.000Z"))
    db.session.commit()



  # data=[{
  #   "venue_id": 1,
  #   "venue_name": "The Musical Hop",
  #   "artist_id": 4,
  #   "artist_name": "Guns N Petals",
  #   "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
  #   "start_time": "2019-05-21T21:30:00.000Z"
  # }, {
  #   "venue_id": 3,
  #   "venue_name": "Park Square Live Music & Coffee",
  #   "artist_id": 5,
  #   "artist_name": "Matt Quevedo",
  #   "artist_image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
  #   "start_time": "2019-06-15T23:00:00.000Z"
  # }, {
  #   "venue_id": 3,
  #   "venue_name": "Park Square Live Music & Coffee",
  #   "artist_id": 6,
  #   "artist_name": "The Wild Sax Band",
  #   "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #   "start_time": "2035-04-01T20:00:00.000Z"
  # }, {
  #   "venue_id": 3,
  #   "venue_name": "Park Square Live Music & Coffee",
  #   "artist_id": 6,
  #   "artist_name": "The Wild Sax Band",
  #   "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #   "start_time": "2035-04-08T20:00:00.000Z"
  # }, {
  #   "venue_id": 3,
  #   "venue_name": "Park Square Live Music & Coffee",
  #   "artist_id": 6,
  #   "artist_name": "The Wild Sax Band",
  #   "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #   "start_time": "2035-04-15T20:00:00.000Z"
  # }]
  # return render_template('pages/shows.html', shows=data)

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

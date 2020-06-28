# Name: Thuc Gia Nguyen
# Email: thucngyyen@gmail.com
# File header: this is a python file to run back-end of the Fyyur project,
#details are explained in the README file

#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    genres = db.Column(db.ARRAY(db.String))
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    website = db.Column(db.String(200))
    facebook_link = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean)
    seeking_description = db.Column(db.String())
    image_link = db.Column(db.String(500))

class Shows(db.Model):
  __tablename__ = 'Shows'

  artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'), primary_key=True)
  venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), primary_key=True)
  start_time = db.Column(db.DateTime(), primary_key=True, nullable=True)
  
class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    genres = db.Column(db.ARRAY(db.String))
    address = db.Column(db.String(120))
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    website = db.Column(db.String(200))
    facebook_link = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean)
    seeking_description = db.Column(db.String())
    image_link = db.Column(db.String(500))
    #artists = db.relationship('Artist', secondary="shows", backref=db.backref('venues', lazy=True))

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

#Venue home page
@app.route('/venues')
def venues():
  
  areas = db.session.query(Venue.city, Venue.state).distinct()
  data=[]
  for area in areas:
    venue_area = Venue.query.filter_by(state=area.state).filter_by(city=area.city).all()
    venues = []
    for venue in venue_area:
      venues.append({
        'id': venue.id,
        'name': venue.name,
        'num_upcoming_shows': len(Shows.query.filter(Shows.start_time > datetime.now()).all())
      })
    data.append({
        'city': area.city,
        'state': area.state,
        'venues': venues
      })

  return render_template('pages/venues.html', areas=data)

# Venue search page
@app.route('/venues/search', methods=['POST'])
def search_venues():

  search_term = request.form.get('search_term', '')
  data = db.session.query(Venue).filter(Venue.name.ilike(f'%{search_term}%')).all()
  count = []

  for res in data:
    count.append({
      'id': res.id,
      'name': res.name,
      'num_upcoming_shows': len(Shows.query.filter(Shows.venue_id==res.id).filter(Shows.start_time > datetime.now()).all())
    })  
  response = {
    'count': len(data),
    'data': count
  }
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

# Individual Venue page
@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
 
  venue = Venue.query.get(venue_id)
  coming_filter = db.session.query(Shows).join(Artist).filter(Shows.venue_id==venue_id).filter(Shows.start_time > datetime.now()).all() 
  passed_filter = db.session.query(Shows).join(Artist).filter(Shows.venue_id==venue_id).filter(Shows.start_time <= datetime.now()).all()

  coming = []
  past = []

  for show in coming_filter:
    coming.append({
      'artist_id': show.artist_id,
      'artist_name': Artist.query.get(show.artist_id).name,
      'artist_image_link': Artist.query.get(show.artist_id).image_link,
      'start_time': show.start_time.strftime("%m/%d/%Y, %H:%M")
    })
  for show in passed_filter:
    past.append({
      'artist_id': show.artist_id,
      'artist_name': Artist.query.get(show.artist_id).name,
      'artist_image_link': Artist.query.get(show.artist_id).image_link,
      'start_time': show.start_time.strftime("%m/%d/%Y, %H:%M")
    })
  data = {
    'id': venue_id,
    'name': venue.name,
    'genres': venue.genres,
    'address': venue.address,
    'city': venue.city,
    'state': venue.state,
    'phone': venue.phone,
    'website': venue.website,
    'image_link': venue.image_link,
    'facebook_link': venue.facebook_link,
    'seeking_talent': venue.seeking_talent,
    'seeking_description': venue.seeking_description,
    'upcoming_shows': coming,
    'upcoming_shows.count': len(coming),
    'past_shows': past,
    'past_shows_count': len(past)
  }
  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

#GET method: take data from database to post on then website
@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

#POST method: retrieve data and save to database
@app.route('/venues/create', methods=['POST'])
def create_venue_submission():

  try:
    name = request.form.get('name')
    city = request.form.get('city')
    state = request.form.get('state')
    address = request.form.get('address')
    phone = request.form.get('phone')
    image_link = request.form.get('image_link')
    genres = request.form.getlist('genres')
    facebook_link = request.form.get('facebook_link')
    website = request.form.get('website')
    seeking_description = request.form.get('seeking_description')

    if request.form.get('seeking_talent') == 'Yes':
      seeking_talent = True
    else: 
      seeking_talent = False

    newVenue = Venue(name=name, city=city, state=state,address=address, phone=phone,
          image_link=image_link, genres=genres, facebook_link=facebook_link, website=website, 
          seeking_talent=seeking_talent, seeking_description=seeking_description)

    db.session.add(newVenue)
    db.session.commit()

    # on successful db insert, flash success
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
  except:
    db.session.rollback()
    flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
  finally:
    db.session.close()

  return render_template('pages/home.html')

#DELETE method
@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
 
  temp = Venue.query.get(venue_id).name
  try:
    Venue.query.filter_by(id=venue_id).delete()
    db.session.commit()
    flash('Venue ' + temp + ' was deleted!')
  except:
    db.session.rollback()
    flash('Something went wrong! Could not delete' + temp)
  finally:
    db.session.close()
  
  # BONUS CHALLENGE: done
  return render_template('pages/home.html')

#  Artists
#  ----------------------------------------------------------------

#Artist main page
@app.route('/artists')
def artists():

  data = Artist.query.all()

  return render_template('pages/artists.html', artists=data)

#Artist search
@app.route('/artists/search', methods=['POST'])
def search_artists():
  
  search_term = request.form.get('search_term', '')
  data = Artist.query.filter(Artist.name.ilike(f'%{search_term}%')).all()
  count = []

  for res in data:
    count.append({
      'id': res.id,
      'name': res.name,
      'num_upcomming_shows': len(Shows.query.filter(Shows.artist_id==res.id).filter(Shows.start_time > datetime.now()).all())
    })
  response = {
    'count': len(data),
    'data': count
  }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

# Individual artist page
@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
 
  artist = Artist.query.get(artist_id)
  coming_filter = db.session.query(Shows).join(Venue).filter(Shows.artist_id==artist_id).filter(Shows.start_time > datetime.now()).all()
  passed_filter = db.session.query(Shows).join(Venue).filter(Shows.artist_id==artist_id).filter(Shows.start_time <= datetime.now()).all()

  coming = []
  past = []

  for show in coming_filter:
    coming.append({
      'venue_id': show.venue_id,
      'venue_name': Venue.query.get(show.venue_id).name,
      'venue_image_link': Venue.query.get(show.venue_id).image_link,
      'start_time': show.start_time.strftime("%m/%d/%Y, %H:%M")
    })
  for show in passed_filter:
    past.append({
      'venue_id': show.venue_id,
      'venue_name': Venue.query.get(show.venue_id).name,
      'venue_image_link': Venue.query.get(show.venue_id).image_link,
      'start_time': show.start_time.strftime("%m/%d/%Y, %H:%M")
    })
  data = {
    'id': artist_id,
    'name': artist.name,
    'genres': artist.genres,
    'city': artist.city,
    'state': artist.state,
    'phone': artist.phone,
    'facebook_link': artist.facebook_link,
    'image_link': artist.image_link,
    'website': artist.website,
    'seeking_venue': artist.seeking_venue,
    'seeking_description': artist.seeking_description,
    'upcoming_shows': coming, 
    'upcoming_shows_count': len(coming),
    'past_shows': past,
    'past_shows_count': len(past)
  }

  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------

@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  id = artist_id
  form = ArtistForm()
  artist={
    "id": id,
    "name": Artist.query.get(id).name,
    "genres": Artist.query.get(id).genres,
    "city": Artist.query.get(id).city,
    "state": Artist.query.get(id).state,
    "phone": Artist.query.get(id).phone,
    "website": Artist.query.get(id).website,
    "facebook_link": Artist.query.get(id).facebook_link,
    "seeking_venue": Artist.query.get(id).seeking_venue,
    "seeking_description": Artist.query.get(id).seeking_description,
    "image_link": Artist.query.get(id).image_link
  }
 
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  
  try:
    artist = Artist.query.get(artist_id)

    artist.name = request.form.get('name')
    artist.city = request.form.get('city')
    artist.state = request.form.get('state')
    artist.phone = request.form.get('phone')
    artist.image_link = request.form.get('image_link')
    artist.genres = request.form.getlist('genres')
    artist.facebook_link = request.form.get('facebook_link')
    artist.website = request.form.get('website')
    artist.seeking_description = request.form.get('seeking_description')
    if request.form.get('seeking_venue') == 'Yes':
      artist.seeking_venue = True
    else: 
      artist.seeking_venue = False  
    
    db.session.commit()
    flash('Artist ' + artist.name + ' was successfully edited!')
  except:
    db.session.rollback()
    flash('An error occurred. Artist ' + artist.name + ' could not be listed.')
  finally:
    db.session.close()

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  id = venue_id
  form = VenueForm()
  venue={
    "id": id,
    "name": Venue.query.get(id).name,
    "genres": Venue.query.get(id).genres,
    "city": Venue.query.get(id).city,
    "state": Venue.query.get(id).state,
    "address": Venue.query.get(id).address,
    "phone": Venue.query.get(id).phone,
    "website": Venue.query.get(id).website,
    "facebook_link": Venue.query.get(id).facebook_link,
    "seeking_talent": Venue.query.get(id).seeking_talent,
    "seeking_description": Venue.query.get(id).seeking_description,
    "image_link": Venue.query.get(id).image_link  
  }
 
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):

  try:
    venue = Venue.query.get(venue_id)

    venue.name = request.form.get('name')
    venue.city = request.form.get('city')
    venue.state = request.form.get('state')
    venue.address = request.form.get('address')
    venue.phone = request.form.get('phone')
    venue.image_link = request.form.get('image_link')
    venue.genres = request.form.getlist('genres')
    venue.facebook_link = request.form.get('facebook_link')
    venue.website = request.form.get('website')
    venue.seeking_description = request.form.get('seeking_description')
    if request.form.get('seeking_talent') == 'Yes':
      venue.seeking_talent = True
    else: 
      venue.seeking_talent = False  
    
    db.session.commit()
    flash('Artist ' + venue.name + ' was successfully edited!')
  except:
    db.session.rollback()
    flash('An error occurred. Artist ' + venue.name + ' could not be listed.')
  finally:
    db.session.close()

  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  
  try:
    name = request.form.get('name')
    city = request.form.get('city')
    state = request.form.get('state')
    phone = request.form.get('phone')
    image_link = request.form.get('image_link')
    genres = request.form.getlist('genres')
    facebook_link = request.form.get('facebook_link')
    website = request.form.get('website')
    seeking_description = request.form.get('seeking_description')
    if request.form.get('seeking_venue') == 'Yes':
      seeking_venue = True
    else: 
      seeking_venue = False

    newArtist = Artist(name=name, city=city, state=state, phone=phone,
          image_link=image_link, genres=genres, facebook_link=facebook_link, website=website, 
          seeking_venue=seeking_venue, seeking_description=seeking_description)

    db.session.add(newArtist)
    db.session.commit()
     # on successful db insert, flash success
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
  except:
    db.session.rollback()
    flash('An error occurred. Artist ' + request.form.get('name') + ' could not be listed.')
  finally:
    db.session.close()

  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
 
  allshow = Shows.query.all()
  data=[]
  for i in allshow:
    data.append({
      'venue_id': i.venue_id,
      'venue_name': Venue.query.get(i.venue_id).name,
      'artist_id': i.artist_id,
      'artist_name': Artist.query.get(i.artist_id).name, 
      'artist_image_link': Artist.query.get(i.artist_id).image_link,
      'start_time': i.start_time.strftime("%m/%d/%Y, %H:%M")
    })
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  
  try:
    artist_id = request.form.get('artist_id')
    venue_id = request.form.get('venue_id')
    start_time = request.form.get('start_time')

    newShow = Shows(artist_id=artist_id, venue_id=venue_id, start_time=start_time)
    db.session.add(newShow)
    db.session.commit()
     # on successful db insert, flash success
    flash('Show was successfully listed!')
  except:
    db.session.rollback()
    flash('An error occurred. Show could not be listed.')
  finally:
    db.session.close()

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

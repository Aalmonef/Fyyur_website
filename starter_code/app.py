#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for, abort
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
from sqlalchemy import desc
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# TODO: connect to a local postgresql database
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://az@localhost:5432/Fyyur'

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    seeking_description = db.Column(db.String(500), default='')
    seeking_talent = db.Column(db.Boolean, default=False)
    website = db.Column(db.String(120))

    show = db.relationship('Show',backref='Venue',lazy='dynamic')

    # TODO: implement any missing fields, as a database migration using Flask-Migrate

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    seeking_description = db.Column(db.String(500), default='')
    seeking_talent = db.Column(db.Boolean, default=False)
    seeking_venue = db.Column(db.String(500), default='')
    website = db.Column(db.String(120))
   
    show = db.relationship('Show',backref='Artist')

    def __repr__(self):
         return ('{name}'.format(name = self.name))
    # TODO: implement any missing fields, as a database migration using Flask-Migrate

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.
class Show(db.Model):
     __tablename__ = 'Show'
     id = db.Column (db.Integer, primary_key=True)
     artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'), nullable=False)
     venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable=False)
     start_time = db.Column(db.String(50))
#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

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
  data=[]
  v = Venue.query.all()
  time = datetime.now().strftime('%Y-%m-%d %H:%S:%M')
  v_city=''
  for venue in v:
    upshow = venue.show.filter(Show.start_time > time).all()
    if(v_city == venue.city + venue.state):  
      v1 = {'id':venue.id, 'name':venue.name, 'num_upcoming_shows':len(upshow)}
      data[len(data)-1]['venues'].append(v1)
    else:
        v_city= venue.city + venue.state
        v2 = {'city':venue.city, 'state':venue.state, 'venues':[{'id':venue.id, 'name':venue.name, 'num_upcoming_shows':len(upshow)}]}
        data.append(v2)
  return render_template('pages/venues.html', areas=data);

  
  # data=[{
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "venues": [{
  #     "id": 1,
  #     "name": " ",
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
  

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  
  
  search_term = request.form.get('search_term','')
  r = Venue.query.filter(Venue.name.ilike(f'%{search_term}%'))
  response={
    "count": r.count(),
    "data": r
  }
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  v = Venue.query.get(venue_id)
  s = Show.query.filter_by(venue_id=venue_id).all()
  
  upshows = []
  pshows = []
 
  for show in s:
       data = {
          "artist_id":show.artist_id,
          "artist_name": show.Artist.name,
          "artist_image_link": show.Artist.image_link,
          "start_time": format_datetime(str(show.start_time))
        }
       time = datetime.strptime(show.start_time, '%Y-%m-%d %H:%M:%S')
       if not time:
            upshows.append(data)
        
       else:
            pshows.append(data)
             

  data={
    "id": v.id,
    "name": v.name,
    "genres": v.genres,
    "address": v.address,
    "city": v.city,
    "state": v.state,
    "phone": v.phone,
    "website": v.website,
    "facebook_link": v.facebook_link,
    "seeking_talent": v.seeking_talent,
    "seeking_description": v.seeking_description,
    "image_link": v.image_link,
    "past_shows": pshows,
    "upcoming_shows": upshows,
    "past_shows_count": len(pshows),
    "upcoming_shows_count": len(upshows),
  }
  
  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  try:
    name = request.form['name']
    city = request.form['city']
    state = request.form['state']
    address = request.form['address']
    phone = request.form['phone']
    genres = request.form['genres']
    image_link = request.form['image_link']
    facebook_link = request.form['facebook_link']
    v = Venue(name=name, city=city, state=state, address=address, phone=phone, genres=genres, image_link=image_link, facebook_link=facebook_link)
    db.session.add(v)
    db.session.commit()
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
    return redirect(url_for('create_venue_form'))
  except:
    db.session.rollback()
    return render_template('errors/404.html')
  finally:
    return render_template('pages/home.html')
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion

  # on successful db insert, flash success
  # except:
  #   db.session.rollback()
  #   flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
  #   print(form)
  #   return redirect(url_for('create_venue_form'))
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
    try:
       Venue.query.filter_by(id = venue_id).delete()
       db.session.commit()
    except:
       db.session.rollback()
       abort(404)
    finally:
        return render_template('pages/home.html')
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
 

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  data=[]
  a = Artist.query.all()
  try:
    for artist in a:
        v1 = {'id':artist.id, 'name':artist.name}
        data.append(v1)
    return render_template('pages/artists.html', artists=data)

  except:
    return render_template('errors/404.html')
  

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".

  search_term = request.form.get('search_term','')

  r = Artist.query.filter(Artist.name.ilike(f'%{search_term}%'))

  response={
    "count": r.count(),
    "data": r
  }
  
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id

  a = Artist.query.get(artist_id)
  s = Show.query.filter_by(artist_id=artist_id).all()
  
  upshows = []
  pshows = []
 
  for show in s:
       data = {
          "artist_id":show.artist_id,
          "artist_name": show.Artist.name,
          "artist_image_link": show.Artist.image_link,
          "start_time": format_datetime(str(show.start_time))
        }
       time = datetime.strptime(show.start_time, '%Y-%m-%d %H:%M:%S')
       if not time:
            upshows.append(data)
        
       else:
            pshows.append(data)
             

  data={
    "id": a.id,
    "name": a.name,
    "genres": a.genres,
    "city": a.city,
    "state": a.state,
    "phone": a.phone,
    "website": a.website,
    "facebook_link": a.facebook_link,
    "seeking_talent": a.seeking_talent,
    "seeking_description": a.seeking_description,
    "image_link": a.image_link,
    "past_shows": pshows,
    "upcoming_shows": upshows,
    "past_shows_count": len(pshows),
    "upcoming_shows_count": len(upshows),
  }
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  nA = Artist.query.get(artist_id)
  artist={
    "id": nA.id,
    "name": nA.name,
    "genres": nA.genres,
    "city": nA.city,
    "state": nA.state,
    "phone": nA.phone,
    "website": nA.website,
    "facebook_link": nA.facebook_link,
    "seeking_venue": nA.seeking_venue,
    "seeking_description": nA.seeking_description,
    "image_link": nA.image_link
  }
  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  
  try:
    oldArtist = Artist.query.get(artist_id)
    oldArtist.name = request.form['name']
    oldArtist.city = request.form['city']
    oldArtist.state = request.form['state']
    oldArtist.phone = request.form['phone']
    oldArtist.genres = request.form['genres']
    oldArtist.image_link = request.form['image_link']
    oldArtist.facebook_link = request.form['facebook_link']

    db.session.commit()
    flash('Artist ' + request.form['name'] + ' was successfully changed!')

  except:
    db.session.rollback()
    flash('An error occurred. Artist ' + request.form['name'] + ' could not be changed.')
    return render_template('errors/500.html')
  finally:
    db.session.close()
  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  nV = Venue.query.get(venue_id)
  venue={
    "id": nV.id,
    "name": nV.name,
    "genres": nV.genres,
    "address": nV.address,
    "city": nV.city,
    "state": nV.state,
    "phone": nV.phone,
    "website": nV.website,
    "facebook_link": nV.facebook_link,
    "seeking_talent": nV.seeking_talent,
    "seeking_description": nV.seeking_description,
    "image_link": nV.image_link
  }
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  try:
    oldVenue = Venue.query.get(venue_id)
    oldVenue.name = request.form['name']
    oldVenue.city = request.form['city']
    oldVenue.state = request.form['state']
    oldVenue.phone = request.form['phone']
    oldVenue.genres = request.form['genres']
    oldVenue.image_link = request.form['image_link']
    oldVenue.facebook_link = request.form['facebook_link']

    db.session.commit()
    flash('Venue ' + request.form['name'] + ' was successfully changed!')

  except:
    db.session.rollback()
    flash('An error occurred. Venue ' + request.form['name'] + ' could not be changed.')
    return render_template('errors/500.html')
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
    name = request.form['name']
    city = request.form['city']
    state = request.form['state']
    phone = request.form['phone']
    genres = request.form['genres']
    image_link = request.form['image_link']
    facebook_link = request.form['facebook_link']
    a = Artist(name=name, city=city, state=state, phone=phone, genres=genres, image_link=image_link, facebook_link=facebook_link)
    db.session.add(a)
    db.session.commit()
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
    return render_template('pages/home.html')  
  except:
    db.session.rollback()
    flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')
    return render_template('errors/404.html')
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion

  # on successful db insert, flash success
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  upshows=Show.query.order_by(desc(Show.start_time))
  data=[]
  for upshow in upshows:
      v1 = {'venue_id' :upshow.venue_id,
                'venue_name' :upshow.Venue.name,
                'artist_id' :upshow.artist_id,
                'artist_name' :upshow.Artist.name,
                'artist_image_link' :upshow.Artist.image_link,
                'start_time' :upshow.start_time}
      data.append(v1)
  return render_template('pages/shows.html', shows=data)
  
@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead
  try:
      artist_id = request.form['artist_id']
      venue_id = request.form['venue_id']
      start_time = request.form['start_time']
      s = Show(artist_id=artist_id, venue_id=venue_id, start_time=start_time)
      db.session.add(s)
      db.session.commit()
      flash('Show was successfully listed!')
      return render_template('pages/home.html')
  except:
      db.session.rollback()
      flash('An error occurred. Show could not be listed.')
      return render_template('errors/404.html')
  # on successful db insert, flash success
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  

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

import json
import dateutil.parser
import babel
from flask import (
    render_template,
    request,
    flash,
    redirect,
    url_for
)
from flask_moment import Moment
import logging
from logging import Formatter, FileHandler
from forms import *
from flask_migrate import Migrate
from forms import VenueForm, ArtistForm, ShowForm
import sys
from models import app, db, Venue, Show, Artist
from datetime import datetime

moment = Moment(app)
migrate = Migrate(app, db)

# TODO: connect to a local postgresql database


#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#


def format_datetime(value, format='medium'):
    date = dateutil.parser.parse(value)
    if format == 'full':
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format = "EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format)


app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#


@ app.route('/')
def index():
    return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@ app.route('/venues')
def venues():
    # TODO: replace with real venues data.
    #       num_shows should be aggregated based on number of upcoming shows
    # per venue.
    trial = list(set([(i.city, i.state) for i in Venue.query.all()]))
    data = []
    for i in range(len(trial)):
        venues = [{"id": i.id, "name": i.name, "num_upcoming_shows": len(Show.query.filter_by(venue_id=i.id).all())}
                  for i in Venue.query.filter_by(city=trial[i][0], state=trial[i][1])]
        city = trial[i][0]
        state = trial[i][1]
        data.append({"city": city, "state": state, "venues": venues})
    return render_template('pages/venues.html', areas=data)


@ app.route('/venues/search', methods=['POST'])
def search_venues():
    # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
    # seach for Hop should return "The Musical Hop".
    # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
    query = request.form.get('search_term', '')
    results = Venue.query.filter(
        Venue.name.ilike("%" + query + "%")).all()
    data = [{"id": i.id, "name": i.name, "num_upcoming_shows": len(Show.query.filter_by(venue_id=i.id).all())}
            for i in results]
    response = {
        "count": len(results),
        "data": data
    }
    return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))


@ app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    # shows the venue page with the given venue_id
    # TODO: replace with real venue data from the venues table, using venue_id
    venue = Venue.query.get(venue_id)
    upcoming_shows = db.session.query(Artist, Show).join(Show).join(Venue).\
        filter(
        Show.venue_id == venue_id,
        Show.artist_id == Artist.id,
        Show.start_time > datetime.now()
    ).\
        all()
    past_shows = db.session.query(Artist, Show).join(Show).join(Venue).\
        filter(
        Show.venue_id == venue_id,
        Show.artist_id == Artist.id,
        Show.start_time < datetime.now()
    ).\
        all()
    data = {
        "id": venue.id,
        "name": venue.name,
        "genres": venue.genres.split(","),
        "address": venue.address,
        "city": venue.city,
        "state": venue.state,
        "phone": venue.phone,
        "website": venue.website,
        "facebook_link": venue.facebook_link,
        "seeking_talent": venue.seeking_talent,
        "seeking_description": venue.seeking_description,
        "image_link": venue.image_link,
        "past_shows":  [{
            'artist_id': artist.id,
            "artist_name": artist.name,
            "artist_image_link": artist.image_link,
            "start_time": show.start_time.strftime("%m/%d/%Y, %H:%M")
        } for artist, show in past_shows],
        "upcoming_shows": [{
            'artist_id': artist.id,
            'artist_name': artist.name,
            'artist_image_link': artist.image_link,
            'start_time': show.start_time.strftime("%m/%d/%Y, %H:%M")
        } for artist, show in upcoming_shows],
        "past_shows_count": len(past_shows),
        "upcoming_shows_count": len(upcoming_shows)
    }
    data = list(filter(lambda d: d['id'] ==
                       venue_id, [data]))[0]
    return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------


@ app.route('/venues/create', methods=['GET'])
def create_venue_form():
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)


@ app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    venue_form = VenueForm(request.form)
    # TODO: insert form data as a new Venue record in the db, instead
    venue = Venue(name=venue_form.name.data,
                  genres=','.join(venue_form.genres.data),
                  address=venue_form.address.data,
                  city=venue_form.city.data,
                  state=venue_form.state.data,
                  phone=venue_form.phone.data,
                  facebook_link=venue_form.facebook_link.data,
                  image_link=venue_form.image_link.data,
                  seeking_description=venue_form.seeking_description.data,
                  seeking_talent=venue_form.seeking_talent.data,
                  website=venue_form.website.data)

    # TODO: modify data to be the data object returned from db insertion
    try:
        db.session.add(venue)
        db.session.commit()
    # on successful db insert, flash success
        flash('Venue ' + request.form['name'] + ' was successfully listed!')
    except:
        db.session.rollback()
        flash('An error occurred. Venue ' + request.form['name'] +
              ' could not be listed.')
    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    return render_template('pages/home.html')


@ app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
    # TODO: Complete this endpoint for taking a venue_id, and using
    # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
    try:
        db.session.query.get(venue_id).delete()
        db.session.commit()
    except:
        db.sesssion.rollback()
    # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
    # clicking that button delete it from the db then redirect the user to the homepage
    return None

#  Artists
#  ----------------------------------------------------------------


@ app.route('/artists')
def artists():
    # TODO: replace with real data returned from querying the database
    data = [{"id": i.id, "name": i.name} for i in Artist.query.all()]
    return render_template('pages/artists.html', artists=data)


@ app.route('/artists/search', methods=['POST'])
def search_artists():
    # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
    # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
    # search for "band" should return "The Wild Sax Band".
    query = request.form.get('search_term', '')
    results = Artist.query.filter(
        Artist.name.ilike("%" + query + "%")).all()
    data = [{"id": i.id, "name": i.name, "num_upcoming_shows": len(Show.query.filter_by(artist_id=i.id).all())}
            for i in results]
    response = {
        "count": len(results),
        "data": data
    }
    return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))


@ app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    # shows the venue page with the given venue_id
    # TODO: replace with real venue data from the venues table, using venue_id
    upcoming_shows = db.session.query(Artist, Show).join(Show).join(Venue).\
        filter(
        Show.venue_id == artist_id,
        Show.artist_id == Artist.id,
        Show.start_time > datetime.now()
    ).\
        all()
    past_shows = db.session.query(Artist, Show).join(Show).join(Venue).\
        filter(
        Show.venue_id == artist_id,
        Show.artist_id == Artist.id,
        Show.start_time < datetime.now()
    ).\
        all()
    artist = Artist.query.get(artist_id)
    data = {
        "id": artist.id,
        "name": artist.name,
        "genres": artist.genres.split(","),
        "city": artist.city,
        "state": artist.state,
        "phone": artist.phone,
        "facebook_link": artist.facebook_link,
        "image_link": artist.image_link,
        "past_shows":  [{
            'artist_id': artist.id,
            "artist_name": artist.name,
            "artist_image_link": artist.image_link,
            "start_time": show.start_time.strftime("%m/%d/%Y, %H:%M")
        } for artist, show in past_shows],
        "upcoming_shows": [{
            'artist_id': artist.id,
            'artist_name': artist.name,
            'artist_image_link': artist.image_link,
            'start_time': show.start_time.strftime("%m/%d/%Y, %H:%M")
        } for artist, show in upcoming_shows],
        "past_shows_count": len(past_shows),
        "upcoming_shows_count": len(upcoming_shows)
    }
    return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------


@ app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    form = ArtistForm()
    artist_query = Artist.query.get(artist_id)
    artist = {
        "id": artist_query.id,
        "name": artist_query.name,
        "genres": json.dumps(form.genres.data),
        "city": artist_query.city,
        "state": artist_query.state,
        "phone": artist_query.phone,
        "facebook_link": artist_query.facebook_link,
        "image_link": artist_query.image_link,
        "address": artist_query.address,
        "website": artist_query.website,
        "seeking_venue": artist_query.seeking_venue,
        "seeking_description": artist_query.seeking_description
    }
    # TODO: populate form with fields from artist with ID <artist_id>
    return render_template('forms/edit_artist.html', form=form, artist=artist)


@ app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    # TODO: take values from the form submitted, and update existing
    # artist record with ID <artist_id> using the new attributes
    form = ArtistForm(request.form)
    artist = Artist.query.get(artist_id)
    artist.name = form.name.data
    artist.genres = json.dumps(form.genres.data)
    artist.city = form.city.data
    artist.state = form.state.data
    artist.phone = form.phone.data
    artist.facebook_link = form.facebook_link.data
    artist.image_link = form.image_link.data
    artist.website = form.website.data
    artist.seeking_venue = form.seeking_venue.data
    artist.seeking_description = form.seeking_description.data
    artist.addresss = form.address.data
    try:
        db.session.add(artist)
        db.session.commit()
    except:
        db.session.rollback()
    return redirect(url_for('show_artist', artist_id=artist_id))


@ app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    form = VenueForm(request.form)
    venue = Venue.query.get(venue_id)
    venue = {
        "id": venue.id,
        "name": venue.name,
        "genres": ','.join(form.genres.data),
        "address": venue.address,
        "city": venue.city,
        "state": venue.state,
        "phone": venue.phone,
        "website": venue.website,
        "facebook_link": venue.facebook_link,
        "seeking_talent": venue.seeking_talent,
        "seeking_description": venue.seeking_description,
        "image_link": venue.image_link,
    }
    # TODO: populate form with values from venue with ID <venue_id>
    return render_template('forms/edit_venue.html', form=form, venue=venue)


@ app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    # TODO: take values from the form submitted, and update existing
    # venue record with ID <venue_id> using the new attributes

    form = VenueForm(request.form)
    venue = Venue.query.get(venue_id)
    venue.name = form.name.data
    venue.genres = '.'.join(form.genres.data)
    venue.city = form.city.data
    venue.state = form.state.data
    venue.address = form.address.data
    venue.phone = form.phone.data
    venue.facebook_link = form.facebook_link.data
    venue.image_link = form.image_link.data
    venue.seeking_description = form.seeking_description.data,
    venue.seeking_talent = form.seeking_talent.data,
    venue.website = form.website.data
    try:
        db.session.add(venue)
        db.session.commit()
    except:
        db.session.rollback()
    return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------


@ app.route('/artists/create', methods=['GET'])
def create_artist_form():
    form = ArtistForm()
    return render_template('forms/new_artist.html', form=form)


@ app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    # called upon submitting the new artist listing form
    # TODO: insert form data as a new Venue record in the db, instead
    # TODO: modify data to be the data object returned from db insertion
    artist_form = ArtistForm(request.form)
    # TODO: insert form data as a new Venue record in the db, instead
    artist = Artist(name=artist_form.name.data,
                    genres=','.join(artist_form.genres.data),
                    city=artist_form.city.data,
                    state=artist_form.state.data,
                    phone=artist_form.phone.data,
                    facebook_link=artist_form.facebook_link.data,
                    image_link=artist_form.image_link.data,
                    address=artist_form.address.data,
                    seeking_venue=artist_form.seeking_venue.data,
                    website=artist_form.website.data,
                    seeking_description=artist_form.seeking_description.data)
    # TODO: modify data to be the data object returned from db insertion
    try:
        db.session.add(artist)
        db.session.commit()
        # on successful db insert, flash success
        flash('Artist ' + request.form['name'] + ' was successfully listed!')
    except:
        db.session.rollback()
        flash('An error occurred. Artist ' + request.form['name'] +
              ' could not be listed.')
    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
    return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@ app.route('/shows')
def shows():
    # displays list of shows at /shows
    # TODO: replace with real venues data.
    #       num_shows should be aggregated based on number of upcoming shows per venue.
    data = [{"venue_id": i.venue_id, "venue_name": Venue.query.get(i.venue_id).name, "artist_id": i.artist_id, "artist_name": Artist.query.get(i.artist_id).name,
             "artist_image_link": Artist.query.get(i.artist_id).image_link, "start_time": str(i.start_time)} for i in Show.query.all()]
    return render_template('pages/shows.html', shows=data)


@ app.route('/shows/create')
def create_shows():
    # renders form. do not touch.
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)


@ app.route('/shows/create', methods=['POST'])
def create_show_submission():
    # called to create new shows in the db, upon submitting new show listing form
    # TODO: insert form data as a new Show record in the db, instead
    # on successful db insert, flash success

    show_form = ShowForm(request.form)
    # TODO: insert form data as a new Venue record in the db, instead
    show = Show(artist_id=show_form.artist_id.data,
                venue_id=show_form.venue_id.data,
                start_time=show_form.start_time.data)
    # TODO: modify data to be the data object returned from db insertion
    try:
        db.session.add(show)
        db.session.commit()
        # on successful db insert, flash success
        flash('Show' + ' was successfully listed!')
    except:
        db.session.rollback()
        print(sys.exc_info())
        flash('An error occurred. Show' +
              ' could not be listed.')
    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Show could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    return render_template('pages/home.html')


@ app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404


@ app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
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

import matplotlib.pyplot as plt

from application.models import *

from flask import render_template, redirect, request, url_for

from sqlalchemy import func, or_


import os, pytz

from flask import current_app as app
'''The current_app object is a proxy to the current Flask 
application instance, which is used to access and 
interact with the current Flask application context. '''
# For example, you might use app to access the configuration
# values of your Flask application or to register new routes and
# views with the application.


@app.route('/', methods=['GET'])
def home():

    venues = Venue.query.all()

    return render_template('index.html', venues=venues)

@app.route('/home_page/search', methods=['POST'])
def home_page_search_results():

    query = request.form.get('q')

    venues = Venue.query.filter(or_(Venue.v_name.ilike('%{}%'.format(query)),
                                    Venue.v_place.ilike(f'%{query}%'),
                                    Venue.v_location.ilike(f'%{query}%'))).all()

    shows = Show.query.filter(or_(Show.s_name.ilike(f'%{query}%'), Show.s_rating.ilike(
        f'%{query}%'), Show.s_tags.ilike(f'%{query}%'), Show.s_time.ilike(f'%{query}%'))).all()

    return render_template('home_page_search_results.html', venues=venues, shows=shows, query=query)




@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():

    if request.method == 'POST':

        user_name = request.form.get('a_name')
        pswd = request.form.get('a_password')

        admin_details = Admin.query.filter_by(a_username=user_name).first()
        if(admin_details):
            if admin_details.a_username == user_name and admin_details.a_password == pswd:

                venues = Venue.query.all()
                #shows = Show.query.all()

                # render_template('admin_dash.html', admin_details=admin_details, venues=venues)# ,shows = shows)
                return redirect('/admin/dashboard')

            return render_template('login_fail.html', admin=1, wrong_pswd=1)
        else:
            return render_template('login_fail.html', admin=1, wrong_username=1)

    return render_template('admin_login.html')

@app.route('/admin/dashboard', methods=['GET'])
def admin_dashboard():

    admin_details = Admin.query.first()
    venues = Venue.query.all()
    return render_template('admin_dash.html', admin_details=admin_details, venues=venues)

@app.route('/add/venue', methods=['GET', 'POST'])
def create_venue():

    admin_details = Admin.query.first()

    if request.method == 'POST':

        name = request.form.get('venue_name')

        venue_exists = Venue.query.filter_by(v_name=name).first()
        if (venue_exists):
            return f'''<h2> Error: A venue with the name <a href="/admin/venue/{venue_exists.v_id}/home_view">{name}</a> already exists!</h2>
                       <h2>Please give the new venue a unique name.<h2>
                       <a href="/add/venue"> <h3>GO BACK</h3> </a>
                        '''

        place = request.form.get('place')
        location = request.form.get('location')
        capacity = request.form.get('capacity')

        new_venue = Venue(v_name=name, v_place=place,
                          v_location=location, v_capacity=capacity, admin_id=1)
        db.session.add(new_venue)
        db.session.commit()

        return redirect(url_for('admin_dashboard'))

    return render_template('create_venue.html', admin_details=admin_details)

@app.route('/venue/<int:v_id>/edit', methods=['GET', 'POST'])
def edit_venue(v_id):

    venue_details = Venue.query.get(v_id)

    if request.method == 'POST':

        name = request.form.get('venue_name')

        venue_exists = Venue.query.filter_by(v_name=name).first()
        if (venue_exists and venue_exists.v_id != v_id) :
            return f'''<h2> Error: A venue with the name <a href="/admin/venue/{venue_exists.v_id}/home_view">{name}</a> already exists! </h2>
                       <h2>Please give the venue a unique name.<h2>
                       <a href="/venue/{v_id}/edit"> <h3>GO BACK</h3> </a>
                        '''

        venue_details.v_name = name
        venue_details.v_place = request.form.get('place')
        venue_details.v_location = request.form.get('location')
        venue_details.v_capacity = request.form.get('capacity')

        db.session.commit()

        return redirect(url_for('admin_dashboard'))

    admin_details = Admin.query.first()
    return render_template('edit_venue.html', admin_details=admin_details, venue_details=venue_details)

@app.route('/venue/<int:venue_id>/add_show', methods=['GET', 'POST'])
def add_show_to_venue(venue_id):

    if request.method == 'POST':

        time = request.form.get('s_timing')

        show = Show.query.filter_by(s_time=time).first()

        if show:
            return f'''<h2> Error: A show named <a href="/api/show/{show.s_id}/display">{show.s_name}</a> is already scheduled at time {time} in Venue - <a href="/api/venue/{venue_id}/display">{venue_id} - {show.which_venue.v_name}</a>. </h2>
                       <h2>Please choose some other time slot.</h2>
                       <a href="/venue/{venue_id}/add_show"> <h2>Go Back</h2> </a>
                        '''
        name = request.form.get('show_name')
        rat = request.form.get('s_rating')
        tags = request.form.get('s_tags')
        prc = request.form.get('s_price')

        new_show = Show(s_name=name, s_rating=rat,
                        s_tags=tags, s_time=time, s_price=prc, s_venue=venue_id)
        db.session.add(new_show)
        db.session.commit()

        return redirect(url_for('admin_dashboard'))

    admin_details = Admin.query.first()
    venue_details = Venue.query.get(venue_id)
    return render_template('create_show.html', admin_details=admin_details, venue_details=venue_details)

@app.route('/venue/<int:v_id>/show/<int:show_id>/edit', methods=['GET', 'POST'])
def edit_show(v_id, show_id):

    show_details = Show.query.get(show_id)

    if request.method == 'POST':

        s_venue = request.form.get('s_venue')

        venue_id = Venue.query.get(s_venue)
        if venue_id is None:
            return f'''<h2> Error: Venue with id {s_venue} dosen\'t exists! </h2>
                       <br><br>
                       <a href="{url_for('admin_dashboard')}"> <h3>GO BACK</h3> </a>
                        '''
        s_time = request.form.get('s_timing')
        show = Show.query.filter_by(s_time=s_time).first()
        if show and show.s_id != show_id:
            return f'''<h2> Error: A show named <a href="/api/show/{show.s_id}/display">{show.s_name}</a> is already scheduled at time {s_time} in Venue - <a href="/api/venue/{s_venue}/display">{s_venue} - {show.which_venue.v_name}</a>. </h2>
                       <h2>Please choose some other time slot.</h2>
                       <a href="/venue/{v_id}/add_show"> <h2>Go Back</h2> </a>
                        '''

        show_details.s_name = request.form.get('show_name')
        show_details.s_rating = request.form.get('s_rating')
        show_details.s_time = s_time
        show_details.s_tags = request.form.get('s_tags')
        show_details.s_price = request.form.get('s_price')
        show_details.s_venue = s_venue

        db.session.commit()

        return redirect(url_for('admin_dashboard'))

    admin_details = Admin.query.first()
    return render_template('edit_show.html', admin_details=admin_details, show_details=show_details)

@app.route('/venue/<int:v_id>/delete')
def delete_venue(v_id):
    venue_to_be_deleted = Venue.query.get(v_id)

    db.session.delete(venue_to_be_deleted)
    db.session.commit()

    return redirect(url_for('admin_dashboard'))

@app.route('/admin/venue/<int:v_id>/home_view')
def admin_venue_page(v_id):
    venue_details = Venue.query.get(v_id)
    return render_template('venue_page_admin.html', venue_details=venue_details)

@app.route('/admin/summary/show/ratings')
def shows_summary():

    image_paths = []
    total_ratings = 0

    total_users = User.query.count()
    total_bookings = Booking.query.count()

    venues = Venue.query.all()

    venue_dict = {}

    for venue in venues:

        if len(venue.v_shows) == 0:
            continue

        rating_flag = 0  # to check if there are venues with their shows having no ratings

        show_dict = {}
        for show in venue.v_shows:

            avg_rating = 0

            if len(show.s_ratings) != 0:

                for rating in show.s_ratings:
                    total_ratings += 1
                    avg_rating += rating.r_score

                avg_rating /= len(show.s_ratings)

                show_dict[show.s_name] = avg_rating
            else:
                rating_flag += 1

        if rating_flag == len(venue.v_shows):
            continue

        venue_dict[venue.v_name] = show_dict
        print(venue_dict)

        fig, ax = plt.subplots()
        ax.bar(show_dict.keys(), show_dict.values())
        filename = f'{venue.v_name.replace(" ", "_")}.png'
        filepath = os.path.join('static', 'images', filename)

        plt.title(f'Venue - {venue.v_name}')

        plt.savefig(filepath)
        image_paths.append(filepath)

    summary = [total_users, total_bookings, total_ratings]
    return render_template('adm_sum_show_ratings.html', image_paths=image_paths, summary=summary)

@app.route('/admin/summary')
def admin_summary():

    total_shows = Show.query.count()
    total_tickets_sold = Booking.query.with_entities(
        func.sum(Booking.no_of_tickets)).scalar()
    total_revenue = Booking.query.with_entities(
        func.sum(Booking.b_cost)).scalar()

    total_venues = 0
    image_paths = []
    total_tickets_sold = 0
    venues = Venue.query.all()

    for venue in venues:

        total_tickets_sold = 0

        total_venues += 1
        if len(venue.v_shows) == 0:
            continue

        num_shows = len(venue.v_shows)

        for show in venue.v_shows:
            for booking in show.s_bookings:
                total_tickets_sold += booking.no_of_tickets
            

        if num_shows != 0:
            occupancy = total_tickets_sold / \
                (num_shows * venue.v_capacity) * 100

        # Creating a new figure and axis for the venue
        fig, ax = plt.subplots()

        # Create a bar graph for the venue
        data = {
            'No. of Shows': num_shows,
            'Total Tickets Sold': total_tickets_sold,
            'Occupancy': occupancy,
        }
        ax.bar(data.keys(), data.values())

        filename = f'{venue.v_name.replace(" ", "_")}_1.png'
        filepath = os.path.join('static', 'images', filename)
        plt.title(f'Venue - {venue.v_name}')
        plt.savefig(filepath)
        image_paths.append(filepath)

    summary = [total_venues, total_shows,
               total_tickets_sold, total_revenue]
    print(image_paths)
    return render_template('admin_summary.html', summary=summary, image_paths=image_paths)

@app.route('/admin/search', methods=['POST'])
def admin_search_shows_venues():

    query = request.form.get('q')

    venues = Venue.query.filter(or_(Venue.v_name.ilike('%{}%'.format(query)),
                                    Venue.v_place.ilike(f'%{query}%'),
                                    Venue.v_location.ilike(f'%{query}%'))).all()

    shows = Show.query.filter(or_(Show.s_name.ilike(f'%{query}%'), Show.s_rating.ilike(
        f'%{query}%'), Show.s_tags.ilike(f'%{query}%'), Show.s_time.ilike(f'%{query}%'))).all()

    return render_template('admin_page_search_results.html', venues=venues, shows=shows, query_string=query)


@app.route('/user_login', methods=['GET', 'POST'])
def user_login():

    if request.method == 'POST':

        user_name = request.form.get('u_name')
        pswd = request.form.get('u_password')

        user_details = User.query.filter_by(u_username=user_name).first()
        if(user_details):
            if user_details.u_username == user_name and user_details.u_password == pswd:

                return redirect(f'/user/{user_details.user_id}')

            return render_template('login_fail.html', user=1, wrong_pswd=1)
        else:
            return render_template('login_fail.html', user=1, wrong_username=1)

    return render_template('user_login.html')

@app.route('/user_register', methods=['GET', 'POST'])
def register_user():
    if request.method == 'POST':

        user_name = request.form.get('u_name')
        user = User.query.filter_by(u_username=user_name).first()
        if user:
            return f'''<h2> Error: A user with username <span style="text-decoration:underline";>{user_name}</span> already exists!</h2>
                       <h2>Please try some other username.</h2>
                       <a href="/user_register"> <h2>Go Back</h2> </a>
                        '''

        pswd = request.form.get('u_password')
        email = request.form.get('u_email')

        u = User(u_username=user_name, u_password=pswd,
                 u_email=email, is_admin=False)
        db.session.add(u)
        db.session.commit()

        return redirect('/user_login')
    
    return render_template('user_register.html')

@app.route('/user/<int:u_id>', methods=['GET', 'POST'])
def user_dashboard(u_id):

    user_details = User.query.get(u_id)
    venues = Venue.query.all()

    return render_template('u_dashboard.html', user_details=user_details, venues=venues)

@app.route('/user/<int:u_id>/bookings', methods=['GET'])
def user_bookings(u_id):

    user_details = User.query.get(u_id)
    bookings = Booking.query.filter_by(user_id=u_id).all()
    ratings_of_this_user = Ratings.query.filter_by(user_id=u_id)
    return render_template('u_bookings.html', user_details=user_details, bookings=bookings)

@app.route('/user/<int:u_id>/profile')
def user_profile(u_id):

    user_details = User.query.get(u_id)
    return render_template('user_profile.html', user_details=user_details)

@app.route('/user/<int:user_id>/venue/<int:venue_id>/show/<int:show_id>/book', methods=['GET', 'POST'])
def book_show(user_id, venue_id, show_id):

    show_details = Show.query.get(show_id)

    if request.method == 'POST':

        tickets = request.form.get('no_of_tickets')
        total_cost = request.form.get('total_price')

        b_date = datetime.utcnow().date()
        b_time_IST = pytz.timezone('Asia/Kolkata').fromutc(datetime.utcnow()).time()

        new_booking = Booking(user_id=user_id, v_id=venue_id, s_id=show_id,
                              no_of_tickets=tickets, b_cost=total_cost, b_date=b_date, b_time=b_time_IST)

        show_details.seats_booked += int(tickets)

        db.session.add(new_booking)
        db.session.commit()

        return redirect(f'/user/{user_id}/bookings')

    user_details = User.query.get(user_id)

    available_seats = show_details.which_venue.v_capacity - show_details.seats_booked

    return render_template('u_book_show.html', user_details=user_details, venue_id=venue_id, show_details=show_details, available_seats=available_seats)

@app.route('/user/<int:user_id>/venue/<int:venue_id>/show/<int:show_id>/rate', methods=['GET', 'POST'])
def rate_show(user_id, venue_id, show_id):

    show_details = Show.query.get(show_id)

    if request.method == 'POST':

        rate_score = request.form.get('rating_score')

        new_rating = Ratings(user_id=user_id, s_id=show_id, r_score=rate_score)

        db.session.add(new_rating)
        db.session.commit()

        return redirect(f'/user/{user_id}/bookings')

    user_details = User.query.get(user_id)

    rating = Ratings.query.filter_by(user_id=user_id, s_id=show_id).first()
    # if rating == None:
    #     rating = {"r_score" : 0}

    return render_template('u_rate_show.html', user_details=user_details, venue_id=venue_id, show_details=show_details, rating=rating)

@app.route('/user/<int:user_id>/venue/<int:venue_id>/show/<int:show_id>/cancel/<int:b_id>', methods=['GET'])
def cancel_show(user_id, venue_id, show_id, b_id):

    booking = Booking.query.get(b_id)

    booking.which_show.seats_booked -= booking.no_of_tickets

    db.session.delete(booking)
    db.session.commit()

    return redirect(f'/user/{user_id}/bookings')

@app.route('/user/<int:u_id>/venue/<int:v_id>/home_view', methods=['GET'])
def venue_page(u_id, v_id):

    venue_details = Venue.query.get(v_id)

    return render_template('venue_page.html', venue_details=venue_details, user_id=u_id)

@app.route('/venue/<int:v_id>/show/<int:show_id>/delete')
def delete_show(v_id, show_id):

    show_to_be_deleted = Show.query.get(show_id)
    db.session.delete(show_to_be_deleted)
    db.session.commit()

    return redirect('/admin/dashboard')

@app.route('/user/<int:user_id>/search', methods=['POST'])
def user_search(user_id):

    query = request.form.get('q')

    venues = Venue.query.filter(or_(Venue.v_name.ilike('%{}%'.format(query)),
                                    Venue.v_place.ilike(f'%{query}%'),
                                    Venue.v_location.ilike(f'%{query}%'))).all()

    shows = Show.query.filter(or_(Show.s_name.ilike(f'%{query}%'), Show.s_rating.ilike(
        f'%{query}%'), Show.s_tags.ilike(f'%{query}%'), Show.s_time.ilike(f'%{query}%'))).all()

    user_details = User.query.get(user_id)

    return render_template('user_search_results.html', user_details=user_details, venues=venues, shows=shows)



@app.route('/api/venue/<int:v_id>/display')
def api_venue_page_display(v_id):

    venue = Venue.query.filter_by(v_id=v_id).first()
    if venue:
        return render_template('api_venue_page.html', venue_details=venue)
    else:
        return '''<h2>Venue dosen\'t exists.</h2>'''

@app.route('/api/show/<int:s_id>/display')
def api_show_page_display(s_id):

    show = Show.query.filter_by(s_id=s_id).first()
    if show:
        avg_rating = Ratings.query.filter_by(s_id=s_id).with_entities(
            func.avg(Ratings.r_score)).scalar()
        if avg_rating == None:
            avg_rating = 0

        return render_template('api_show_page.html', show_details=show, avg_rating_score=avg_rating)
    else:
        return '''<h2>Show dosen\'t exists.</h2>'''





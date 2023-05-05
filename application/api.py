
from sqlalchemy import func
from flask_restful import Resource, marshal_with, fields, reqparse, abort
from flask import render_template, redirect

from application.database import db
from application.models import *


# -------------------- Output Fields in JSON Format  --------------------
venue_fields = {
    "venue_id": fields.Integer(attribute="v_id"),
    "venue_name": fields.String(attribute="v_name"),
    "venue_place": fields.String(attribute="v_place"),
    "venue_location": fields.String(attribute="v_location"),
    "venue_capacity": fields.Integer(attribute="v_capacity"),
    "venue_shows": fields.List(fields.String, attribute="v_shows")
}

show_fields = {

    "show_id": fields.Integer(attribute="s_id"),
    "show_name": fields.String(attribute="s_name"),
    "show_rating": fields.String(attribute="s_rating"),
    "show_tags": fields.String(attribute="s_tags"),
    "show_time": fields.String(attribute="s_time"),
    "show_venue": fields.String(attribute="s_venue"),
    "show_price": fields.Integer(attribute="s_price")
}

# -------------------- Creating Parsers to handle data in the request body --------------------

# Defining what a typical request should look like
show_parser = reqparse.RequestParser(bundle_errors=True)
# show_parser.add_argument("s_id", type=int, required=True)
show_parser.add_argument("s_name", required=True)
show_parser.add_argument("s_rating", type=str)
show_parser.add_argument("s_tags")
show_parser.add_argument("s_time", type=str)
show_parser.add_argument("s_venue", type=int, required=True)
show_parser.add_argument("s_price", type=int, required=True)

venue_parser = reqparse.RequestParser(bundle_errors=True)
venue_parser.add_argument("v_name", required=True)
venue_parser.add_argument("v_place", required=True)
venue_parser.add_argument("v_location", required=True)
venue_parser.add_argument("v_capacity", type=int, required=True)



# ---------------------------------------- API classes ----------------------------------------
'''------------------  Show API  --------------------'''

class ShowApi(Resource):

    # CRUD operations

    @marshal_with(show_fields)
    def get(self, show_id):

        show = Show.query.filter_by(s_id=show_id).first()

        if show:
            return show, 200
        else:
            abort(404, message="Show dosen't exists!")

    def delete(self, show_id):

        show = Show.query.filter_by(s_id=show_id).first()

        if show:
            db.session.delete(show)
            db.session.commit()
            return "Successfully deleted", 200

        else:
            abort(404, message="Show dosen't exists!")

    @marshal_with(show_fields)
    def post(self):

        # Getting the data from the request body
        args = show_parser.parse_args()
        s_name = args["s_name"]
        s_rating = args.get("s_rating", None)
        s_tags = args.get("s_tags", None)
        s_time = args.get("s_time", None)
        s_venue = args["s_venue"]
        s_price = args["s_price"]

        is_venue = Venue.query.get(s_venue)

        if is_venue == None:

            abort(405, message=f"Venue with id {s_venue} doesn't exists!")

        any_show_with_same_time_in_same_venue = Show.query.filter_by(s_time=s_time,s_venue = s_venue).first()
        if any_show_with_same_time_in_same_venue:
            abort(410, message=f'A show named \'{any_show_with_same_time_in_same_venue.s_name}\' is already scheduled at time {s_time} in venue {s_venue} - {is_venue.v_name}. Please choose some other time slot.')

    

        new_show = Show(s_name=s_name, s_rating=s_rating,
                        s_tags=s_tags, s_time=s_time, s_price=s_price, s_venue=s_venue)

        db.session.add(new_show)
        db.session.commit()
        return new_show, 201


    @marshal_with(show_fields)
    def put(self, show_id):

        show = Show.query.filter_by(s_id=show_id).first()

        if show == None:
            abort(404, message="Show dosen't exists!")

        else:

            args = show_parser.parse_args()
            s_name = args["s_name"]
            s_rating = args.get("s_rating", None)
            s_tags = args.get("s_tags", None)
            s_time = args.get("s_time", None)
            s_venue = args["s_venue"]
            s_price = args["s_price"]

            is_venue = Venue.query.get(s_venue)

            if is_venue == None:

                abort(405, message=f"Venue with id {s_venue} doesn't exists!")


            any_show_with_same_time_in_same_venue = Show.query.filter_by(s_time=s_time,s_venue = s_venue).first()
            if any_show_with_same_time_in_same_venue and any_show_with_same_time_in_same_venue.s_id != show_id:
                abort(409, message=f'A show named \'{any_show_with_same_time_in_same_venue.s_name}\' is already scheduled at time {s_time} in venue {s_venue} - {any_show_with_same_time_in_same_venue.which_venue.v_name}. Please choose some other time slot.')

            show.s_name = s_name
            show.s_rating = s_rating
            show.s_tags = s_tags
            show.s_time = s_time
            show.s_venue = s_venue
            show.s_price = s_price

            db.session.commit()

            return show, 201


'''------------------  Venue API  --------------------'''


class VenueApi(Resource):

    # CRUD operations

    @marshal_with(venue_fields)
    def get(self, venue_id):

        venue = Venue.query.filter_by(v_id=venue_id).first()

        if venue:
            # venue exists in database, hence return the venue object which will be marshalled to json
            return venue, 200
        else:
            abort(404, message="Venue dosen't exists!")

    def delete(self, venue_id):

        venue = Venue.query.filter_by(v_id=venue_id).first()

        if venue:
            db.session.delete(venue)
            db.session.commit()
            return "Successfully deleted", 200
        else:
            abort(404, message="Venue dosen't exists!")

    @marshal_with(venue_fields)
    def post(self):

        # Getting the data from the request body
        args = venue_parser.parse_args()
        name = args["v_name"]

        venue_present = Venue.query.filter_by(v_name=name).first()

        if venue_present is not None:
            abort(
                409, message=f"Venue with name '{name}' already exists. Venue names must be unique.")

        place = args["v_place"]
        location = args["v_location"]
        capacity = args["v_capacity"]

        new_venue = Venue(v_name=name, v_place=place,
                          v_location=location, v_capacity=capacity)
        db.session.add(new_venue)
        db.session.commit()

        return new_venue, 201

    @marshal_with(venue_fields)
    def put(self, venue_id):

        venue = Venue.query.filter_by(v_id=venue_id).first()

        if venue == None:
            abort(404, message="Venue dosen't exists!")

        else:

            args = venue_parser.parse_args()
            name = args["v_name"]

            venue_present = Venue.query.filter_by(v_name=name).first()

            if venue_present is not None and venue_present.v_id != venue_id:
                abort(
                    409, message=f"Venue with name '{name}' already exists. Venue names must be unique.")

            place = args["v_place"]
            location = args["v_location"]
            capacity = args["v_capacity"]

            venue.v_name = name
            venue.v_place = place
            venue.v_location = location
            venue.v_capacity = capacity

            db.session.commit()

            return venue, 201


'''------------------  Other APIs --------------------'''


class ShowDisplayApi(Resource):

    def get(self, show_id):

        return redirect(f'/api/venue/{show_id}/display')

        show = Show.query.filter_by(s_id=show_id).first()

        if show:

            avg_rating = Ratings.query.filter_by(s_id=show_id).with_entities(
                func.avg(Ratings.r_score)).scalar()

            return redirect('/admin/dashboard')
            return render_template('api_show_page.html', show_details=show, avg_rating_score=avg_rating)
        else:
            return '<h2>Show dosen\'t exists.</h2>'


class VenueDisplayApi(Resource):

    def get(self, venue_id):

        return redirect(f'/api/venue/{venue_id}/display')

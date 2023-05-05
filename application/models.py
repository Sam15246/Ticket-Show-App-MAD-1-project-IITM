# from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from .database import db
# db = SQLAlchemy()


class Admin(db.Model):
    admin_id = db.Column(db.Integer, primary_key=True)
    a_username = db.Column(db.String(50), unique=True)
    a_password = db.Column(db.String(50), nullable=False)


class User(db.Model):
    user_id = db.Column(db.Integer, primary_key=True)
    u_username = db.Column(db.String(50), unique=True)
    u_password = db.Column(db.String(50), nullable=False)
    u_email = db.Column(db.String(50))
    is_admin = db.Column(db.Boolean, nullable=True)

    # 1 - n relationship b/w user and bookings
    u_bookings = db.relationship(
        "Booking", backref="which_user", cascade="all, delete")

    # 1 - n relationship b/w user and Ratings
    u_ratings = db.relationship(
        "Ratings", backref="which_user", cascade="all, delete")


class Venue(db.Model):

    v_id = db.Column(db.Integer, primary_key=True)
    v_name = db.Column(db.String(50),unique=True, nullable=False)
    v_place = db.Column(db.String(50), nullable=False)
    v_location = db.Column(db.String(50))
    v_capacity = db.Column(db.Integer, nullable=False)

    admin_id = db.Column(db.Integer, db.ForeignKey(
        'admin.admin_id'), default=1)

    # 1 - n relationship b/w venue and shows
    v_shows = db.relationship(
        "Show", backref="which_venue", cascade="all, delete")

    def __repr__(self):
        return f"<Venue {self.v_name}>"


class Show(db.Model):
    s_id = db.Column(db.Integer, primary_key=True)
    s_name = db.Column(db.String(50), nullable=False)
    seats_booked = db.Column(db.Integer, default=0)
    s_rating = db.Column(db.String(6), nullable=True)
    s_tags = db.Column(db.String(100), nullable=True)
    s_price = db.Column(db.Integer, nullable=False)
    s_time = db.Column(db.String, nullable = False)
    s_venue = db.Column(db.Integer, db.ForeignKey('venue.v_id'), nullable=False)

    admin_id = db.Column(db.Integer, db.ForeignKey(
        'admin.admin_id'), default=1)
    
    # __table_args__ = (db.UniqueConstraint('s_name', 's_time'),)

    # 1 - n relationship b/w show(event) and bookings
    s_bookings = db.relationship(
        "Booking", backref="which_show", cascade="all, delete")

    # 1 - n relationship b/w show(event) and Ratings
    s_ratings = db.relationship(
        "Ratings", backref="which_show", cascade="all, delete")

    def __repr__(self):
        return f"<Show {self.s_name}>"


class Ratings(db.Model):

    __tablename__ = 'ratings'
    r_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable = False)
    s_id = db.Column(db.Integer, db.ForeignKey('show.s_id'))
    r_score = db.Column(db.Float, default = 0)
    r_date = db.Column(db.DateTime, default=datetime.utcnow())

    # __table_args__ = (db.UniqueConstraint('user_id', 's_id'),)

    def __repr__(self):
        return f"<Rating {self.r_id}>"


class Booking(db.Model):
    booking_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey(
        'user.user_id'), nullable=False)
    v_id = db.Column(db.Integer, db.ForeignKey('venue.v_id'), nullable=False)
    s_id = db.Column(db.Integer, db.ForeignKey('show.s_id'), nullable=False)
    no_of_tickets = db.Column(db.Integer, default=1)

    b_date = db.Column(db.Date)
    b_time = db.Column(db.Time)
    b_cost = db.Column(db.Float)

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config.from_pyfile('config.py')
db = SQLAlchemy(app)


class Owner(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), unique=True)
    emails = db.relationship('OwnerEmail', backref=db.backref('owner', lazy='joined'), lazy='joined')
    # person_points = db.relationship('PersonalPoint', backref='owner', lazy='dynamic')
    # trips = db.relationship('Trip', backref='owner', lazy=True)

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return "Owner(%s) - ID(%s)" % (self.name, self.id)


class OwnerEmail(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    owner_email = db.Column(db.String(45), nullable=False, unique=True)
    access_level = db.Column(db.Integer, nullable=False, server_default='2')
    owner_id = db.Column(db.Integer, db.ForeignKey('owner.id'), nullable=False)

    def __init__(self, owner_email, owner, **kwargs):
        self.owner_email = owner_email
        self.owner = owner
        if 'access_level' in kwargs:
            self.access_level = kwargs['access_level']

    def __repr__(self):
        return "Email(%s) - ID(%s) - Owner(%s)" % (self.owner_email, self.id, self.owner)


class Resort(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), unique=True, nullable=False)
    bookable_rooms = db.relationship('BookableRoom', backref=db.backref('resort', lazy='joined'), lazy='joined')


class RoomType(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), unique=True, nullable=False)
    sleeps = db.Column(db.Integer, nullable=True)
    bookable_rooms = db.relationship('BookableRoom', backref=db.backref('room_type', lazy='joined'), lazy='joined')


class BookableRoom(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    resort_id = db.Column(db.Integer, db.ForeignKey('resort.id'), nullable=False)
    room_type_id = db.Column(db.Integer, db.ForeignKey('room_type.id'), nullable=False)
    # trips = db.relationship('Trip', backref='bookable_room', lazy='joined')

    def __repr__(self):
        return "Bookable Room = %s at %s" % (self.room_type.name, self.resort.name)


class PersonalPoint(db.Model):
    id = db.Column(db.Integer, unique=True, nullable=False, primary_key=False, autoincrement=True)
    use_year = db.Column(db.DateTime, primary_key=True)
    point_number = db.Column(db.Integer, primary_key=True, autoincrement=False)
    owner_id = db.Column(db.Integer, db.ForeignKey('owner.id'), primary_key=True)
    # trip_id = db.Column(db.Integer, db.ForeignKey('trip.id'))

    def __init__(self, use_year, point_number, owner_id):
        self.use_year = use_year
        self.point_number = point_number
        self.owner_id = owner_id


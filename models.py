from marshmallow import fields, pre_load
from marshmallow import validate
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from sqlalchemy.sql import func

db = SQLAlchemy()
ma = Marshmallow()

google_id = "test@test.com"

class AddUpdateDelete():
    def add(self, resource, log=""):
        db.session.add(resource)
        if log.__len__() > 0:
            db.session.add(EventLogger(google_id, log))
        return db.session.commit()

    def update(self, log=""):
        if log.__len__() > 0:
            db.session.add(EventLogger(google_id, log))
        return db.session.commit()

    def delete(self, resource, log=""):
        db.session.delete(resource)
        if log.__len__() > 0:
            db.session.add(EventLogger(google_id, log))
        return db.session.commit()


def EventLogger(google_id, description):
    new_event = EventLog()
    new_event.google_id = google_id
    new_event.description = description
    return new_event

class Owner(db.Model, AddUpdateDelete):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), unique=True)
    emails = db.relationship('OwnerEmail', backref='owner', lazy='dynamic')
    person_points = db.relationship('PersonalPoint', backref='owner', lazy='dynamic')
    trips = db.relationship('Trip', backref='owner', lazy='dynamic')

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return "Owner(%s) - ID(%s)" % (self.name, self.id)


class OwnerEmail(db.Model, AddUpdateDelete):
    id = db.Column(db.Integer, primary_key=True)
    owner_email = db.Column(db.String(45), nullable=False, unique=True)
    access_level = db.Column(db.Integer,nullable=False, server_default='2')
    owner_id = db.Column(db.Integer, db.ForeignKey('owner.id'), nullable=False)

    def __init__(self, owner_email, owner, **kwargs):
        self.owner_email = owner_email
        self.owner = owner
        if 'access_level' in kwargs:
            self.access_level = kwargs['access_level']

    def __repr__(self):
        return "Email(%s) - ID(%s) - Owner(%s)" % (self.owner_email, self.id, self.owner)


class Resort(db.Model, AddUpdateDelete):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), unique=True, nullable=False)
    bookable_rooms = db.relationship('BookableRoom', backref='resort')

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return "Resort(%s) - ID(%s)" % (self.name, self.id)


class RoomType(db.Model, AddUpdateDelete):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), unique=True, nullable=False)
    sleeps = db.Column(db.Integer, nullable=True)
    bookable_rooms = db.relationship('BookableRoom', backref='room_type')

    def __init__(self, name, **kwargs):
        self.name = name
        if 'sleeps' in kwargs:
            self.sleeps = kwargs['sleeps']

    def __repr__(self):
        return "Room Type(%s) - ID(%s) - Sleeps(%s)" % (self.name, self.id, self.sleeps)


class BookableRoom(db.Model, AddUpdateDelete):
    id = db.Column(db.Integer, primary_key=True)
    resort_id = db.Column(db.Integer, db.ForeignKey('resort.id'), nullable=False)
    room_type_id = db.Column(db.Integer, db.ForeignKey('room_type.id'), nullable=False)
    trips = db.relationship('Trip', backref='bookable_room', lazy='dynamic')

    def __init__(self, resort, room_type):
        self.resort = resort
        self.room_type = room_type

    def __repr__(self):
        return "Bookable Room = %s at %s" %(self.room_type.name, self.resort.name)


class ActualPoint(db.Model, AddUpdateDelete):
    id = db.Column(db.Integer, unique=True, nullable=False, primary_key=False, autoincrement=True)
    use_year = db.Column(db.DateTime, primary_key=True)
    point_number = db.Column(db.Integer, primary_key=True, autoincrement=False)
    trip_id = db.Column(db.Integer, db.ForeignKey('trip.id'))
    banked_date = db.Column(db.DateTime)

    def __init__(self, use_year, point_number):
        self.use_year = use_year
        self.point_number = point_number

    def __repr__(self):
        return "Actual point %s-%s - ID(%s)" %(self.use_year, self.point_number, self.id)


class PersonalPoint(db.Model, AddUpdateDelete):
    id = db.Column(db.Integer, unique=True, nullable=False, primary_key=False, autoincrement=True)
    use_year = db.Column(db.DateTime, primary_key=True)
    point_number = db.Column(db.Integer, primary_key=True, autoincrement=False)
    owner_id = db.Column(db.Integer, db.ForeignKey('owner.id'), primary_key=True)
    trip_id = db.Column(db.Integer, db.ForeignKey('trip.id'))

    def __init__(self, use_year, point_number, owner_id):
        self.use_year = use_year
        self.point_number = point_number
        self.owner_id = owner_id

    def __repr__(self):
        return "Person point %s-%s-%s - ID(%s)" % (self.use_year, self.point_number, self.owner.name, self.id)


class Trip(db.Model, AddUpdateDelete):
    id = db.Column(db.Integer, primary_key=True)
    check_in_date = db.Column(db.DateTime, nullable=False)
    check_out_date = db.Column(db.DateTime, nullable=False)
    notes = db.Column(db.String(255))
    bookable_room_id = db.Column(db.Integer, db.ForeignKey('bookable_room.id'), nullable=False)
    owner_id = db.Column(db.Integer, db.ForeignKey('owner.id'), nullable=False)
    booked_date = db.Column(db.DateTime, nullable=False)
    points_needed = db.Column(db.Integer, nullable=False)


class EventLog(db.Model, AddUpdateDelete):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, server_default=func.now(), nullable=False)
    google_id = db.Column(db.String(45), nullable=False)
    description = db.Column(db.String(4095), nullable=False)



class OwnerSchema(ma.Schema):
    id = fields.Integer(dump_only=True)
    url = ma.URLFor('api.ownerresource', id='<id>', _external=True)
    name = fields.String(required=True, validate=validate.Length(3))
    emails = fields.Nested('OwnerEmailSchema', many=True, exclude=('owner',))


class OwnerEmailSchema(ma.Schema):
    id = fields.Integer(dump_only=True)
    url = ma.URLFor('api.owneremailresource', id='<id>', _external=True)
    owner_email = fields.String(required=True, validate=validate.Email())
    access_level = fields.Integer()
    owner = fields.Nested('OwnerSchema', only=['id', 'name', 'url'], required=True)

    @pre_load
    def process_owner(self, data):
        owner = data.get('owner')
        if owner:
            if isinstance(owner, dict):
                owner_name = owner.get('name')
            else:
                owner_name = owner
            owner_dict = dict(name=owner_name)
        else:
            owner_dict = {}
        data['owner'] = owner_dict
        return data


class ResortSchema(ma.Schema):
    id = fields.Integer(dump_only=True)
    url = ma.URLFor('api.resortresource', id='<id>', _external=True)
    name = fields.String(required=True, validate=validate.Length(3))


class RoomTypeSchema(ma.Schema):
    id = fields.Integer(dump_only=True)
    url = ma.URLFor('api.roomtyperesource', id='<id>', _external=True)
    name = fields.String(required=True, validate=validate.Length(3))
    sleeps = fields.Integer(allow_none=True)


class BookableRoomSchema(ma.Schema):
    id = fields.Integer(dump_only=True)
    url = ma.URLFor('api.bookableroomresource', id='<id>', _external=True)
    resort = fields.Nested('ResortSchema', only=['id','name'], required=True)
    room_type = fields.Nested('RoomTypeSchema', only=['id','name'], required=True)


class ActualPointScheme(ma.Schema):
    id = fields.Integer(dump_only=True)
    url = ma.URLFor('api.actualpointresource', id='<id>', _external=True)
    use_year = fields.DateTime(required=True)
    point_number = fields.Integer(required=True)
    trip_id = fields.Integer()
    banked_date = fields.DateTime()


class PersonalPointSchema(ma.Schema):
    id = fields.Integer(dump_only=True)
    url = ma.URLFor('api.personalpointresource', id='<id>', _external=True)
    use_year = fields.DateTime(required=True)
    point_number = fields.Integer(required=True)
    owner = fields.Nested('OwnerSchema', only=['name'], required=True)
    trip_id = fields.Integer()


class TripSchema(ma.Schema):
    id = fields.Integer(dump_only=True)
    url = ma.URLFor('api.tripresource', id='<id>', _external=True)
    check_in_date = fields.DateTime(required=True)
    check_out_date = fields.DateTime(required=True)
    notes = fields.String(validate=validate.Length(max=4095))
    bookable_room = fields.Nested('BookableRoomSchema', only=['resort','room_type'], required=True)
    owner = fields.Nested('OwnerSchema', only=['name'], required=True)
    booked_date = fields.DateTime(required=True)
    points_needed = fields.Integer(required=True, validate=validate.Range(min=1))


class EventLogSchema(ma.Schema):
    id = fields.Integer(dump_only=True)
    url = ma.URLFor('api.eventlogresource', id='<id>', _external=True)
    timestamp = fields.DateTime(dump_only=True)
    google_id = fields.String(required=True)
    description = fields.String(required=True, validate=validate.Length(min=3))


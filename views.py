from flask import Blueprint, request, jsonify, make_response
from flask_restful import Api, Resource
from sqlalchemy.exc import SQLAlchemyError
from models import db, Owner, OwnerSchema, OwnerEmail, OwnerEmailSchema, Resort, ResortSchema, RoomType, RoomTypeSchema
from models import BookableRoom, BookableRoomSchema, ActualPoint, ActualPointScheme, PersonalPoint, PersonalPointSchema
from models import Trip, TripSchema, EventLogger
import status

api_bp = Blueprint('api', __name__)
owner_schema = OwnerSchema()
owner_email_schema = OwnerEmailSchema()
resort_schema = ResortSchema()
room_type_schema = RoomTypeSchema()
bookable_room_schema = BookableRoomSchema()
actual_point_schema = ActualPointScheme()
personal_point_schema = PersonalPointSchema()
trip_schema = TripSchema()
api = Api(api_bp)

google_id = "test@fallara.net"


class OwnerResource(Resource):
    def get(self, id):
        owner = Owner.query.get_or_404(id)
        result = owner_schema.dump(owner).data
        return result

    def put(self, id):
        owner = Owner.query.get_or_404(id)
        update_dict = request.get_json()
        if not update_dict:
            resp = {'message': 'No input data provided'}
            return resp, status.HTTP_400_BAD_REQUEST
        errors = owner_schema.validate(update_dict)
        if errors:
            return errors, status.HTTP_400_BAD_REQUEST
        try:
            if 'name' in update_dict:
                owner.name = update_dict['name']
            owner.update()
            return self.get(id)
        except SQLAlchemyError as e:
                db.session.rollback()
                resp = jsonify({"error": str(e)})
                resp.status_code = status.HTTP_400_BAD_REQUEST
                return resp

    def delete(self, id):
        owner = Owner.query.get_or_404(id)
        try:
            owner.delete(owner)
            return ('', status.HTTP_204_NO_CONTENT)
        except SQLAlchemyError as e:
                db.session.rollback()
                #resp = jsonify({"error": str(e)})
                resp = jsonify({"error": "Unable to delete owner"})
                resp.status_code = status.HTTP_401_UNAUTHORIZED
                return resp


class OwnerListResource(Resource):
    def get(self):
        owners = Owner.query.order_by(Owner.id).all()
        result = owner_schema.dump(owners, many=True).data
        return result

    def post(self):
        request_dict = request.get_json()
        if not request_dict:
            resp = {'message': 'No input data provided'}
            return resp, status.HTTP_400_BAD_REQUEST
        errors = owner_schema.validate(request_dict)
        if errors:
            return errors, status.HTTP_400_BAD_REQUEST
        try:
            owner = Owner(request_dict['name'])
            owner.add(owner)
            query = Owner.query.get(owner.id)
            result = owner_schema.dump(query).data
            return result, status.HTTP_201_CREATED
        except SQLAlchemyError as e:
            db.session.rollback()
            resp = jsonify({"error": str(e)})
            resp.status_code = status.HTTP_400_BAD_REQUEST
            return resp


class OwnerEmailResource(Resource):
    def get(self, id):
        owner_email = OwnerEmail.query.get_or_404(id)
        result = owner_email_schema.dump(owner_email).data
        return result

    def put(self, id):
        owner_email = OwnerEmail.query.get_or_404(id)
        update_dict = request.get_json()
        if not update_dict:
            resp = {'message': 'No input data provided'}
            return resp, status.HTTP_400_BAD_REQUEST
        if 'owner_email' in update_dict:
            owner_email.owner_email = update_dict['owner_email']
        if 'access_level' in update_dict:
            owner_email.access_level = update_dict['access_level']
        dumped_message, dump_errors = owner_email_schema.dump(owner_email)
        if dump_errors:
            return dump_errors, status.HTTP_400_BAD_REQUEST
        validate_errors = owner_email_schema.validate(dumped_message)
        if validate_errors:
            return validate_errors, status.HTTP_400_BAD_REQUEST
        try:
            owner_email.update()
            return self.get(id)
        except SQLAlchemyError as e:
            db.session.rollback()
            resp = jsonify({"error": str(e)})
            resp.status_code = status.HTTP_400_BAD_REQUEST
            return resp


    def delete(self, id):
        owner_email = OwnerEmail.query.get_or_404(id)
        try:
            owner_email.delete(owner_email)
            return ('', status.HTTP_204_NO_CONTENT)
        except SQLAlchemyError as e:
                db.session.rollback()
                resp = jsonify({"error": str(e)})
                resp.status_code = status.HTTP_401_UNAUTHORIZED
                return resp


class OwnerEmailListResource(Resource):
    def get(self):
        owner_emails = OwnerEmail.query.all()
        result = owner_email_schema.dump(owner_emails, many=True).data
        return result

    def post(self):
        request_dict = request.get_json()
        if not request_dict:
            resp = {'message': 'No input data provided'}
            return resp, status.HTTP_400_BAD_REQUEST
        errors = owner_email_schema.validate(request_dict)
        if errors:
            return errors, status.HTTP_400_BAD_REQUEST
        try:
            owner_name = request_dict['owner']['name']
            owner = Owner.query.filter_by(name=owner_name).first()
            if owner is None:
                # Owner does not exist
                resp = {'message': 'owner name does not exist'}
                return resp, status.HTTP_400_BAD_REQUEST
                # Now that we are sure we have an owner
                # create a new owner email
            owner_email = OwnerEmail(request_dict['owner_email'],owner)
            if 'access_level' in request_dict:
                owner_email.access_level = request_dict['access_level']
            owner_email.add(owner_email)
            query = OwnerEmail.query.get(owner_email.id)
            result = owner_email_schema.dump(query).data
            return result, status.HTTP_201_CREATED
        except SQLAlchemyError as e:
            db.session.rollback()
            resp = jsonify({"error": str(e)})
            resp.status_code = status.HTTP_400_BAD_REQUEST
            return resp


class ResortResource(Resource):
    def get(self, id):
        resort = Resort.query.get_or_404(id)
        result = resort_schema.dump(resort).data
        return result

    def put(self, id):
        resort = Resort.query.get_or_404(id)
        update_dict = request.get_json()
        if not update_dict:
            resp = {'message': 'No input data provided'}
            return resp, status.HTTP_400_BAD_REQUEST
        if 'name' in update_dict:
            resort.name = update_dict['name']
        dumped_message, dump_errors = resort_schema.dump(resort)
        if dump_errors:
            return dump_errors, status.HTTP_400_BAD_REQUEST
        validate_errors = resort_schema.validate(dumped_message)
        if validate_errors:
            return validate_errors, status.HTTP_400_BAD_REQUEST
        try:
            resort.update(log = "UPDATE " + resort.__repr__())
            return self.get(id)
        except SQLAlchemyError as e:
            db.session.rollback()
            resp = jsonify({"error": str(e)})
            resp.status_code = status.HTTP_400_BAD_REQUEST
            return resp

    def delete(self, id):
        resort = Resort.query.get_or_404(id)
        try:
            resort.delete(resort, log="DELETE - " + resort.__repr__())
            return ('', status.HTTP_204_NO_CONTENT)
        except SQLAlchemyError as e:
                db.session.rollback()
                resp = jsonify({"error": str(e)})
                resp.status_code = status.HTTP_401_UNAUTHORIZED
                return resp


class ResortListResource(Resource):
    def get(self):
        resort = Resort.query.all()
        result = resort_schema.dump(resort, many=True).data
        return result

    def post(self):
        request_dict = request.get_json()
        if not request_dict:
            resp = {'message': 'No input data provided'}
            return resp, status.HTTP_400_BAD_REQUEST
        errors = resort_schema.validate(request_dict)
        if errors:
            return errors, status.HTTP_400_BAD_REQUEST
        try:
            resort = Resort(request_dict['name'])
            resort.add(resort)
            resort.add(EventLogger(google_id, "ADD "+resort.__repr__()))
            query = Resort.query.get(resort.id)
            result = resort_schema.dump(query).data
            return result, status.HTTP_201_CREATED
        except SQLAlchemyError as e:
            db.session.rollback()
            resp = jsonify({"error": str(e)})
            resp.status_code = status.HTTP_400_BAD_REQUEST
            return resp


class RoomTypeResource(Resource):
    
    def get(self, id):
        room_type = RoomType.query.get_or_404(id)
        result = room_type_schema.dump(room_type).data
        return result

    def put(self, id):
        room_type = RoomType.query.get_or_404(id)
        update_dict = request.get_json()
        if not update_dict:
            resp = {'message': 'No input data provided'}
            return resp, status.HTTP_400_BAD_REQUEST
        if 'name' in update_dict:
            room_type.name = update_dict['name']
        if 'sleeps' in update_dict:
            room_type.sleeps = update_dict['sleeps']
        dumped_message, dump_errors = room_type_schema.dump(room_type)
        if dump_errors:
            return dump_errors, status.HTTP_400_BAD_REQUEST
        validate_errors = room_type_schema.validate(dumped_message)
        if validate_errors:
            return validate_errors, status.HTTP_400_BAD_REQUEST
        try:
            room_type.update(log="UPDATE - " + room_type.__repr__())
            return self.get(id)
        except SQLAlchemyError as e:
            db.session.rollback()
            resp = jsonify({"error": str(e)})
            resp.status_code = status.HTTP_400_BAD_REQUEST
            return resp
    
    def delete(self, id):
        room_type = RoomType.query.get_or_404(id)
        try:
            room_type.delete(room_type, log = "DELETE - " + room_type.__repr__())
            return ('', status.HTTP_204_NO_CONTENT)
        except SQLAlchemyError as e:
                db.session.rollback()
                resp = jsonify({"error": str(e)})
                resp.status_code = status.HTTP_401_UNAUTHORIZED
                return resp


class RoomTypeListResource(Resource):

    def get(self):
        room_type = RoomType.query.all()
        result = room_type_schema.dump(room_type, many=True).data
        return result

    def post(self):
        request_dict = request.get_json()
        if not request_dict:
            resp = {'message': 'No input data provided'}
            return resp, status.HTTP_400_BAD_REQUEST
        errors = room_type_schema.validate(request_dict)
        if errors:
            return errors, status.HTTP_400_BAD_REQUEST
        try:
            room_type = RoomType(request_dict['name'])
            if 'sleeps' in request_dict:
                room_type.sleeps = request_dict['sleeps']
            room_type.add(room_type)
            room_type.add(EventLogger(google_id, "ADD - "+room_type.__repr__()))
            query = RoomType.query.get(room_type.id)
            result = room_type_schema.dump(query).data
            return result, status.HTTP_201_CREATED
        except SQLAlchemyError as e:
            db.session.rollback()
            resp = jsonify({"error": str(e)})
            resp.status_code = status.HTTP_400_BAD_REQUEST
            return resp


class BookableRoomResource(Resource):
    
    def get(self, id):
        bookable_room = BookableRoom.query.get_or_404(id)
        result = bookable_room_schema.dump(bookable_room).data
        return result

    def put(self, id):
        bookable_room = BookableRoom.query.get_or_404(id)
        update_dict = request.get_json()
        if not update_dict:
            resp = {'message': 'No input data provided'}
            return resp, status.HTTP_400_BAD_REQUEST
        if 'resort' in update_dict:
            resort_name = update_dict['resort']['name']
            resort = Resort.query.filter_by(name=resort_name).first()
            if resort is None:
                # Resort does not exist
                resp = {'message': 'resort name does not exist'}
                return resp, status.HTTP_400_BAD_REQUEST
            bookable_room.resort = resort
        if 'room_type' in update_dict:
            room_type_name = update_dict['room_type']['name']
            room_type = RoomType.query.filter_by(name=room_type_name).first()
            if room_type is None:
                # Resort does not exist
                resp = {'message': 'room type name does not exist'}
                return resp, status.HTTP_400_BAD_REQUEST
            bookable_room.room_type = room_type
        dumped_message, dump_errors = bookable_room_schema.dump(bookable_room)
        if dump_errors:
            return dump_errors, status.HTTP_400_BAD_REQUEST
        validate_errors = bookable_room_schema.validate(dumped_message)
        if validate_errors:
            return validate_errors, status.HTTP_400_BAD_REQUEST
        try:
            bookable_room.update(log="UPDATE - " + bookable_room.__repr__())
            return self.get(id)
        except SQLAlchemyError as e:
            db.session.rollback()
            resp = jsonify({"error": str(e)})
            resp.status_code = status.HTTP_400_BAD_REQUEST
            return resp

    def delete(self, id):
        bookable_room = BookableRoom.query.get_or_404(id)
        try:
            bookable_room.delete(bookable_room, log="DELETE" + bookable_room.__repr__() )
            return ('', status.HTTP_204_NO_CONTENT)
        except SQLAlchemyError as e:
            db.session.rollback()
            resp = jsonify({"error": str(e)})
            resp.status_code = status.HTTP_401_UNAUTHORIZED
            return resp


class BookableRoomListResource(Resource):
    def get(self):
        bookable_room = BookableRoom.query.all()
        result = bookable_room_schema.dump(bookable_room, many=True).data
        return result

    def post(self):
        request_dict = request.get_json()
        if not request_dict:
            resp = {'message': 'No input data provided'}
            return resp, status.HTTP_400_BAD_REQUEST
        errors = bookable_room_schema.validate(request_dict)
        if errors:
            return errors, status.HTTP_400_BAD_REQUEST
        try:
            resort_name = request_dict['resort']['name']
            resort = Resort.query.filter_by(name=resort_name).first()
            if resort is None:
                # Resort does not exist
                resp = {'message': 'resort name does not exist'}
                return resp, status.HTTP_400_BAD_REQUEST
            room_type_name = request_dict['room_type']['name']
            room_type = RoomType.query.filter_by(name=room_type_name).first()
            if room_type is None:
                # Room Type does not exist
                resp = {'message': 'room type name does not exist'}
                return resp, status.HTTP_400_BAD_REQUEST
            bookable_room = BookableRoom(resort, room_type)
            bookable_room.add(bookable_room)
            bookable_room.add(EventLogger(google_id, "ADD - "+bookable_room.__repr__()))
            query = BookableRoom.query.get(bookable_room.id)
            result = bookable_room_schema.dump(query).data
            return result, status.HTTP_201_CREATED
        except SQLAlchemyError as e:
            db.session.rollback()
            resp = jsonify({"error": str(e)})
            resp.status_code = status.HTTP_400_BAD_REQUEST
            return resp


class ActualPointResource(Resource):

    def get(self, id):
        actual_point = ActualPoint.query.get_or_404(id)
        result = actual_point_schema.dump(actual_point).data
        return result


class ActualPointListResource(Resource):

    def get(self):
        actual_point = ActualPoint.query.all()
        result = actual_point_schema.dump(actual_point, many=True).data
        return result


class PersonalPointResource(Resource):

    def get(self, id):
        personal_point = PersonalPoint.query.get_or_404(id)
        result = personal_point_schema.dump(personal_point).data
        return result


class PersonalPointListResource(Resource):

    def get(self):
        personal_point = PersonalPoint.query.all()
        result = personal_point_schema.dump(personal_point, many=True).data
        return result


class TripResource(Resource):

    def get(self, id):
        trip = Trip.query.get_or_404(id)
        result = trip_schema.dump(trip).data
        return result


class TripListResource(Resource):
    def get(self):
        trip = Trip.query.all()
        result = trip_schema.dump(trip, many=True).data
        return result


api.add_resource(OwnerResource, '/owners/<int:id>')
api.add_resource(OwnerListResource, '/owners/')
api.add_resource(OwnerEmailResource, '/owner_emails/<int:id>')
api.add_resource(OwnerEmailListResource, '/owner_emails/')
api.add_resource(ResortResource, '/resorts/<int:id>')
api.add_resource(ResortListResource, '/resorts/')
api.add_resource(RoomTypeResource, '/room_types/<int:id>')
api.add_resource(RoomTypeListResource, '/room_types/')
api.add_resource(BookableRoomResource, '/bookable_rooms/<int:id>')
api.add_resource(BookableRoomListResource, '/bookable_rooms/')
api.add_resource(ActualPointResource, '/actual_points/<int:id>')
api.add_resource(ActualPointListResource, '/actual_points/')
api.add_resource(PersonalPointResource, '/personal_points/<int:id>')
api.add_resource(PersonalPointListResource, '/personal_points/')
api.add_resource(TripResource, '/trips/<int:id>')
api.add_resource(TripListResource, '/trips/')

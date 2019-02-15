from flask import request, jsonify
from flask_restful import Resource
from sqlalchemy.exc import SQLAlchemyError
from models import db, Resort, ResortSchema, RoomType, RoomTypeSchema, BookableRoom, BookableRoomSchema, EventLogger
from flask_jwt_extended import jwt_required
import status


google_id = "test@fallara.net"

resort_schema = ResortSchema()
room_type_schema = RoomTypeSchema()
bookable_room_schema = BookableRoomSchema()


class ResortResource(Resource):
    @jwt_required
    def get(self, id):
        resort = Resort.query.get_or_404(id)
        result = resort_schema.dump(resort).data
        return result

    @jwt_required
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
            resort.update(log="UPDATE " + resort.__repr__())
            return self.get(id)
        except SQLAlchemyError as e:
            db.session.rollback()
            resp = jsonify({"error": str(e)})
            resp.status_code = status.HTTP_400_BAD_REQUEST
            return resp

    @jwt_required
    def delete(self, id):
        resort = Resort.query.get_or_404(id)
        try:
            resort.delete(resort, log="DELETE - " + resort.__repr__())
            return None, status.HTTP_200_OK
        except SQLAlchemyError as e:
            db.session.rollback()
            resp = jsonify({"error": str(e)})
            resp.status_code = status.HTTP_401_UNAUTHORIZED
            return resp


class ResortListResource(Resource):
    @jwt_required
    def get(self):
        resort = Resort.query.order_by(Resort.name).all()
        result = resort_schema.dump(resort, many=True).data
        return result

    @jwt_required
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
            resort.add(EventLogger(google_id, "ADD "+ resort.__repr__()))
            query = Resort.query.get(resort.id)
            result = resort_schema.dump(query).data
            return result, status.HTTP_201_CREATED
        except SQLAlchemyError as e:
            db.session.rollback()
            resp = jsonify({"error": str(e)})
            resp.status_code = status.HTTP_400_BAD_REQUEST
            return resp


class RoomTypeResource(Resource):
    @jwt_required
    def get(self, id):
        room_type = RoomType.query.get_or_404(id)
        result = room_type_schema.dump(room_type).data
        return result

    @jwt_required
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

    @jwt_required
    def delete(self, id):
        room_type = RoomType.query.get_or_404(id)
        try:
            room_type.delete(room_type, log="DELETE - " + room_type.__repr__())
            return None, status.HTTP_200_OK
        except SQLAlchemyError as e:
            db.session.rollback()
            resp = jsonify({"error": str(e)})
            resp.status_code = status.HTTP_401_UNAUTHORIZED
            return resp


class RoomTypeListResource(Resource):
    @jwt_required
    def get(self):
        room_type = RoomType.query.order_by(RoomType.name).all()
        result = room_type_schema.dump(room_type, many=True).data
        return result

    @jwt_required
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
            room_type.add(EventLogger(google_id, "ADD - " + room_type.__repr__()))
            query = RoomType.query.get(room_type.id)
            result = room_type_schema.dump(query).data
            return result, status.HTTP_201_CREATED
        except SQLAlchemyError as e:
            db.session.rollback()
            resp = jsonify({"error": str(e)})
            resp.status_code = status.HTTP_400_BAD_REQUEST
            return resp


class BookableRoomResource(Resource):
    @jwt_required
    def get(self, id):
        bookable_room = BookableRoom.query.get_or_404(id)
        result = bookable_room_schema.dump(bookable_room).data
        return result

    @jwt_required
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

    @jwt_required
    def delete(self, id):
        bookable_room = BookableRoom.query.get_or_404(id)
        try:
            bookable_room.delete(bookable_room, log="DELETE" + bookable_room.__repr__())
            return None, status.HTTP_200_OK
        except SQLAlchemyError as e:
            db.session.rollback()
            resp = jsonify({"error": str(e)})
            resp.status_code = status.HTTP_401_UNAUTHORIZED
            return resp


class BookableRoomListResource(Resource):
    @jwt_required
    def get(self):
        bookable_room = BookableRoom.query.all()
        result = bookable_room_schema.dump(bookable_room, many=True).data
        return result

    @jwt_required
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
            bookable_room.add(EventLogger(google_id, "ADD - " + bookable_room.__repr__()))
            query = BookableRoom.query.get(bookable_room.id)
            result = bookable_room_schema.dump(query).data
            return result, status.HTTP_201_CREATED
        except SQLAlchemyError as e:
            db.session.rollback()
            resp = jsonify({"error": str(e)})
            resp.status_code = status.HTTP_400_BAD_REQUEST
            return resp

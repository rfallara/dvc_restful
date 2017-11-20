from flask import request
from flask_restful import Resource
from models import Trip, TripSchema, Owner, BookableRoom, Resort
import status

trip_schema = TripSchema()


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

    def post(self):
        request_dict = request.get_json()
        if not request_dict:
            resp = {'message': 'No input data provided'}
            return resp, status.HTTP_400_BAD_REQUEST
        errors = trip_schema.validate(request_dict)
        if errors:
            return errors, status.HTTP_400_BAD_REQUEST
        else :
            # create a new trip object and validate data
            new_trip = Trip()
            trip_owner = Owner.query.filter_by(name=request_dict['owner']['name']).first()
            if trip_owner is None:
                # Resort does not exist
                resp = {'message': 'owner does not exist'}
                return resp, status.HTTP_400_BAD_REQUEST
            new_trip.owner_id = trip_owner.id
            trip_bookable_room = BookableRoom.query. \
                filter(BookableRoom.resort.has(name=request_dict['bookable_room']['resort']['name'])). \
                filter(BookableRoom.room_type.has(name=request_dict['bookable_room']['room_type']['name'])).first()
            if trip_bookable_room is None:
                # Resort does not exist
                resp = {'message': 'bookable room does not exist'}
                return resp, status.HTTP_400_BAD_REQUEST
            new_trip.bookable_room_id = trip_bookable_room.id
            new_trip.check_in_date = request_dict['check_in_date']
            new_trip.check_out_date = request_dict['check_out_date']
            if new_trip.check_in_date >= new_trip.check_out_date:
                resp = {'message': 'check out must be after check in date'}
                return resp, status.HTTP_400_BAD_REQUEST
            new_trip.booked_date = request_dict['booked_date']
            new_trip.notes = request_dict['notes']
            new_trip.points_needed = request_dict['points_needed']
            if new_trip.points_needed < 0:
                resp = {'message': 'points needed must be at least 1'}
                return resp, status.HTTP_400_BAD_REQUEST


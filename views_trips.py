from flask import request, jsonify
from sqlalchemy.exc import SQLAlchemyError
from flask_restful import Resource
from models import Trip, TripSchema, Owner, BookableRoom
import status
from flask_jwt_extended import jwt_required
from dateutil.relativedelta import *
from datetime import datetime
from models import db, PersonalPoint, ActualPoint, EventLogger
from sqlalchemy import or_

trip_schema = TripSchema()


class TripResource(Resource):
    @jwt_required
    def get(self, trip_id):
        trip = Trip.query.get_or_404(trip_id)
        result = trip_schema.dump(trip).data
        return result

    @jwt_required
    def delete(self, trip_id: int):
        trip: Trip = db.session.query(Trip).get_or_404(trip_id)
        personal_points: PersonalPoint = db.session.query(PersonalPoint).filter_by(trip_id=trip_id).all()
        for point in personal_points:
            point.trip_id = None
        actual_points: ActualPoint = db.session.query(ActualPoint).filter_by(trip_id=trip_id).all()
        for point in actual_points:
            point.trip_id = None
        try:
            db.session.add(EventLogger('test@fallara.net', 'DELETE - ' + trip.__repr__()))
            db.session.delete(trip)
            db.session.commit()
            # trip.delete(trip, log='DELETE - ' + trip.__repr__())
            return None, status.HTTP_200_OK
        except SQLAlchemyError as e:
            db.session.rollback()
            resp = jsonify({"error": str(e)})
            resp.status_code = status.HTTP_401_UNAUTHORIZED
            return resp




class TripListResource(Resource):
    @jwt_required
    def get(self):
        trip = Trip.query.all()
        result = trip_schema.dump(trip, many=True).data
        return result

    @jwt_required
    def post(self):
        request_dict = request.get_json()
        if not request_dict:
            resp = {'message': 'No input data provided'}
            return resp, status.HTTP_400_BAD_REQUEST
        errors = trip_schema.validate(request_dict)
        if errors:
            return errors, status.HTTP_400_BAD_REQUEST
        else:
            # create a new trip object and validate data
            trip_owner = Owner.query.filter_by(name=request_dict['owner']['name']).first()
            if trip_owner is None:
                # owner does not exist
                resp = {'message': 'owner does not exist'}
                return resp, status.HTTP_400_BAD_REQUEST
            # new_trip.owner_id = trip_owner.id
            trip_bookable_room = BookableRoom.query. \
                filter(BookableRoom.resort.has(name=request_dict['bookable_room']['resort']['name'])). \
                filter(BookableRoom.room_type.has(name=request_dict['bookable_room']['room_type']['name'])).first()
            if trip_bookable_room is None:
                # Resort does not exist
                resp = {'message': 'bookable room does not exist'}
                return resp, status.HTTP_400_BAD_REQUEST
            # new_trip.bookable_room_id = trip_bookable_room.id
            new_trip = Trip(trip_owner, trip_bookable_room)
            # new_trip.check_in_date = request_dict['check_in_date']
            new_trip.check_in_date = datetime.strptime(request_dict['check_in_date'].split('T')[0], '%Y-%m-%d')
            # new_trip.check_out_date = request_dict['check_out_date']
            new_trip.check_out_date = datetime.strptime(request_dict['check_out_date'].split('T')[0], '%Y-%m-%d')
            if new_trip.check_in_date >= new_trip.check_out_date:
                resp = {'message': 'check out must be after check in date'}
                return resp, status.HTTP_400_BAD_REQUEST
            new_trip.booked_date = datetime.strptime(request_dict['booked_date'].split('T')[0], '%Y-%m-%d')
            # new_trip.booked_date = request_dict['booked_date']
            new_trip.notes = request_dict['notes']
            new_trip.points_needed = request_dict['points_needed']
            if new_trip.points_needed < 0:
                resp = {'message': 'points needed must be at least 1'}
                return resp, status.HTTP_400_BAD_REQUEST
        db.session.flush()

        # New trip is valid now try to allocate points

        current_use_year = new_trip.check_in_date
        previous_use_year = current_use_year+relativedelta(years=-1)
        next_use_year = current_use_year+relativedelta(years=1)
        previous_two_use_year = current_use_year+relativedelta(years=-2)
        booked_date = new_trip.booked_date

        personal_points_needed = new_trip.points_needed
        trip_owner_id = new_trip.owner_id
        # Find banked personal points
        personal_points_banked = db.session.query(PersonalPoint)\
            .filter(PersonalPoint.owner_id == trip_owner_id,
                    PersonalPoint.trip_id.is_(None),
                    PersonalPoint.use_year < previous_use_year)\
            .order_by("use_year").order_by("point_number")\
            .limit(personal_points_needed).all()

        for point in personal_points_banked:
            point.trip_id = new_trip.id

        personal_points_needed -= len(personal_points_banked)

        # IF more points needed look for current personal points
        if personal_points_needed > 0:

            personal_points_current = db.session.query(PersonalPoint)\
                .filter(PersonalPoint.use_year < current_use_year, PersonalPoint.use_year > previous_use_year)\
                .filter(PersonalPoint.owner_id == new_trip.owner_id)\
                .filter(PersonalPoint.trip_id.is_(None))\
                .order_by("use_year").order_by("point_number")\
                .limit(personal_points_needed).all()

            for point in personal_points_current:
                point.trip_id = new_trip.id

            personal_points_needed -= len(personal_points_current)
        else:
            personal_points_current = []

        # IF more points needed look for borrow personal points
        if personal_points_needed > 0:

            personal_points_borrow = db.session.query(PersonalPoint) \
                .filter(PersonalPoint.use_year < next_use_year, PersonalPoint.use_year > current_use_year) \
                .filter(PersonalPoint.owner_id == new_trip.owner_id) \
                .filter(PersonalPoint.trip_id.is_(None)) \
                .order_by("use_year").order_by("point_number") \
                .limit(personal_points_needed).all()

            for point in personal_points_borrow:
                point.trip_id = new_trip.id

            personal_points_needed -= len(personal_points_borrow)
        else:
            personal_points_borrow = []

        # IF more personal points requirement was satisfied
        if personal_points_needed > 0:
            print('Points needed - ' + str(new_trip.points_needed))
            print('Personal Banked Points - ' + str(len(personal_points_banked)))
            print('Personal Current Points - ' + str(len(personal_points_current)))
            print('Personal Borrow Points - ' + str(len(personal_points_borrow)))
            new_trip.delete(new_trip, "Removing Trip - Personal Points Short")
            resp = {'message': 'personal points shortage of %s points' % personal_points_needed}
            return resp, status.HTTP_400_BAD_REQUEST

        # FIND actual points
        actual_points_needed = new_trip.points_needed

        actual_points_banked = db.session.query(ActualPoint)\
            .filter(ActualPoint.use_year < previous_use_year, ActualPoint.use_year > previous_two_use_year)\
            .filter(ActualPoint.trip_id.is_(None))\
            .filter(ActualPoint.banked_date < booked_date) \
            .order_by("use_year").order_by("point_number") \
            .limit(actual_points_needed).all()

        for point in actual_points_banked:
            point.trip_id = new_trip.id

        actual_points_needed -= len(actual_points_banked)

        # IF actual points requirement is satisfied
        if actual_points_needed > 0:

            actual_points_current = db.session.query(ActualPoint)\
                .filter(ActualPoint.use_year < current_use_year, ActualPoint.use_year > previous_two_use_year)\
                .filter(ActualPoint.trip_id.is_(None))\
                .filter(or_(ActualPoint.banked_date.is_(None), ActualPoint.banked_date > booked_date)) \
                .order_by("use_year").order_by("point_number") \
                .limit(actual_points_needed).all()

            for point in actual_points_current:
                point.trip_id = new_trip.id

            actual_points_needed -= len(actual_points_current)
        else:
            actual_points_current = []

        # IF actual points requirement is satisfied
        if actual_points_needed > 0:

            actual_points_borrow = db.session.query(ActualPoint)\
                .filter(ActualPoint.use_year < next_use_year, ActualPoint.use_year > current_use_year)\
                .filter(ActualPoint.trip_id.is_(None))\
                .order_by("use_year").order_by("point_number")\
                .limit(actual_points_needed).all()

            for point in actual_points_borrow:
                point.trip_id = new_trip.id

            actual_points_needed -= len(actual_points_borrow)
        else:
            actual_points_borrow = []

        # IF more personal points requirement was satisfied
        if actual_points_needed > 0:
            print('Points needed - ' + str(new_trip.points_needed))
            print('Actual Banked Points - ' + str(len(actual_points_banked)))
            print('Actual Current Points - ' + str(len(actual_points_current)))
            print('Actual Borrow Points - ' + str(len(actual_points_borrow)))
            new_trip.delete(new_trip, "Removing Trip - Actual Point Short")
            resp = {'message': 'actual points shortage of %s points' % actual_points_needed}
            return resp, status.HTTP_400_BAD_REQUEST

        print('All points requirements satisfied, ok to book trip')
        print('Points needed - ' + str(new_trip.points_needed))
        print('Personal Banked Points - ' + str(len(personal_points_banked)))
        print('Personal Current Points - ' + str(len(personal_points_current)))
        print('Personal Borrow Points - ' + str(len(personal_points_borrow)))
        print('Actual Banked Points - ' + str(len(actual_points_banked)))
        print('Actual Current Points - ' + str(len(actual_points_current)))
        print('Actual Borrow Points - ' + str(len(actual_points_borrow)))

        # ALL is good commit to db and return success
        try:
            db.session.commit()
            result = trip_schema.dump(new_trip).data
            return result, status.HTTP_201_CREATED
        except SQLAlchemyError as e:
            db.session.rollback()
            resp = jsonify({"error": str(e)})
            resp.status_code = status.HTTP_400_BAD_REQUEST
            return resp

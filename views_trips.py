from flask import request
from flask_restful import Resource
from models import Trip, TripSchema, Owner, BookableRoom
import status
from flask_jwt_extended import jwt_required
from dateutil.relativedelta import *
from datetime import datetime
from models import db

trip_schema = TripSchema()


class TripResource(Resource):
    @jwt_required
    def get(self, id):
        trip = Trip.query.get_or_404(id)
        result = trip_schema.dump(trip).data
        return result


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
            new_trip = Trip()
            trip_owner = Owner.query.filter_by(name=request_dict['owner']['name']).first()
            if trip_owner is None:
                # owner does not exist
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
        # New trip is valid now check for available points
        current_use_year = datetime.strptime(new_trip.check_in_date.split('T')[0], '%Y-%m-%d')
        previous_use_year = current_use_year+relativedelta(years=-1)
        next_use_year = current_use_year+relativedelta(years=1)
        previous_two_use_year = current_use_year+relativedelta(years=-2)
        booked_date = datetime.strptime(new_trip.booked_date.split('T')[0], '%Y-%m-%d')

        located_personal_point_ids = []
        personal_points_needed = new_trip.points_needed
        count_banked_personal_points = 0
        count_current_personal_points = 0
        count_borrow_personal_points = 0

        # Find banked personal points

        select_qry = "SELECT trip_id, id, use_year, point_number, owner_id"\
                     " FROM personal_point"\
                     " WHERE ((use_year) < '%s' AND ((owner_id)='%s') AND ((trip_id) Is Null))"\
                     " ORDER BY use_year, point_number"\
                     " LIMIT %s" % (previous_use_year.strftime('%Y-%m-%d'),
                                    new_trip.owner_id,
                                    personal_points_needed)

        result = db.engine.execute(select_qry)
        for row in result:
            located_personal_point_ids.append(row['id'])
            count_banked_personal_points += 1

        personal_points_needed -= count_banked_personal_points

        # IF more points needed look for current personal points
        if personal_points_needed > 0:

            select_qry = "SELECT trip_id, id, use_year, point_number, owner_id"\
                         " FROM personal_point"\
                         " WHERE ((use_year) < '%s' And (use_year) > '%s')"\
                         " AND ((personal_point.owner_id)= '%s') AND ((trip_id) Is Null)"\
                         " ORDER BY use_year, point_number"\
                         " LIMIT %s" % (current_use_year,
                                        previous_use_year,
                                        new_trip.owner_id,
                                        personal_points_needed)
            result = db.engine.execute(select_qry)
            for row in result:
                located_personal_point_ids.append(row['id'])
                count_current_personal_points += 1

            personal_points_needed -= count_current_personal_points

        # IF more points needed look for borrow personal points
        if personal_points_needed > 0:

            select_qry = "SELECT trip_id, id, use_year, point_number, owner_id"\
                         " FROM personal_point "\
                         " WHERE (((use_year) < '%s' And (use_year) > '%s') AND ((owner_id) = '%s') AND ((trip_id) Is Null) ) "\
                         " ORDER BY use_year, point_number "\
                         " LIMIT %s" % (next_use_year,
                                        current_use_year,
                                        new_trip.owner_id,
                                        personal_points_needed)

            result = db.engine.execute(select_qry)
            for row in result:
                located_personal_point_ids.append(row['id'])
                count_borrow_personal_points += 1

            personal_points_needed -= count_borrow_personal_points

        # IF more personal points requirement was satisfied
        if personal_points_needed > 0:
            print('Points needed - ' + str(new_trip.points_needed))
            print('Personal Banked Points - ' + str(count_banked_personal_points))
            print('Personal Current Points - ' + str(count_current_personal_points))
            print('Personal Borrow Points - ' + str(count_borrow_personal_points))
            resp = {'message': 'personal points shortage of %s points' % personal_points_needed}
            return resp, status.HTTP_400_BAD_REQUEST

        # FIND actual points
        located_actual_point_ids = []
        actual_points_needed = new_trip.points_needed
        count_banked_actual_points = 0
        count_current_actual_points = 0
        count_borrow_actual_points = 0

        select_qry = "SELECT trip_id, id, use_year, point_number "\
                     " FROM actual_point "\
                     " WHERE (( use_year < '%s' And use_year > '%s') "\
                     " AND (trip_id Is Null) "\
                     " AND (banked_date < '%s') ) "\
                     " ORDER BY use_year, point_number "\
                     " LIMIT %s" % (previous_use_year,
                                    previous_two_use_year,
                                    booked_date,
                                    actual_points_needed)

        result = db.engine.execute(select_qry)
        for row in result:
            located_actual_point_ids.append(row['id'])
            count_banked_actual_points += 1

        actual_points_needed -= count_banked_actual_points

        # IF actual points requirement is satisfied
        if actual_points_needed > 0:
            select_qry = "SELECT trip_id, id, use_year, point_number"\
                         " FROM actual_point"\
                         " WHERE (((use_year) < '%s' And (use_year) > '%s') "\
                         " AND ((trip_id) Is Null) AND (banked_date Is Null Or banked_date > '%s')  )"\
                         " ORDER BY use_year, point_number"\
                         " LIMIT %s" % (current_use_year,
                                        previous_two_use_year,
                                        booked_date,
                                        actual_points_needed)
            result = db.engine.execute(select_qry)
            for row in result:
                located_actual_point_ids.append(row['id'])
                count_current_actual_points += 1

            actual_points_needed -= count_current_actual_points

        # IF actual points requirement is satisfied
        if actual_points_needed > 0:
            select_qry = "SELECT trip_id, id, use_year, point_number"\
                         " FROM actual_point"\
                         " WHERE (((use_year) < '%s' And (use_year) > '%s') "\
                         " AND ((trip_id) Is Null) )"\
                         " ORDER BY use_year, point_number"\
                         " LIMIT %s" % (next_use_year,
                                        current_use_year,
                                        actual_points_needed)
            result = db.engine.execute(select_qry)
            for row in result:
                located_actual_point_ids.append(row['id'])
                count_borrow_actual_points += 1

            actual_points_needed -= count_borrow_actual_points

        # IF more personal points requirement was satisfied
        if actual_points_needed > 0:
            print('Points needed - ' + str(new_trip.points_needed))
            print('Actual Banked Points - ' + str(count_banked_actual_points))
            print('Actual Current Points - ' + str(count_current_actual_points))
            print('Actual Borrow Points - ' + str(count_borrow_actual_points))
            resp = {'message': 'actual points shortage of %s points' % actual_points_needed}
            return resp, status.HTTP_400_BAD_REQUEST

        print('All points requirements satisfied, ok to book trip')
        print('Points needed - ' + str(new_trip.points_needed))
        print('Personal Banked Points - ' + str(count_banked_personal_points))
        print('Personal Current Points - ' + str(count_current_personal_points))
        print('Personal Borrow Points - ' + str(count_borrow_personal_points))
        print('Actual Banked Points - ' + str(count_banked_actual_points))
        print('Actual Current Points - ' + str(count_current_actual_points))
        print('Actual Borrow Points - ' + str(count_borrow_actual_points))

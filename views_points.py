from flask_restful import Resource, reqparse
from flask import jsonify, request
from models import db, ActualPoint, ActualPointScheme, PersonalPoint, PersonalPointSchema,\
    Owner, OwnerEmail, EventLogger
from flask_jwt_extended import jwt_required
from dateutil.relativedelta import *
import datetime
import status

actual_point_schema = ActualPointScheme()
personal_point_schema = PersonalPointSchema()


class ActualPointResource(Resource):
    @jwt_required
    def get(self, id):
        actual_point = ActualPoint.query.get_or_404(id)
        result = actual_point_schema.dump(actual_point).data
        return result


class ActualPointListResource(Resource):
    @jwt_required
    def get(self):
        actual_point = ActualPoint.query.all()
        result = actual_point_schema.dump(actual_point, many=True).data
        return result


def get_actual_point_count(reference_date):
    banked_count = len(ActualPoint.query.
                       filter(ActualPoint.use_year < (reference_date + relativedelta(years=-1)),
                              ActualPoint.use_year > (reference_date + relativedelta(years=-2))).
                       filter(ActualPoint.trip_id.is_(None)).
                       filter(ActualPoint.banked_date.isnot(None)).
                       all())
    current_count = len(ActualPoint.query.
                        filter(ActualPoint.use_year < reference_date,
                               ActualPoint.use_year > (reference_date + relativedelta(years=-1))).
                        filter(ActualPoint.trip_id.is_(None)).
                        filter(ActualPoint.banked_date.is_(None)).
                        all())
    current_banked_count = len(ActualPoint.query.
                               filter(ActualPoint.use_year < reference_date,
                                      ActualPoint.use_year > (reference_date + relativedelta(years=-1))).
                               filter(ActualPoint.trip_id.is_(None)).
                               filter(ActualPoint.banked_date.isnot(None)).
                               all())
    borrow_count = len(ActualPoint.query.
                       filter(ActualPoint.use_year < (reference_date + relativedelta(years=+1)),
                              ActualPoint.use_year > reference_date).
                       filter(ActualPoint.trip_id.is_(None)).
                       filter(ActualPoint.banked_date.is_(None)).
                       all())

    return {'banked': banked_count,
            'current': current_count,
            'current_banked': current_banked_count,
            'borrow': borrow_count}


class ActualPointCountResource(Resource):
    @jwt_required
    def get(self):
        reference_date = datetime.datetime.now()
        return get_actual_point_count(reference_date)


class PersonalPointResource(Resource):
    @jwt_required
    def get(self, id):
        personal_point = PersonalPoint.query.get_or_404(id)
        result = personal_point_schema.dump(personal_point).data
        return result


class PersonalPointListResource(Resource):
    @jwt_required
    def get(self):
        personal_point = PersonalPoint.query.all()
        result = personal_point_schema.dump(personal_point, many=True).data
        return result


def get_personal_point_count(email, reference_date):
    banked_count = len(PersonalPoint.query.
                       join(Owner).join(OwnerEmail).
                       filter(OwnerEmail.owner_email == email).
                       filter(PersonalPoint.use_year < (reference_date + relativedelta(years=-1))).
                       filter(PersonalPoint.trip_id.is_(None)).
                       all())
    current_count = len(PersonalPoint.query.
                        join(Owner).join(OwnerEmail).
                        filter(OwnerEmail.owner_email == email).
                        filter(PersonalPoint.use_year < reference_date,
                               PersonalPoint.use_year > (reference_date + relativedelta(years=-1))).
                        filter(PersonalPoint.trip_id.is_(None)).
                        all())
    borrow_count = len(PersonalPoint.query.
                       join(Owner).join(OwnerEmail).
                       filter(OwnerEmail.owner_email == email).
                       filter(PersonalPoint.use_year < (reference_date + relativedelta(years=+1)),
                              PersonalPoint.use_year > reference_date).
                       filter(PersonalPoint.trip_id.is_(None)).
                       all())
    return {'banked': banked_count,
            'current': current_count,
            'borrow': borrow_count}


class PersonalPointCountResource(Resource):
    @jwt_required
    def get(self, owner_id):
        reference_date = datetime.datetime.now()
        return get_personal_point_count(owner_id, reference_date)


class PointCount(Resource):
    @jwt_required
    def get(self, owner_email):
        reference_date = datetime.datetime.now()
        personal_points = get_personal_point_count(owner_email, reference_date)
        actual_points = get_actual_point_count(reference_date)

        return {'actual_points': actual_points,
                'personal_points': personal_points}


class BankPointCountResource(Resource):
    @jwt_required
    def get(self, epoch_bank_date):
        bank_date = datetime.datetime.fromtimestamp(epoch_bank_date)
        banked_count = len(ActualPoint.query.
                           filter(ActualPoint.use_year < bank_date,
                                  ActualPoint.use_year > (bank_date + relativedelta(years=-1))).
                           filter(ActualPoint.trip_id.is_(None)).filter(ActualPoint.banked_date.is_(None)).
                           all())
        return {'available_bank_count': banked_count,
                'bank_date': bank_date.strftime('%Y-%m-%d')}


class BankPointResource(Resource):
    @jwt_required
    def post(self):
        request_dict = request.get_json()
        if not request_dict:
            resp = {'message': 'No input data provided'}
            return resp, status.HTTP_400_BAD_REQUEST
        bank_date = datetime.datetime.fromtimestamp(request_dict['epoch_bank_date'])
        bankable_points = ActualPoint.query.\
            filter(ActualPoint.use_year < bank_date,
                   ActualPoint.use_year > (bank_date + relativedelta(years=-1))).\
            filter(ActualPoint.trip_id.is_(None)).filter(ActualPoint.banked_date.is_(None)).\
            limit(request_dict['count_to_bank']).all()

        if request_dict['count_to_bank'] > len(bankable_points):
            resp = jsonify({"error": "requested bank is more than available bankable points"})
            resp.status_code = status.HTTP_400_BAD_REQUEST
            return resp

        for point in bankable_points:
            point.banked_date = bank_date

        log = 'POINTS BANKED - %s points banked with a bank date of %s' % (len(bankable_points), bank_date.strftime('%Y-%m-%d %H:%M:%S'))

        db.session.add(EventLogger('test@google.com', log))
        db.session.commit()



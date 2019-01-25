from flask_restful import Resource, reqparse
from models import ActualPoint, ActualPointScheme, PersonalPoint, PersonalPointSchema
from flask_jwt_extended import jwt_required
from dateutil.relativedelta import *
import datetime

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


class ActualPointCountResource(Resource):
    @jwt_required
    def get(self):
        reference_date = datetime.datetime.now()

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


class PersonalPointCountResource(Resource):
    @jwt_required
    def get(self, owner_id):
        reference_date = datetime.datetime.now()
        # parser = reqparse.RequestParser()
        # parser.add_argument('owner_id', help='ID of owner')
        # args = parser.parse_args()
        # owner_id = args['owner_id']

        banked_count = len(PersonalPoint.query.
                           filter(PersonalPoint.use_year < (reference_date + relativedelta(years=-1))).
                           filter(PersonalPoint.trip_id.is_(None)).
                           filter(PersonalPoint.owner_id == owner_id).all())
        current_count = len(PersonalPoint.query.
                            filter(PersonalPoint.use_year < reference_date,
                                   PersonalPoint.use_year > (reference_date + relativedelta(years=-1))).
                            filter(PersonalPoint.trip_id.is_(None)).
                            filter(PersonalPoint.owner_id == owner_id).all())
        borrow_count = len(PersonalPoint.query.
                           filter(PersonalPoint.use_year < (reference_date + relativedelta(years=+1)),
                                  PersonalPoint.use_year > reference_date).
                           filter(PersonalPoint.trip_id.is_(None)).
                           filter(PersonalPoint.owner_id == owner_id).all())
        return {'banked': banked_count,
                'current': current_count,
                'borrow': borrow_count}


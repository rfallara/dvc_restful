from flask_restful import Resource
from models import ActualPoint, ActualPointScheme, PersonalPoint, PersonalPointSchema

actual_point_schema = ActualPointScheme()
personal_point_schema = PersonalPointSchema()

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


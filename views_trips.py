from flask_restful import Resource
from models import Trip, TripSchema

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

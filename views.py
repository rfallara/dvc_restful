from flask import Blueprint
from flask_restful import Api
from views_owner import OwnerResource, OwnerListResource, OwnerEmailResource, OwnerEmailListResource
from views_resorts import ResortResource, ResortListResource, RoomTypeResource, RoomTypeListResource, \
    BookableRoomResource, BookableRoomListResource
from views_points import ActualPointResource, ActualPointListResource, PersonalPointResource, PersonalPointListResource
from views_trips import TripResource, TripListResource


api_bp = Blueprint('api', __name__)
api = Api(api_bp)

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

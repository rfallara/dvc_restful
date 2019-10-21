from flask import request
from flask_restful import Resource
from models import EventLog, EventLogSchema
from flask_jwt_extended import jwt_required
from dvc_decorators import jwt_access_level


event_log_schema = EventLogSchema()


class EventLogResource(Resource):
    @jwt_required
    @jwt_access_level(7)
    def get(self, id):
        event = EventLog.query.get_or_404(id)
        result = event_log_schema.dump(event).data
        return result


class EventLogListResource(Resource):
    @jwt_required
    @jwt_access_level(7)
    def get(self):
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 25, type=int)
        events = EventLog.query.order_by(EventLog.timestamp.desc()).paginate(page, per_page)
        items = event_log_schema.dump(events.items, many=True).data
        result = {
            'items': items,
            'current_page': page,
            'pages': events.pages,
            'has_next': events.has_next,
            'has_prev': events.has_prev,
            'next_page': events.next_num,
            'prev_page': events.prev_num,
            'collection_size': events.total
        }

        return result

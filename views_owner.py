from flask import request, jsonify
from flask_restful import Resource
from sqlalchemy.exc import SQLAlchemyError
from models import db, Owner, OwnerSchema, OwnerEmail, OwnerEmailSchema, PersonalPoint, log_event
import status
import datetime
from dateutil.relativedelta import *
from flask_jwt_extended import jwt_required, get_jwt_identity

owner_schema = OwnerSchema()
owner_email_schema = OwnerEmailSchema()


class OwnerResource(Resource):
    @jwt_required
    def get(self, owner_id):
        owner = Owner.query.get_or_404(owner_id)
        result = owner_schema.dump(owner).data
        return result

    @jwt_required
    def put(self, owner_id):
        owner = Owner.query.get_or_404(owner_id)
        update_dict = request.get_json()
        if not update_dict:
            resp = {'message': 'No input data provided'}
            return resp, status.HTTP_400_BAD_REQUEST
        errors = owner_schema.validate(update_dict)
        if errors:
            return errors, status.HTTP_400_BAD_REQUEST
        try:
            if 'name' in update_dict:
                owner.name = update_dict['name']
            owner.update()
            log_event(get_jwt_identity(), 'UPDATE - ' + owner.__repr__())
            return self.get(owner_id)
        except SQLAlchemyError as e:
            db.session.rollback()
            resp = jsonify({"error": str(e)})
            resp.status_code = status.HTTP_400_BAD_REQUEST
            return resp

    @jwt_required
    def delete(self, owner_id):
        owner = Owner.query.get_or_404(owner_id)
        try:
            owner.delete(owner)
            log_event(get_jwt_identity(), 'DELETE - ' + owner.__repr__())
            return '', status.HTTP_204_NO_CONTENT
        except SQLAlchemyError as e:
            db.session.rollback()
            # resp = jsonify({"error": str(e)})
            print(e)
            resp = jsonify({"error": "Unable to delete owner"})
            resp.status_code = status.HTTP_401_UNAUTHORIZED
            return resp


class OwnerListResource(Resource):
    @jwt_required
    def get(self):
        owners = Owner.query.order_by(Owner.id).all()
        result = owner_schema.dump(owners, many=True).data
        return result

    @jwt_required
    def post(self):
        request_dict = request.get_json()
        if not request_dict:
            resp = {'message': 'No input data provided'}
            return resp, status.HTTP_400_BAD_REQUEST
        errors = owner_schema.validate(request_dict)
        if errors:
            return errors, status.HTTP_400_BAD_REQUEST
        try:
            owner = Owner(request_dict['name'])
            owner.add(owner)
            log_event(get_jwt_identity(), 'ADD - ' + owner.__repr__())
            query = Owner.query.get(owner.id)
            result = owner_schema.dump(query).data
            return result, status.HTTP_201_CREATED
        except SQLAlchemyError as e:
            db.session.rollback()
            resp = jsonify({"error": str(e)})
            resp.status_code = status.HTTP_400_BAD_REQUEST
            return resp


class OwnerEmailResource(Resource):
    @jwt_required
    def get(self, owner_id):
        owner_email = OwnerEmail.query.get_or_404(owner_id)
        result = owner_email_schema.dump(owner_email).data
        return result

    @jwt_required
    def put(self, owner_id):
        owner_email = OwnerEmail.query.get_or_404(owner_id)
        update_dict = request.get_json()
        if not update_dict:
            resp = {'message': 'No input data provided'}
            return resp, status.HTTP_400_BAD_REQUEST
        if 'owner_email' in update_dict:
            owner_email.owner_email = update_dict['owner_email']
        if 'access_level' in update_dict:
            owner_email.access_level = update_dict['access_level']
        dumped_message, dump_errors = owner_email_schema.dump(owner_email)
        if dump_errors:
            return dump_errors, status.HTTP_400_BAD_REQUEST
        validate_errors = owner_email_schema.validate(dumped_message)
        if validate_errors:
            return validate_errors, status.HTTP_400_BAD_REQUEST
        try:
            log_event(get_jwt_identity(), 'UPDATE - ' + owner_email.__repr__())
            owner_email.update()
            return self.get(owner_id)
        except SQLAlchemyError as e:
            db.session.rollback()
            resp = jsonify({"error": str(e)})
            resp.status_code = status.HTTP_400_BAD_REQUEST
            return resp

    @jwt_required
    def delete(self, owner_id):
        owner_email = OwnerEmail.query.get_or_404(owner_id)
        try:
            owner_email.delete(owner_email)
            log_event(get_jwt_identity(), 'DELETE - ' + owner_email.__repr__())
            return '', status.HTTP_204_NO_CONTENT
        except SQLAlchemyError as e:
            db.session.rollback()
            resp = jsonify({"error": str(e)})
            resp.status_code = status.HTTP_401_UNAUTHORIZED
            return resp


class OwnerEmailListResource(Resource):
    @jwt_required
    def get(self):
        owner_emails = OwnerEmail.query.all()
        result = owner_email_schema.dump(owner_emails, many=True).data
        return result

    @jwt_required
    def post(self):
        request_dict = request.get_json()
        if not request_dict:
            resp = {'message': 'No input data provided'}
            return resp, status.HTTP_400_BAD_REQUEST
        errors = owner_email_schema.validate(request_dict)
        if errors:
            return errors, status.HTTP_400_BAD_REQUEST
        try:
            owner_name = request_dict['owner']['name']
            owner = Owner.query.filter_by(name=owner_name).first()
            if owner is None:
                # Owner does not exist
                resp = {'message': 'owner name does not exist'}
                return resp, status.HTTP_400_BAD_REQUEST
                # Now that we are sure we have an owner
                # create a new owner email
            owner_email = OwnerEmail(request_dict['owner_email'], owner)
            if 'access_level' in request_dict:
                owner_email.access_level = request_dict['access_level']
            owner_email.add(owner_email)
            log_event(get_jwt_identity(), 'ADD - ' + owner_email.__repr__())
            query = OwnerEmail.query.get(owner_email.id)
            result = owner_email_schema.dump(query).data
            return result, status.HTTP_201_CREATED
        except SQLAlchemyError as e:
            db.session.rollback()
            resp = jsonify({"error": str(e)})
            resp.status_code = status.HTTP_400_BAD_REQUEST
            return resp


class OwnerDetailedResource(Resource):

    @jwt_required
    def get(self, owner_id):
        current_owner = Owner.query.get_or_404(owner_id)
        # current_owner = Owner.query.join(OwnerEmail).filter(OwnerEmail.owner_email == email).first()

        reference_date = datetime.datetime.now()

        banked_count = len(PersonalPoint.query.
                           join(Owner).
                           filter(Owner.id == current_owner.id).
                           filter(PersonalPoint.use_year < (reference_date + relativedelta(years=-1))).
                           filter(PersonalPoint.trip_id.is_(None)).
                           all())

        current_count = len(PersonalPoint.query.
                            join(Owner).
                            filter(Owner.id == current_owner.id).
                            filter(PersonalPoint.use_year < reference_date,
                                   PersonalPoint.use_year > (reference_date + relativedelta(years=-1))).
                            filter(PersonalPoint.trip_id.is_(None)).
                            all())
        borrow_count = len(PersonalPoint.query.
                           join(Owner).
                           filter(Owner.id == current_owner.id).
                           filter(PersonalPoint.use_year < (reference_date + relativedelta(years=+1)),
                                  PersonalPoint.use_year > reference_date).
                           filter(PersonalPoint.trip_id.is_(None)).
                           all())
        # return {'banked': banked_count,
        #         'current': current_count,
        #         'borrow': borrow_count}

        current_owner_data = owner_schema.dump(current_owner).data
        current_owner_data.update({'bankedPoints': banked_count,
                                   'currentPoints': current_count,
                                   'borrowPoints': borrow_count})
        return current_owner_data

from flask import request, jsonify
from flask_restful import Resource
from sqlalchemy.exc import SQLAlchemyError
from models import db, Owner, OwnerSchema, OwnerEmail, OwnerEmailSchema
import status
from flask_jwt_extended import jwt_required

owner_schema = OwnerSchema()
owner_email_schema = OwnerEmailSchema()

class OwnerResource(Resource):
    @jwt_required
    def get(self, id):
        owner = Owner.query.get_or_404(id)
        result = owner_schema.dump(owner).data
        return result

    @jwt_required
    def put(self, id):
        owner = Owner.query.get_or_404(id)
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
            return self.get(id)
        except SQLAlchemyError as e:
                db.session.rollback()
                resp = jsonify({"error": str(e)})
                resp.status_code = status.HTTP_400_BAD_REQUEST
                return resp

    @jwt_required
    def delete(self, id):
        owner = Owner.query.get_or_404(id)
        try:
            owner.delete(owner)
            return ('', status.HTTP_204_NO_CONTENT)
        except SQLAlchemyError as e:
                db.session.rollback()
                #resp = jsonify({"error": str(e)})
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
    def get(self, id):
        owner_email = OwnerEmail.query.get_or_404(id)
        result = owner_email_schema.dump(owner_email).data
        return result

    @jwt_required
    def put(self, id):
        owner_email = OwnerEmail.query.get_or_404(id)
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
            owner_email.update()
            return self.get(id)
        except SQLAlchemyError as e:
            db.session.rollback()
            resp = jsonify({"error": str(e)})
            resp.status_code = status.HTTP_400_BAD_REQUEST
            return resp

    @jwt_required
    def delete(self, id):
        owner_email = OwnerEmail.query.get_or_404(id)
        try:
            owner_email.delete(owner_email)
            return ('', status.HTTP_204_NO_CONTENT)
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
            owner_email = OwnerEmail(request_dict['owner_email'],owner)
            if 'access_level' in request_dict:
                owner_email.access_level = request_dict['access_level']
            owner_email.add(owner_email)
            query = OwnerEmail.query.get(owner_email.id)
            result = owner_email_schema.dump(query).data
            return result, status.HTTP_201_CREATED
        except SQLAlchemyError as e:
            db.session.rollback()
            resp = jsonify({"error": str(e)})
            resp.status_code = status.HTTP_400_BAD_REQUEST
            return resp

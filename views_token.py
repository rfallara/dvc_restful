import time
from datetime import timedelta

from flask import request
from flask_jwt_extended import create_access_token, create_refresh_token, decode_token
from flask_restful import Resource
from google.auth.transport import requests
from google.oauth2 import id_token

import status
from models import TokenUser, OwnerEmail, Owner, event_logger


class Token(Resource):
    def post(self):
        # get the post data
        post_data = request.get_json()
        if post_data.get('username'):
            return self.traditional_login(post_data)
        elif post_data.get('google_id_token'):
            return self.google_auth_login(post_data)

    @staticmethod
    def traditional_login(post_data):

        try:
            # fetch the user data
            user = TokenUser.query.filter_by(
                username=post_data.get('username')
            ).first()

            #
            # if user and bcrypt.check_password_hash(
            #         user.password, post_data.get('password')
            # ):
            if user and user.password == post_data.get('password'):
                access_token = create_access_token(identity=user.username,
                                                   expires_delta=timedelta(minutes=60))
                refresh_token = create_refresh_token(identity=user.username)
                decoded_token = decode_token(access_token)

                response_object = {
                    'status': 'success',
                    'message': 'Successfully logged in.',
                    'access_token': access_token,
                    'refresh_token': refresh_token,
                    'exp': decoded_token['exp'],
                    'owner': '',
                    'email': '',
                    'picture': ''
                }
                return response_object, status.HTTP_201_CREATED
            else:
                response_object = {
                    'status': 'fail',
                    'message': 'User does not exist or bad password.'
                }
                return response_object, status.HTTP_401_UNAUTHORIZED
                # return make_response(jsonify(response_object)), 404
        except Exception as e:
            print(e)
            response_object = {
                'status': 'fail',
                'message': 'Try again'
            }
            return response_object, status.HTTP_500_INTERNAL_SERVER_ERROR
            # return make_response(jsonify(response_object)), 500

    @staticmethod
    def google_auth_login(post_data):
        token = post_data.get('google_id_token')
        client_id = '352426068501-r1o358blf1hqnhvnh5olce4b5toasadj.apps.googleusercontent.com'
        idinfo = id_token.verify_oauth2_token(token, requests.Request(), client_id)
        # check issuer
        if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
            response_object = {
                'status': 'fail',
                'message': 'Not a valid issuer.'
            }
            return response_object, status.HTTP_401_UNAUTHORIZED

        # check expired
        if idinfo['exp'] < time.time():
            response_object = {
                'status': 'fail',
                'message': 'Token is expired'
            }
            return response_object, status.HTTP_401_UNAUTHORIZED

        # find a valid owner email
        # owner = OwnerEmail.query.filter_by(owner_email = idinfo['email']).first()
        owner = Owner.query.join(OwnerEmail).filter(OwnerEmail.owner_email == idinfo['email']).first()
        if owner:
            access_token = create_access_token(identity=idinfo['email'],
                                               expires_delta=timedelta(minutes=60))
            refresh_token = create_refresh_token(identity=idinfo['email'])
            decoded_token = decode_token(access_token)

            response_object = {
                'status': 'success',
                'message': 'Successfully logged in.',
                'access_token': access_token,
                'refresh_token': refresh_token,
                'exp': decoded_token['exp'],
                'owner': owner.name,
                'email': idinfo['email'],
                'picture': idinfo['picture']
            }
            owner.add(event_logger(idinfo['email'], 'User authenticated - ' + owner.__repr__()))
            return response_object, status.HTTP_201_CREATED
        else:
            response_object = {
                'status': 'fail',
                'message': 'Matching owner email not found'
            }
            return response_object, status.HTTP_401_UNAUTHORIZED

from flask import request
from flask_restful import Resource
from models import TokenUser
import status
from flask_jwt_extended import create_access_token, create_refresh_token, decode_token
from datetime import timedelta


class Token(Resource):
    def post(self):
        # get the post data
        post_data = request.get_json()
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
                    'exp': decoded_token['exp']
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


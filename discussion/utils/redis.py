# from discussion.extentions import redis
# import jwt
# from flask import g, current_app

# class RedisTokenManager(redis):

#     def __init__(self):
#         self.user_id = g.user.id
#         self.refresh_expire = current_app.config['REFRESH_EXP']
#         self.access_expire = current_app.config['ACCESS_EXP']
#         self.token_family = current_app.config['REFRESH_TOKEN_FAMILY'].format(user_id=self.user_id)


#     def store_used_refresh_token(refresh_token):
#         response = redis.set(
#             current_app.config['REFRESH_TOKEN_FAMILY'].format(user_id=g.user.id),
#             refresh_token,
#         )
#         if not response:
#             logger.error('Failed to store revoked refresh token.')
#             raise InvalidAttemp()
        
#     def check_revoked_token():
#         response = redis.get(
#             token
#         )
#         if response:
#             raise jwt.exceptions.InvalidTokenError()

#     def check_used_refresh_token(self, refresh_token):
#         response = redis.sismember(
#             self.token_family,
#             refresh_token,
#         )
#         if response:
#             redis.delete(

#             )
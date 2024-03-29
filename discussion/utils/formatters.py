from logging import Formatter
from flask import request

class ResponseFormatter(Formatter):
    def format(self, record):

        # Response parameters
        record.status = record.response.status_code
        record.content_type = record.response.content_type
        
        #Request parameters
        record.url = request.url
        record.scheme = request.scheme
        record.method = request.method
        record.path = request.path
        record.remote_addr = request.remote_addr
        record.view_args = request.view_args
        record.data = request.data
        record.query_string = request.query_string
        record.user_agent = request.user_agent
        record.authorization = request.authorization
        return super().format(record)
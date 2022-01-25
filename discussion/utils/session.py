from flask import request, g, current_app
from discussion.extentions import redis

class Session:
    def __init__(self, user_id=None, ip=None, client=None, refresh_token=None, access_token=None):
        self.user_id = user_id or g.user.id
        self.ip = ip or request.remote_addr
        self.client = client or request.headers['User-Agent']
        self.refresh_token = refresh_token
        self.access_token = access_token
        self.index = None

    @staticmethod
    def from_session_id(session_id):
        parsed_id = session_id.split(':')
        return Session(*parsed_id)
    
    def load_all_user_sessions(self):
        session_ids = redis.connection.lrange(g.user.id, 0, -1)
        self.all_sessions = list(map(Session.from_session_id, session_ids))

    def load_current_session(self):
        self.load_all_user_sessions()
        try:
            self.index = self.all_sessions.index(self)
            self.refresh_token = self.all_sessions[self.index].refresh_token
            self.access_token = self.all_sessions[self.index].access_token
        except:
            pass

    def current_session_exists(self):
        self.load_current_session()
        if self.refresh_token:
            return True
        return False
    
    def sessions_limit_exceeded(self):
        if self.current_session_exists():
            return False
        return len(self.all_sessions) >= current_app.config['MAX_SESSIONS']
    
    def remove_this_session(self):
        self.all_sessions.remove(self.index)

    def get_all_tokens(self):
        return [(s.access_token, s.refresh_token) for s in self.all_sessions]

    def __eq__(self, __o: object) -> bool:
        return self.__repr__() == __o.__repr__()
    
    def __ne__(self, __o: object) -> bool:
        return not self.__eq__(__o)
    
    def __str__(self) -> str:
        return f"{self.user_id}:{self.ip}:{self.client}:{self.refresh_token}:{self.access_token}"
    
    def __repr__(self) -> str:
        return f"{self.user_id}:{self.ip}:{self.client}"

from ipaddress import ip_address

from discussion.extentions import redis
from flask import current_app, g, request


class Session:

    def __init__(self, 
        user_id=None, 
        ip='0.0.0.0',
        client=None, 
        refresh_token=None, 
        access_token=None
    ):
        self.user_id = user_id or g.user.id
        # self.ip = ip_address(ip) or ip_address(request.remote_addr)
        self.ip = ip or request.remote_addr
        self.client = client or request.headers['User-Agent']
        self.refresh_token = refresh_token
        self.access_token = access_token
        self.index = None
        self._all_sessions = None

    @staticmethod
    def from_session_id(session_id):
        parsed_id = session_id.split(':')
        return Session(*parsed_id)
    
    @property
    def all_sessions(self):
        if not self._all_sessions:
            session_ids = redis.connection.lrange(g.user.id, 0, -1)
            self._all_sessions = list(map(Session.from_session_id, session_ids))
        return self._all_sessions

    def load_current_session(self):
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
    
    def delete_session(self):
        pipe = redis.connection.pipeline()

        pipe = pipe.delete(g.session.refresh_token)
        self.all_sessions.remove(self.index)
        pipe = pipe.delete(g.user.id)
        pipe = pipe.lpush([str(s) for s in g.session.all_sessions])
        pipe.execute()
    
    def renew_token(self):
        pipe = redis.connection.pipeline()

        access_token_expire = current_app.config['ACCESS_TOKEN_EXP']
        refresh_token_expire = current_app.config['REFRESH_TOKEN_EXP']

        pipe = pipe.expire(g.access_token, access_token_expire)
        pipe = pipe.expire(g.session.refresh_token, refresh_token_expire)
        pipe.execute()

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

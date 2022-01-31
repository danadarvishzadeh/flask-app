from datetime import datetime
from hashlib import sha256
import re
from discussion.extentions import redis
from flask import current_app, g, request
from user_agents import parse
from .errors import InvalidSession

class Session:

    def __init__(self,
        session_id=None,
        ip=None,
        user_agent=None,
        first_login=None,
        refresh_token=None,
        access_token=None
    ):
        self._session_id = session_id
        self.ip = ip or request.remote_addr
        self.user_agent = user_agent
        self.first_login = first_login or datetime.utcnow()
        self.refresh_token = refresh_token
        self.access_token = access_token
        self.index = None
        self._all_sessions = None

    @staticmethod
    def from_redis(session):
        parsed = session.split('|')
        return Session(*parsed)

    @property
    def session_id(self):
        if not self._session_id:
            data = (self.ip + request.headers['User-Agent']).encode()
            self._session_id = sha256(data).hexdigest()
        return self._session_id

    @property
    def user_agent(self):
        if not self._user_agent:
            self._user_agent = {}    
        return self._user_agent
    
    @user_agent.setter
    def user_agent(self, value):
        self._user_agent = {}
        if value:
            parsed = value.split(':')
            if len(parsed) != 3:
                raise InvalidSession()
            self._user_agent['os'] = parsed[0]
            self._user_agent['device'] = parsed[1]
            self._user_agent['browser'] = parsed[2]
        else:
            self._user_agent['platform'] = request.user_agent.platform
            self._user_agent['device'] = request.user_agent.device.family
            self._user_agent['browser'] = request.user_agent.browser

    @property
    def all_sessions(self):
        if self._all_sessions is None:
            session_ids = redis.connection.lrange(g.user.id, 0, -1)
            self._all_sessions = list(
            map(Session.from_redis, session_ids))
        return self._all_sessions

    def load_current_session(self):
        try:
            self.index = self.all_sessions.index(self)
            self.refresh_token = self.all_sessions[self.index].refresh_token
            self.access_token = self.all_sessions[self.index].access_token
        except Exception as e:
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
        self.load_current_session()
        pipe = redis.connection.pipeline()

        access_token_expire = current_app.config['ACCESS_TOKEN_EXP']
        refresh_token_expire = current_app.config['REFRESH_TOKEN_EXP']

        pipe = pipe.expire(self.access_token, access_token_expire)
        pipe = pipe.expire(self.refresh_token, refresh_token_expire)
        pipe.execute()

    def get_all_tokens(self):
        return [(s.access_token, s.refresh_token) for s in self.all_sessions]

    def __eq__(self, __o: object) -> bool:
        if isinstance(__o, Session):
            return self.session_id == __o.session_id
        return super().__eq__(self, __o)

    def __ne__(self, __o: object) -> bool:
        return not self.__eq__(__o)

    def __str__(self) -> str:
        return f"{self.session_id}|{self.ip}|"\
        f"{self.user_agent['platform']}:{self.user_agent['device']}:"\
        f"{self.user_agent['browser']}|{self.first_login}|"\
        f"{self.refresh_token}|{self.access_token}"

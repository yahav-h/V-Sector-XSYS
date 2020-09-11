from commons import Base
from sqlalchemy import Column, String, DateTime, JSON, ForeignKey, Boolean
from sqlalchemy.orm import relationship
import uuid
import datetime
import time


class Agent(Base):
    __tablename__ = 'agents'
    id = Column(String(50), primary_key=True)
    delegated_id = Column(String(50), unique=True, nullable=False)
    did_handshake = Column(Boolean(), nullable=False, default=False)
    history = Column(JSON(), nullable=False, default=dict())
    last_time_accessed = Column(DateTime(), nullable=False)
    time_created = Column(DateTime(), nullable=False)

    def __init__(self, peer_id=None, last_time_accessed=None, json=None):
        self.id = uuid.uuid5(uuid.NAMESPACE_URL, time.time().__str__()[:10]).__str__()
        self.time_created = datetime.datetime.now()
        self.last_time_accessed = datetime.datetime.now() if last_time_accessed is None else last_time_accessed
        self.delegated_id = peer_id
        if self.delegated_id:
            self.did_handshake = True
        self.history = dict() if json is None else json

    def __repr__(self):
        return '<Agent %r>' % self.id

    def to_json(self):
        return {
            'id': self.id,
            'peerId': self.delegated_id,
            'didHandshake': self.did_handshake,
            'timeCreated': self.time_created.__str__(),
            'lastTimeAccessed': self.last_time_accessed.__str__(),
            'history': self.history
        }

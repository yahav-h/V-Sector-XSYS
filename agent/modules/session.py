from commons import Base
from sqlalchemy import Column, String, DateTime, ForeignKey, Boolean
# from sqlalchemy.orm import relationship
import uuid
import datetime
import time


class Session(Base):
    __tablename__ = 'sessions'
    id = Column(String(50), primary_key=True)
    time_created = Column(DateTime(), unique=True, default=None)
    valid_until = Column(DateTime(), unique=True, default=None)
    is_active = Column(Boolean(), nullable=False, default=False)
    token = Column(String(64), nullable=False, default=None)
    internet_id = Column(String(64), unique=True, nullable=False, default=-1)

    def __init__(self, token=None):
        self.id = uuid.uuid5(uuid.NAMESPACE_URL, time.time().__str__()[:10]).__str__()
        self.time_created = int(datetime.datetime.now().timestamp().__str__()[:10])
        self.valid_until = self.time_created + 500000
        self.token = token
        self.internet_id = '%s:%s' % (self.id, token)
        if self.time_created is not None:
            self.is_active = True

    def __repr__(self):
        return '<Session %r>' % self.id

    def to_json(self):
        return {
                'id': self.id,
                'timeCreated': self.time_created,
                'validUntil': self.valid_until,
                'isActive': self.is_active,
                'token': self.token
        }


if __name__ == '__main__':
    s = Session()
    print(s.to_json())


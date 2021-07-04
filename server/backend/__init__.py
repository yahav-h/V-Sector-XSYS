from sqlalchemy.ext.declarative import declarative_base
from os.path import join, dirname, abspath, exists
import logging

__SERVER_DIR = 'server'

get_server_db_path = lambda: join(dirname(dirname(abspath(__file__))), __SERVER_DIR) \
    if exists(join(dirname(dirname(abspath(__file__))), __SERVER_DIR)) \
    else Exception(f'[Err] path {join(dirname(dirname(abspath(__file__))), __SERVER_DIR)} does not exists')

Base = declarative_base()


class BaseDB:
    log = None
    db_session = None
    engine = None
    app_name = None

    def __init__(self):
        self.Base = Base
        self.log = logging.getLogger(self.app_name)

    def init_db(self):
        try:
            self.Base.metadata.create_all(bind=self.engine)
            self.log.debug(f'[+] database schema created')
            return True
        except Exception as e:
            self.log.error(f'[Err] error occur while initializing database\n{e}')
            return False

    def add(self, obj):
        try:
            self.db_session.add(obj)
            self.db_session.commit()
            self.log.debug(f'[+] new object {obj} added to database')
            return True
        except Exception as e:
            self.log.error(f'[Err] error occur while adding object to database\n{e}')
            return False

    def delete(self, obj):
        try:
            self.db_session.delete(obj)
            self.db_session.commit()
            self.log.debug(f'[+] object {obj} deleted from database')
            return True
        except Exception as e:
            self.log.error(f'[Err] error occur while deleting object from ddatabase\n{e}')
            return False


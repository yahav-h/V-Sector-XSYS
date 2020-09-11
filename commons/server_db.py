from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from commons import BaseDB, get_server_db_path, join, logging


class ServerDataBase(BaseDB):
    app_name = 'ServerDB'
    logging.basicConfig(filename=join(get_server_db_path(), 'logs', 'server.app-runtime.log'),
                        filemode='w', format=logging.BASIC_FORMAT,
                        level=logging.DEBUG)

    def __init__(self):
        super(ServerDataBase, self).__init__()
        self.engine = create_engine(f'sqlite:////{get_server_db_path()}/v_sec_server.db', convert_unicode=True)
        self.db_session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=self.engine))
        self.Base.query = self.db_session.query_property()
        self.init_db()

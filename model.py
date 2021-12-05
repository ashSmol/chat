from sqlalchemy import create_engine, Column, Integer, String, MetaData, ForeignKey, TIMESTAMP
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from common.vars import DB_ENGINE

Base = declarative_base()


class ChatClientModel(Base):
    __tablename__ = 'clients'
    id = Column(Integer, primary_key=True)
    login = Column(String)
    info = Column(String)

    def __init__(self, login, info):
        self.login = login
        self.info = info

    def __repr__(self):
        return "<Client('%s','%s)>" % (self.login, self.info)


class ClientHistory(Base):
    __tablename__ = 'clients_history'
    id = Column(Integer, primary_key=True)
    client_id = Column(Integer, ForeignKey('clients.id', ondelete='CASCADE'))
    timestamp = Column(TIMESTAMP)
    ip_address = Column(String)

    def __init__(self, login, info):
        self.login = login
        self.info = info

    def __repr__(self):
        return "<ClientHistory('%s','%s)>" % (self.login, self.info)


metadata = Base.metadata
metadata.create_all(DB_ENGINE)

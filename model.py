from sqlalchemy import create_engine, Column, Integer, String, MetaData, ForeignKey, TIMESTAMP, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from common.vars import DB_ENGINE

Base = declarative_base()


class ChatClientModel(Base):
    __tablename__ = 'clients'
    id = Column(Integer, primary_key=True)
    login = Column(String, unique=True)
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
    timestamp = Column(String)
    message_text = Column(String)

    def __init__(self, client_id, timestamp, message_text):
        self.client_id = client_id
        self.timestamp = timestamp
        self.message_text = message_text

    def __repr__(self):
        return "<ClientHistory('%s','%s)>" % (self.login, self.info)


class Contacts(Base):
    __tablename__ = 'contacts'
    id = Column(Integer, primary_key=True)
    client_id = Column(Integer, ForeignKey('clients.id', ondelete='CASCADE'))
    contact_id = Column(Integer, ForeignKey('clients.id', ondelete='CASCADE'))
    # TODO write to base unique pairs
    # UniqueConstraint('customer_id', 'location_code', name='uix_1')

    def __init__(self, client_id, contact_id):
        self.client_id = client_id
        self.contact_id = contact_id

    def __repr__(self):
        return "<Contact('%s','%s)>" % (self.client_id, self.contact_id)


metadata = Base.metadata
metadata.create_all(DB_ENGINE)

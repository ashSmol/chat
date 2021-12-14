from sqlalchemy import create_engine, Column, Integer, String, MetaData, ForeignKey, TIMESTAMP, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from common.vars import CLIENT_DB_ENGINE_PATH, CLIENT_DB_ENGINE

Base = declarative_base()


class ContactModel(Base):
    __tablename__ = 'contacts'
    id = Column(Integer, primary_key=True)
    login = Column(String, unique=True)
    info = Column(String)

    def __init__(self, login, info):
        self.login = login
        self.info = info

    def __repr__(self):
        return "<Contact('%s','%s)>" % (self.login, self.info)


class ContactsHistoryModel(Base):
    __tablename__ = 'contacts_history'
    id = Column(Integer, primary_key=True)
    contact_id = Column(Integer, ForeignKey('contacts.id', ondelete='CASCADE'))
    timestamp = Column(String)
    message_text = Column(String)

    def __init__(self, contact_id, timestamp, message_text):
        self.contact_id = contact_id
        self.timestamp = timestamp
        self.message_text = message_text

    def __repr__(self):
        return "<ContactsHistory('%s','%s, %s)>" % (self.contact_id, self.timestamp, self.message_text)


metadata = Base.metadata
metadata.create_all(CLIENT_DB_ENGINE)

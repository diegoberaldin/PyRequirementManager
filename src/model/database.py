# -*- coding: utf-8 -*-

"""This module is responsible for providing an easy-to-use interface to the
data persistence layer of the application. It contains the base class which
all ORM classes must inherit, a function to initialize the database and the
access point to all database sessions.
"""

from contextlib import contextmanager
import os

import sqlalchemy
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker

# hidden directory where the database will be stored
_DB_DIR = os.path.join(os.path.expanduser('~'), '.reqmanager')
# name of the database file
_DB_NAME = 'mydb.sqlite'
# full path where the application DB is located
DB_LOCATION = os.path.join(_DB_DIR, _DB_NAME)
# connection string for the engine
_DB_CONNECTION_STRING = 'sqlite:///' + DB_LOCATION
# database engine used by SQLAlchemy
_ENGINE = sqlalchemy.create_engine(_DB_CONNECTION_STRING)
# session to be instantiated
Session = scoped_session(sessionmaker(_ENGINE))

# class to be inherited by all ORM objects
MappedBase = declarative_base()


@contextmanager
def get_session():
    """Returns a session instance to be used for querying/manipulating the
    information stored in the application database.
    """
    session = Session()
    try:
        yield session
        session.commit()
    except sqlalchemy.exc.SQLAlchemyError as exc:
        session.rollback()
        raise exc
    finally:
        session.close()


def initialize_db():
    """Initializes the DB if it was not present on disk.
    """
    if not os.path.exists(DB_LOCATION):
        os.mkdir(_DB_DIR)
        MappedBase.metadata.create_all(_ENGINE)

# -*- coding: utf-8 -*-

"""A set of functions to perform CRUD operations on requirement sources.
"""

from src.model import database as db
from src.model.mapping import Source


def create_source(source_name):
    """Creates a new requirement source with the given name.
    """
    with db.get_session() as session:
        source = Source(source_name)
        session.add(source)


def delete_source(source_id):
    """Deletes the requirement source with the given ID.
    """
    with db.get_session() as session:
        session.query(Source).filter(Source.source_id == source_id).delete()


def get_all_source_ids():
    """Returns a list of all the source IDs that are used in the system.
    """
    with db.get_session() as session:
        return [s[0] for s in session.query(Source.source_id)]


def get_all_source_names():
    """Returns a list of all the names of the sources used in the system.
    """
    with db.get_session() as session:
        return [s[0] for s in session.query(Source.name)]


def get_source(source_id):
    """Returns the source TO that corresponds to the given source ID.
    """
    with db.get_session() as session:
        source = session.query(Source).filter(
                Source.source_id == source_id).one()
        session.expunge_all()
        return source


def get_source_id(source_name):
    """Converts between a source name and a source ID (possible because
    names are under a unique constraint and can be used as super-keys).
    """
    with db.get_session() as session:
        return session.query(Source.source_id).filter(
                Source.name == source_name).scalar()


def update_source_name(source_id, source_name):
    """Changes to the given source name the source with the given ID.
    """
    with db.get_session() as session:
        source = session.query(Source).filter(
                Source.source_id == source_id).one()
        source.name = source_name

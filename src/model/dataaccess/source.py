# -*- coding: utf-8 -*-

"""A set of functions to perform CRUD operations on requirement sources.
"""

from src.model import database as db
from src.model.mapping import Source


def create_source(source_name):
    with db.get_session() as session:
        source = Source(source_name)
        session.add(source)


def delete_source(source_id):
    with db.get_session() as session:
        session.query(Source).filter(Source.source_id == source_id).delete()


def get_all_source_ids():
    with db.get_session() as session:
        return [s[0] for s in session.query(Source.source_id)]


def get_all_source_names():
    with db.get_session() as session:
        return [e[0] for e in session.query(Source.name)]


def get_source(source_id):
    with db.get_session() as session:
        source = session.query(Source).filter(
                Source.source_id == source_id).one()
        session.expunge_all()
        return source


def get_source_id(source_name):
    with db.get_session() as session:
        return session.query(Source.source_id).filter(
                Source.name == source_name).scalar()


def update_source_name(source_id, source_name):
    with db.get_session() as session:
        source = session.query(Source).filter(
                Source.source_id == source_id).one()
        source.name = source_name

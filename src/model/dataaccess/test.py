# -*- coding: utf-8 -*-

"""A set of functions to perform CRUD operations on system tests.
"""

from src.model import database as db
from src.model.mapping import SystemTest, Requirement


def create_test(test_id, description):
    with db.get_session() as session:
        test = SystemTest(test_id, description)
        session.add(test)


def delete_test(test_id):
    with db.get_session() as session:
        session.query(SystemTest).filter(
                SystemTest.test_id == test_id).delete()
        session.execute('DELETE FROM RequirementsTests '
                'WHERE test_id = :test_id', {'test_id': test_id})


def get_all_test_ids():
    with db.get_session() as session:
        return [t[0] for t in session.query(SystemTest.test_id)]


def get_all_test_names_and_descriptions():
    with db.get_session() as session:
        return [{'id': test[0], 'description': test[1]}
                for test in
                session.query(SystemTest.test_id, SystemTest.description)]


def get_test(test_id):
    with db.get_session() as session:
        test = session.query(SystemTest).filter(
                SystemTest.test_id == test_id).scalar()
        session.expunge_all()
        return test


def update_test_associations(test_id, newly_associated_requirements):
    with db.get_session() as session:
        test = session.query(SystemTest).filter(
                SystemTest.test_id == test_id).one()
        newly_associated_requirements = set(newly_associated_requirements)
        associated_requirements = set([req.req_id
                for req in test.requirements])
        ids_to_add = newly_associated_requirements - associated_requirements
        ids_to_remove = associated_requirements - newly_associated_requirements
        for req_id in ids_to_add:
            req = session.query(Requirement).filter(
                    Requirement.req_id == req_id).one()
            test.requirements.append(req)
        for req_id in ids_to_remove:
            req = session.query(Requirement).filter(
                    Requirement.req_id == req_id).one()
            test.requirements.remove(req)


def update_test_description(test_id, description):
    with db.get_session() as session:
        test = session.query(SystemTest).filter(
                SystemTest.test_id == test_id).one()
        test.description = description


def update_test_id(test_id, new_test_id):
    with db.get_session() as session:
        test = session.query(SystemTest).filter(
                SystemTest.test_id == test_id).one()
        test.test_id = new_test_id
        session.execute('UPDATE RequirementsTests '
                'SET test_id = :new_test_id WHERE test_id = :test_id',
                {'new_test_id': new_test_id, 'test_id': test_id})

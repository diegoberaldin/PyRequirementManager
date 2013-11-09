# -*- coding: utf-8 -*-

"""A set of functions to perform CRUD operations on system tests.
"""

from src.model import database as db
from src.model.mapping import SystemTest, Requirement


def create_test(test_id, description):
    """Creates a new system test with the given ID and description.
    """
    with db.get_session() as session:
        test = SystemTest(test_id, description)
        session.add(test)


def delete_test(test_id):
    """Deletes the test with the given test ID, removing also all the entries
    from the association table linking tests and requirements.
    """
    with db.get_session() as session:
        session.query(SystemTest).filter(
                SystemTest.test_id == test_id).delete()
        session.execute('DELETE FROM RequirementsTests '
                'WHERE test_id = :test_id', {'test_id': test_id})


def get_all_test_ids():
    """Returns a list of the IDsof all tests.
    """
    with db.get_session() as session:
        return [t[0] for t in session.query(SystemTest.test_id)]


def get_all_test_names_and_descriptions():
    """Returns a list of dictionaries containing the 'id' and 'description'
    keys corresponding to the information about all the registered tests.
    """
    with db.get_session() as session:
        return [{'id': test[0], 'description': test[1]}
                for test in
                session.query(SystemTest.test_id, SystemTest.description)]


def get_test(test_id):
    """Converts a test ID to the corresponding (detached) transfer object.
    """
    with db.get_session() as session:
        test = session.query(SystemTest).filter(
                SystemTest.test_id == test_id).scalar()
        session.expunge_all()
        return test


def update_test_associations(test_id, newly_associated_requirements):
    """Updates the association between tests and requirement starting from the
    ID of the base test and a list of IDs of the requirements involved. It
    determines which entries must be added to and which must be removed from
    the association table and updates its content accordingly.
    """
    with db.get_session() as session:
        test = session.query(SystemTest).filter(
                SystemTest.test_id == test_id).one()
        newly_associated_requirements = set(newly_associated_requirements)
        associated_requirements = set([req.req_id
                for req in test.requirements])
        # determines entries to add
        ids_to_add = newly_associated_requirements - associated_requirements
        for req_id in ids_to_add:
            req = session.query(Requirement).filter(
                    Requirement.req_id == req_id).one()
            test.requirements.append(req)
        # determines entries to remove
        ids_to_remove = associated_requirements - newly_associated_requirements
        for req_id in ids_to_remove:
            req = session.query(Requirement).filter(
                    Requirement.req_id == req_id).one()
            test.requirements.remove(req)


def update_test_description(test_id, description):
    """Updates the description of the test with the given ID.
    """
    with db.get_session() as session:
        test = session.query(SystemTest).filter(
                SystemTest.test_id == test_id).one()
        test.description = description


def update_test_id(test_id, new_test_id):
    """Updates the ID of a system test. It raises IntegrityError if the
    provided new ID conflicts with the one some other already existing test.
    """
    with db.get_session() as session:
        test = session.query(SystemTest).filter(
                SystemTest.test_id == test_id).one()
        test.test_id = new_test_id
        session.execute('UPDATE RequirementsTests '
                'SET test_id = :new_test_id WHERE test_id = :test_id',
                {'new_test_id': new_test_id, 'test_id': test_id})

# -*- coding: utf-8 -*-

"""A set of functions to perform CRUD operations on system requirements.
"""

from src.model import database as db
from src.model.mapping import UseCase, Requirement, Source, SystemTest


def create_requirement(req_id, description, req_type, priority, source_id,
        parent_id=None):
    if parent_id and not _is_requirement_existing(parent_id):
        raise Exception('Nonexistent parent')
    with db.get_session() as session:
        requirement = Requirement(req_id, description, req_type, priority,
                source_id, parent_id)
        session.add(requirement)


def delete_requirement(req_id):
    with db.get_session() as session:
        session.query(Requirement).filter(
                Requirement.req_id == req_id).delete()
        session.execute('UPDATE Requirements SET parent_id = NULL '
                'WHERE parent_id = :req_id', {'req_id': req_id})
        session.execute('DELETE FROM RequirementsTests '
                'WHERE req_id = :req_id', {'req_id': req_id})
        session.execute('DELETE FROM UseCasesRequirements '
                'WHERE req_id = :req_id', {'req_id': req_id})


def get_all_requirement_ids():
    with db.get_session() as session:
        return [r[0] for r in session.query(Requirement.req_id)]


def get_all_requirement_names_and_descriptions():
    with db.get_session() as session:
        return [{'id': req[0], 'description': req[1]}
                for req in
                session.query(Requirement.req_id, Requirement.description)]


def get_requirement(req_id):
    with db.get_session() as session:
        requirement = session.query(Requirement).filter(
                Requirement.req_id == req_id).scalar()
        session.expunge_all()
        return requirement


def get_requirement_children_ids(req_id):
    with db.get_session() as session:
        return [req[0] for req in
                session.query(Requirement.req_id).filter(
                Requirement.parent_id == req_id).order_by(Requirement.req_id)]


def get_top_level_requirement_ids():
    with db.get_session() as session:
        return [req[0] for req in
                session.query(Requirement.req_id).filter(
                Requirement.parent_id == None).order_by(Requirement.req_id)]


def _is_requirement_existing(req_id):
    with db.get_session() as session:
        count = session.query(Requirement).filter(
                 Requirement.req_id == req_id).count()
        return count != 0


def update_requirement_associations(req_id, newly_associated_use_cases,
        newly_associated_tests):
    with db.get_session() as session:
        requirement = session.query(Requirement).filter(
                Requirement.req_id == req_id).one()
        # handle use cases
        newly_associated_use_cases = set(newly_associated_use_cases)
        associated_use_cases = set([uc.uc_id for uc in requirement.use_cases])
        ids_to_add = newly_associated_use_cases - associated_use_cases
        ids_to_remove = associated_use_cases - newly_associated_use_cases
        for uc_id in ids_to_add:
            uc = session.query(UseCase).filter(UseCase.uc_id == uc_id).one()
            requirement.use_cases.append(uc)
        for uc_id in ids_to_remove:
            uc = session.query(UseCase).filter(UseCase.uc_id == uc_id).one()
            requirement.use_cases.remove(uc)
        # handle tests
        newly_associated_tests = set(newly_associated_tests)
        associated_tests = set([test.test_id for test in requirement.tests])
        ids_to_add = newly_associated_tests - associated_tests
        ids_to_remove = associated_tests - newly_associated_tests
        for test_id in ids_to_add:
            test = session.query(SystemTest).filter(
                    SystemTest.test_id == test_id).one()
            requirement.tests.append(test)
        for test_id in ids_to_remove:
            test = session.query(SystemTest).filter(
                    SystemTest.test_id == test_id).one()
            requirement.tests.remove(test)


def update_requirement_description(req_id, description):
    with db.get_session() as session:
        requirement = session.query(Requirement).filter(
                Requirement.req_id == req_id).one()
        requirement.description = description


def update_requirement_id(req_id, new_req_id):
    with db.get_session() as session:
        requirement = session.query(Requirement).filter(
                Requirement.req_id == req_id).one()
        requirement.req_id = new_req_id
        session.execute('UPDATE UseCasesRequirements '
                'SET req_id = :new_req_id WHERE req_id = :req_id',
                {'new_req_id': new_req_id, 'req_id': req_id})
        session.execute('UPDATE RequirementsTests '
                'SET req_id = :new_req_id WHERE req_id = :req_id',
                {'new_req_id': new_req_id, 'req_id': req_id})
        session.execute('UPDATE Requirements set parent_id = :new_req_id '
                ' WHERE parent_id = :req_id', {'new_req_id': new_req_id,
                'req_id': req_id})


def update_requirement_parent_id(req_id, parent_id):
    with db.get_session() as session:
        requirement = session.query(Requirement).filter(
                Requirement.req_id == req_id).one()
        requirement.parent_id = parent_id


def update_requirement_priority(req_id, priority):
    with db.get_session() as session:
        requirement = session.query(Requirement).filter(
                Requirement.req_id == req_id).one()
        requirement.priority = priority


def update_requirement_source(req_id, source_name):
    with db.get_session() as session:
        requirement = session.query(Requirement).filter(
                Requirement.req_id == req_id).one()
        source = session.query(Source).filter(Source.name == source_name).one()
        requirement.source = source


def update_requirement_type(req_id, req_type):
    with db.get_session() as session:
        requirement = session.query(Requirement).filter(
                Requirement.req_id == req_id).one()
        requirement.req_type = req_type
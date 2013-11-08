# -*- coding: utf-8 -*-

"""This module contains the basic data access layer of the application, i.e. a
simple API that is offered to the UI *to query* the model about business data
state (and relationships) and to the controller *to modify* the data. This
module is intended to be used as an abstraction from the underlying data
persistence subsystem, it should only depend on transfer object (mapping) and
with the database session manager.
"""

from src.model import database as db
from src.model.mapping import UseCase, Requirement, Source, SystemTest


def get_source_ids():
    with db.get_session() as session:
        return [s[0] for s in session.query(Source.source_id)]


def get_source(source_id):
    with db.get_session() as session:
        source = session.query(Source).filter(
                Source.source_id == source_id).one()
        session.expunge_all()
        return source


def get_requirement(req_id):
    with db.get_session() as session:
        requirement = session.query(Requirement).filter(
                Requirement.req_id == req_id).scalar()
        session.expunge_all()
        return requirement


def delete_source(source_id):
    with db.get_session() as session:
        session.query(Source).filter(Source.source_id == source_id).delete()


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


def get_use_case(uc_id):
    with db.get_session() as session:
        uc = session.query(UseCase).filter(UseCase.uc_id == uc_id).scalar()
        session.expunge_all()
        return uc


def get_use_case_children_ids(uc_id):
    with db.get_session() as session:
        return [uc[0] for uc in
                session.query(UseCase.uc_id).filter(
                UseCase.parent_id == uc_id).order_by(UseCase.uc_id)]


def get_top_level_use_case_ids():
    with db.get_session() as session:
        return [uc[0] for uc in
                session.query(UseCase.uc_id).filter(
                UseCase.parent_id == None).order_by(UseCase.uc_id)]


def _is_uc_existing(uc_id):
    with db.get_session() as session:
        count = session.query(UseCase).filter(UseCase.uc_id == uc_id).count()
        return count != 0


def _is_requirement_existing(req_id):
    with db.get_session() as session:
        count = session.query(Requirement).filter(
                 Requirement.req_id == req_id).count()
        return count != 0


def create_requirement(req_id, description, req_type, priority, source_id,
        parent_id=None):
    if parent_id and not _is_requirement_existing(parent_id):
        raise Exception('Nonexistent parent')
    with db.get_session() as session:
        requirement = Requirement(req_id, description, req_type, priority,
                source_id, parent_id)
        session.add(requirement)


def create_source(source_name):
    with db.get_session() as session:
        source = Source(source_name)
        session.add(source)


def create_test(test_id, description):
    with db.get_session() as session:
        test = SystemTest(test_id, description)
        session.add(test)


def create_uc(uc_id, description, image=None, parent_id=None):
    if parent_id and not _is_uc_existing(parent_id):
        raise Exception('Nonexistent parent')
    with db.get_session() as session:
        uc = UseCase(uc_id, description, image, parent_id)
        session.add(uc)


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


def delete_test(test_id):
    with db.get_session() as session:
        session.query(SystemTest).filter(
                SystemTest.test_id == test_id).delete()
        session.execute('DELETE FROM RequirementsTests '
                'WHERE test_id = :test_id', {'test_id': test_id})


def delete_uc(uc_id):
    with db.get_session() as session:
        session.query(UseCase).filter(UseCase.uc_id == uc_id).delete()
        session.execute('UPDATE UseCases SET parent_id = NULL '
                'WHERE parent_id = :uc_id', {'uc_id': uc_id})
        session.execute('DELETE FROM UseCasesRequirements '
                'WHERE uc_id = :uc_id', {'uc_id': uc_id})


def get_all_req_ids():
    with db.get_session() as session:
        return [e[0] for e in session.query(Requirement.req_id)]


def get_all_uc_ids():
    with db.get_session() as session:
        return [e[0] for e in session.query(UseCase.uc_id)]


def get_all_source_names():
    with db.get_session() as session:
        return [e[0] for e in session.query(Source.name)]


def get_all_test_ids():
    with db.get_session() as session:
        return [e[0] for e in session.query(SystemTest.test_id)]


def get_source_id(source_name):
    with db.get_session() as session:
        return session.query(Source.source_id).filter(
                Source.name == source_name).scalar()


def get_all_uc_names_and_descriptions():
    with db.get_session() as session:
        return [{'id': uc[0], 'description': uc[1]}
                for uc in session.query(UseCase.uc_id, UseCase.description)]


def get_all_test_names_and_descriptions():
    with db.get_session() as session:
        return [{'id': test[0], 'description': test[1]}
                for test in
                session.query(SystemTest.test_id, SystemTest.description)]


def get_all_requirement_names_and_descriptions():
    with db.get_session() as session:
        return [{'id': req[0], 'description': req[1]}
                for req in
                session.query(Requirement.req_id, Requirement.description)]


def get_top_level_test_ids():
    with db.get_session() as session:
        return [test[0] for test in session.query(SystemTest.test_id)]


def get_test(test_id):
    with db.get_session() as session:
        test = session.query(SystemTest).filter(
                SystemTest.test_id == test_id).scalar()
        session.expunge_all()
        return test


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


def update_requirement_description(req_id, description):
    with db.get_session() as session:
        requirement = session.query(Requirement).filter(
                Requirement.req_id == req_id).one()
        requirement.description = description


def update_requirement_type(req_id, req_type):
    with db.get_session() as session:
        requirement = session.query(Requirement).filter(
                Requirement.req_id == req_id).one()
        requirement.req_type = req_type


def update_requirement_parent_id(req_id, parent_id):
    with db.get_session() as session:
        requirement = session.query(Requirement).filter(
                Requirement.req_id == req_id).one()
        requirement.parent_id = parent_id


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


def update_use_case_description(uc_id, description):
    with db.get_session() as session:
        uc = session.query(UseCase).filter(UseCase.uc_id == uc_id).one()
        uc.description = description


def update_use_case_id(uc_id, new_uc_id):
    with db.get_session() as session:
        uc = session.query(UseCase).filter(UseCase.uc_id == uc_id).one()
        uc.uc_id = new_uc_id
        session.execute('UPDATE UseCasesRequirements '
                'SET uc_id = :new_uc_id WHERE uc_id = :uc_id',
                {'new_uc_id': new_uc_id, 'uc_id': uc_id})
        session.execute('UPDATE UseCases set parent_id = :new_uc_id '
                ' WHERE parent_id = :uc_id', {'new_uc_id': new_uc_id,
                'uc_id': uc_id})


def update_use_case_parent_id(uc_id, parent_id):
    with db.get_session() as session:
        uc = session.query(UseCase).filter(UseCase.uc_id == uc_id).one()
        uc.parent_id = parent_id


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


def update_source_name(source_id, source_name):
    with db.get_session() as session:
        source = session.query(Source).filter(
                Source.source_id == source_id).one()
        source.name = source_name


def update_use_case_associations(uc_id, newly_associated_requirements):
    with db.get_session() as session:
        uc = session.query(UseCase).filter(UseCase.uc_id == uc_id).one()
        newly_associated_requirements = set(newly_associated_requirements)
        associated_requirements = set([req.req_id for req in uc.requirements])
        ids_to_add = newly_associated_requirements - associated_requirements
        ids_to_remove = associated_requirements - newly_associated_requirements
        for req_id in ids_to_add:
            req = session.query(Requirement).filter(
                    Requirement.req_id == req_id).one()
            uc.requirements.append(req)
        for req_id in ids_to_remove:
            req = session.query(Requirement).filter(
                    Requirement.req_id == req_id).one()
            uc.requirements.remove(req)


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

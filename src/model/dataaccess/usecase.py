# -*- coding: utf-8 -*-

"""A set of functions to perform CRUD operations on system use cases.
"""

from src.model import database as db
from src.model.mapping import UseCase, Requirement


def create_use_case(uc_id, description, image=None, parent_id=None):
    if parent_id and not _is_uc_existing(parent_id):
        raise Exception('Nonexistent parent')
    with db.get_session() as session:
        uc = UseCase(uc_id, description, image, parent_id)
        session.add(uc)


def delete_use_case(uc_id):
    with db.get_session() as session:
        session.query(UseCase).filter(UseCase.uc_id == uc_id).delete()
        session.execute('UPDATE UseCases SET parent_id = NULL '
                'WHERE parent_id = :uc_id', {'uc_id': uc_id})
        session.execute('DELETE FROM UseCasesRequirements '
                'WHERE uc_id = :uc_id', {'uc_id': uc_id})


def get_all_use_case_ids():
    with db.get_session() as session:
        return [e[0] for e in session.query(UseCase.uc_id)]


def get_all_uc_names_and_descriptions():
    with db.get_session() as session:
        return [{'id': uc[0], 'description': uc[1]}
                for uc in session.query(UseCase.uc_id, UseCase.description)]


def get_use_case(uc_id):
    with db.get_session() as session:
        uc = session.query(UseCase).filter(UseCase.uc_id == uc_id).scalar()
        session.expunge_all()
        return uc


def get_top_level_use_case_ids():
    with db.get_session() as session:
        return [uc[0] for uc in
                session.query(UseCase.uc_id).filter(
                UseCase.parent_id == None).order_by(UseCase.uc_id)]


def get_use_case_children_ids(uc_id):
    with db.get_session() as session:
        return [uc[0] for uc in
                session.query(UseCase.uc_id).filter(
                UseCase.parent_id == uc_id).order_by(UseCase.uc_id)]


def _is_uc_existing(uc_id):
    with db.get_session() as session:
        count = session.query(UseCase).filter(UseCase.uc_id == uc_id).count()
        return count != 0


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

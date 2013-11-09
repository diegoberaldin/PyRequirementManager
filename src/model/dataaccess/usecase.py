# -*- coding: utf-8 -*-

"""A set of functions to perform CRUD operations on system use cases.
"""

from src.model import database as db
from src.model.mapping import UseCase, Requirement


def create_use_case(uc_id, description, image=None, parent_id=None):
    """Creates a new use case with the given ID, description and parent.
    """
    if parent_id and not _is_uc_existing(parent_id):
        raise Exception('Nonexistent parent')
    with db.get_session() as session:
        uc = UseCase(uc_id, description, image, parent_id)
        session.add(uc)


def delete_use_case(uc_id):
    """Deletes the use case with the given ID.
    """
    with db.get_session() as session:
        session.query(UseCase).filter(UseCase.uc_id == uc_id).delete()
        session.execute('UPDATE UseCases SET parent_id = NULL '
                'WHERE parent_id = :uc_id', {'uc_id': uc_id})
        session.execute('DELETE FROM UseCasesRequirements '
                'WHERE uc_id = :uc_id', {'uc_id': uc_id})


def get_all_use_case_ids():
    """Returns a list of all the registered use case IDs.
    """
    with db.get_session() as session:
        return [e[0] for e in session.query(UseCase.uc_id)]


def get_all_uc_names_and_descriptions():
    """Returns a list of dictionaries containing the 'id' and 'description'
    keys that can be used to create a UseCaseListModel for some requirement.
    """
    with db.get_session() as session:
        return [{'id': uc[0], 'description': uc[1]}
                for uc in session.query(UseCase.uc_id, UseCase.description)]


def get_use_case(uc_id):
    """Converts the given use case ID to the corresponding transfer object.
    """
    with db.get_session() as session:
        uc = session.query(UseCase).filter(UseCase.uc_id == uc_id).scalar()
        session.expunge_all()
        return uc


def get_top_level_use_case_ids():
    """Returns a list of all those use case IDs corresponding to items that
    have no parent (top level items).
    """
    with db.get_session() as session:
        return [uc[0] for uc in
                session.query(UseCase.uc_id).filter(
                UseCase.parent_id == None).order_by(UseCase.uc_id)]


def get_use_case_children_ids(uc_id):
    """Returns the list of use case ID corresponding to the children of the
    use case with the given ID (empty list if it has no children at all).
    """
    with db.get_session() as session:
        return [uc[0] for uc in
                session.query(UseCase.uc_id).filter(
                UseCase.parent_id == uc_id).order_by(UseCase.uc_id)]


def _is_uc_existing(uc_id):
    """Returns True if a use case with the given ID has already been saved,
    False otherwise.
    """
    with db.get_session() as session:
        count = session.query(UseCase).filter(UseCase.uc_id == uc_id).count()
        return count != 0


def update_use_case_associations(uc_id, newly_associated_requirements):
    """Updates the association between use case and requirement starting from
    the ID of the base use case and a list of IDs of the requirements involved.
    It determines which entries must be added to and which must be removed from
    the association table and updates its content accordingly.
    """
    with db.get_session() as session:
        uc = session.query(UseCase).filter(UseCase.uc_id == uc_id).one()
        newly_associated_requirements = set(newly_associated_requirements)
        associated_requirements = set([req.req_id for req in uc.requirements])
        # determines entries to be added
        ids_to_add = newly_associated_requirements - associated_requirements
        for req_id in ids_to_add:
            req = session.query(Requirement).filter(
                    Requirement.req_id == req_id).one()
            uc.requirements.append(req)
        # determines entries to be removed
        ids_to_remove = associated_requirements - newly_associated_requirements
        for req_id in ids_to_remove:
            req = session.query(Requirement).filter(
                    Requirement.req_id == req_id).one()
            uc.requirements.remove(req)


def update_use_case_description(uc_id, description):
    """Updates the description of the use case with the given ID.
    """
    with db.get_session() as session:
        uc = session.query(UseCase).filter(UseCase.uc_id == uc_id).one()
        uc.description = description


def update_use_case_id(uc_id, new_uc_id):
    """Updates the use case ID to a new value, raising IntegrityError if the
    operation cannot be performed due to primary key conflicts.
    """
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
    """Reassign the use case with the given ID to the new parent corresponding
    to the given parent ID.
    """
    with db.get_session() as session:
        uc = session.query(UseCase).filter(UseCase.uc_id == uc_id).one()
        uc.parent_id = parent_id

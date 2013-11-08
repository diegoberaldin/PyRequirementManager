# -*- coding: utf-8 -*-

"""This module contains the main application controller and the event handler
functions that are used to react to inputs coming from the user interface.
Most of these functions are simple proxies that redirect the operation to the
model data access layer, decoupling its structure from the user interface.
"""

from contextlib import contextmanager

from PySide import QtCore
from sqlalchemy.exc import SQLAlchemyError

from src import model as mdl, gui


class ApplicationController(QtCore.QObject):
    """This object acts as an observer on the user interface and reacts to the
    events originating from it. Its handle_event public slot then redirects the
    event to the proper handler function.
    """
    def __init__(self):
        super(ApplicationController, self).__init__()

    @QtCore.Slot(str, dict)
    def handle_event(self, event_name, params):
        """Call the correct handler within this module, appending _handle_ to
        the name of the event to obtain the conventional event handler name.
        """
        function_name = '_handle_{0}'.format(event_name)
        if function_name in globals():
            globals()[function_name](**params)


@contextmanager
def _extreme_caution():
    """This is used to display informative messages on the UI when naming
    conflicts are detected at the data persistence level.
    """
    try:
        yield
    except SQLAlchemyError as exc:
        gui.get_main_window().display_message(exc.message)


def _handle_create_requirement(data):
    """Creates a new requirement and resets the requirement model.
    """
    with _extreme_caution():
        mdl.dal.create_requirement(**data)
        mdl.get_requirement_model().append_child_to_parent(
                data['req_id'], data['parent_id'])


def _handle_create_source(data):
    """Creates a new requirement source.
    """
    with _extreme_caution():
        mdl.dal.create_source(**data)
        new_source_id = mdl.dal.get_source_id(data['source_name'])
        mdl.get_source_model().append_child_to_parent(new_source_id)


def _handle_create_test(data):
    """Creates a new test and resets the test model.
    """
    with _extreme_caution():
        mdl.dal.create_test(**data)
        mdl.get_test_model().append_child_to_parent(
                data['test_id'], data['parent_id'])


def _handle_create_use_case(data):
    """Creates a new use case and resets the use case model.
    """
    with _extreme_caution():
        mdl.dal.create_uc(**data)
        mdl.get_use_case_model().append_child_to_parent(
                data['uc_id'], data['parent_id'])


def _handle_delete_requirement(req_id):
    """Deletes a requirement and rebuilds all models basing on the DB content.
    """
    mdl.dal.delete_requirement(req_id)
    mdl.get_requirement_model().delete_item(req_id)


def _handle_delete_source(source_id):
    """Deletes the source with the given source ID.
    """
    with _extreme_caution():
        mdl.dal.delete_source(source_id)
        mdl.get_source_model().delete_item(source_id)


def _handle_delete_test(test_id):
    """Deletes a test and rebuilds all models basing on the DB content.
    """
    mdl.dal.delete_test(test_id)
    mdl.get_test_model().delete_item(test_id)


def _handle_delete_use_case(uc_id):
    """Deletes a use case and rebuilds all models basing on the DB content.
    """
    mdl.dal.delete_uc(uc_id)
    mdl.get_use_case_model().delete_item(uc_id)


def _handle_update_requirement_associations(req_id, newly_associated_use_cases,
        newly_associated_tests):
    """Updates the use case and test associations for the given requirement.
    """
    mdl.dal.update_requirement_associations(req_id, newly_associated_use_cases,
        newly_associated_tests)


def _handle_update_requirement_description(req_id, description):
    """Updates the descriptions for the requirement with the given ID.
    """
    mdl.dal.update_requirement_description(req_id, description)


def _handle_update_requirement_id(req_id, new_req_id):
    """Allows requirements to change their ID (with cascading).
    """
    with _extreme_caution():
        mdl.dal.update_requirement_id(req_id, new_req_id)
        mdl.get_requirement_model().update_item_id(req_id, new_req_id)


def _handle_update_requirement_parent_id(req_id, parent_id):
    """Updates the parent ID of the requirement with the given ID.
    """
    mdl.dal.update_requirement_parent_id(req_id, parent_id)
    mdl.get_requirement_model().update_item_parent(req_id, parent_id)


def _handle_update_requirement_priority(req_id, priority):
    """Updates the priority level of the requirement with the given ID.
    """
    mdl.dal.update_requirement_priority(req_id, priority)


def _handle_update_source_name(source_id, source_name):
    """Updates the name of the source with the given ID number.
    """
    with _extreme_caution():
        mdl.dal.update_source_name(source_id, source_name)


def _handle_update_requirement_source(req_id, source_name):
    """Updates the source of the requirement with the given ID.
    """
    mdl.dal.update_requirement_source(req_id, source_name)


def _handle_update_requirement_type(req_id, req_type):
    """Updates the type of the requirement with the given ID.
    """
    mdl.dal.update_requirement_type(req_id, req_type)


def _handle_update_test_associations(test_id, newly_associated_requirements):
    """Updates the requirement associations for the test with the given ID.
    """
    mdl.dal.update_test_associations(test_id, newly_associated_requirements)


def _handle_update_test_description(test_id, description):
    """Updates the description of the test with the given ID.
    """
    mdl.dal.update_test_description(test_id, description)


def _handle_update_test_id(test_id, new_test_id):
    """Allows tests to change their ID (with cascading).
    """
    with _extreme_caution():
        mdl.dal.update_test_id(test_id, new_test_id)
        mdl.get_test_model().update_item_id(test_id, new_test_id)


def _handle_update_use_case_associations(uc_id, newly_associated_requirements):
    """Updates the requirement associations for the use case with the given ID.
    """
    mdl.dal.update_use_case_associations(uc_id, newly_associated_requirements)


def _handle_update_use_case_description(uc_id, description):
    """Updates the description of the use case with the given ID.
    """
    mdl.dal.update_use_case_description(uc_id, description)


def _handle_update_use_case_id(uc_id, new_uc_id):
    """Allows uses cases to change their ID (with cascading)
    """
    with _extreme_caution():
        mdl.dal.update_use_case_id(uc_id, new_uc_id)
        mdl.get_use_case_model().update_item_id(uc_id, new_uc_id)


def _handle_update_use_case_parent_id(uc_id, parent_id):
    """Updates the parent ID of a given use case.
    """
    mdl.dal.update_use_case_parent_id(uc_id, parent_id)
    mdl.get_use_case_model().update_item_parent(uc_id, parent_id)

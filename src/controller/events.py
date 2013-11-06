# -*- coding: utf-8 -*-

"""This module contains the main application controller and the event handler
functions that are used to react to inputs coming from the user interface.
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
    try:
        yield
    except SQLAlchemyError as exc:
        gui.get_main_window().display_message(exc.message)


def _handle_create_requirement(data):
    """Creates a new requirement and resets the requirement model.
    """
    with _extreme_caution():
        mdl.dal.create_requirement(**data)
        mdl.get_requirement_model().initialize()


def _handle_create_test(data):
    """Creates a new test and resets the test model.
    """
    with _extreme_caution():
        mdl.dal.create_test(**data)
        mdl.get_test_model().initialize()


def _handle_create_use_case(data):
    """Creates a new use case and resets the use case model.
    """
    with _extreme_caution():
        mdl.dal.create_uc(**data)
        mdl.get_use_case_model().initialize()


def _handle_delete_requirement(req_id):
    """Deletes a requirement and rebuilds all models basing on the DB content.
    """
    mdl.dal.delete_requirement(req_id)
    mdl.get_requirement_model().initialize()


def _handle_delete_test(test_id):
    """Deletes a test and rebuilds all models basing on the DB content.
    """
    mdl.dal.delete_test(test_id)
    mdl.get_test_model().initialize()


def _handle_delete_use_case(uc_id):
    """Deletes a use case and rebuilds all models basing on the DB content.
    """
    mdl.dal.delete_uc(uc_id)
    mdl.get_use_case_model().initialize()


def _handle_update_requirement_associations(req_id, newly_associated_use_cases,
        newly_associated_tests):
    mdl.dal.update_requirement_associations(req_id, newly_associated_use_cases,
        newly_associated_tests)


def _handle_update_requirement_description(req_id, description):
    mdl.dal.update_requirement_description(req_id, description)


def _handle_update_requirement_id(req_id, new_req_id):
    with _extreme_caution():
        mdl.dal.update_requirement_id(req_id, new_req_id)
        mdl.get_requirement_model().initialize()


def _handle_update_requirement_parent_id(req_id, parent_id):
    mdl.dal.update_requirement_parent_id(req_id, parent_id)
    mdl.get_requirement_model().initialize()


def _handle_update_requirement_priority(req_id, priority):
    mdl.dal.update_requirement_priority(req_id, priority)


def _handle_update_requirement_source(req_id, source_name):
    mdl.dal.update_requirement_source(req_id, source_name)


def _handle_update_requirement_type(req_id, req_type):
    mdl.dal.update_requirement_type(req_id, req_type)


def _handle_update_test_associations(test_id, newly_associated_requirements):
    mdl.dal.update_test_associations(test_id, newly_associated_requirements)


def _handle_update_test_description(test_id, description):
    mdl.dal.update_test_description(test_id, description)


def _handle_update_test_id(test_id, new_test_id):
    with _extreme_caution():
        mdl.dal.update_test_id(test_id, new_test_id)
        mdl.get_test_model().initialize()


def _handle_update_use_case_associations(uc_id, newly_associated_requirements):
    mdl.dal.update_use_case_associations(uc_id, newly_associated_requirements)


def _handle_update_use_case_description(uc_id, description):
    mdl.dal.update_use_case_description(uc_id, description)


def _handle_update_use_case_id(uc_id, new_uc_id):
    with _extreme_caution():
        mdl.dal.update_use_case_id(uc_id, new_uc_id)
        mdl.get_use_case_model().initialize()


def _handle_update_use_case_parent_id(uc_id, parent_id):
    mdl.dal.update_use_case_parent_id(uc_id, parent_id)
    mdl.get_use_case_model().initialize()

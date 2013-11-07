# -*- coding: utf-8 -*-

"""This package corresponds to the business model, it exposes the data access
layer for the controller to interact with and a set of read-only functions that
are needed by the UI to query the model for information.
"""

# expose data access layer
from src.model import dataaccess as dal
# expose constants
from src.model.constants import TYPE_LIST, PRIORITY_LIST
# read-only functions for the views
from src.model.dataaccess import (get_all_req_ids, get_all_uc_ids,
    get_all_test_ids, get_all_source_names, get_source_id)
# required by the controller at startup
from src.model.database import initialize_db
# these are needed to bind the views to their data model
from src.model.qtbind import (get_requirement_model, get_use_case_model,
    get_test_model, get_use_case_list_model, get_test_list_model,
    get_requirement_list_model)

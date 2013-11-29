# -*- coding: utf-8 -*-

"""This package contains the basic data access layer of the application, i.e. a
simple API that is offered to the UI *to query* the model about business data
state (and relationships) and to the controller *to modify* the data. This
package is intended to be used as an abstraction from the underlying data
persistence subsystem, it should only depend on transfer object (mapping) and
with the database session manager.
"""

from src.model.dataaccess.requirement import (create_requirement,
    delete_requirement, get_all_requirement_ids, get_requirement,
    get_all_requirement_names_and_descriptions, get_requirement_children_ids,
    get_top_level_requirement_ids, update_requirement_associations,
    update_requirement_description, update_requirement_id,
    update_requirement_parent_id, update_requirement_priority,
    update_requirement_source, update_requirement_type,
    get_all_requirement_ids_spec)
from src.model.dataaccess.source import (create_source, delete_source,
    get_all_source_ids, get_all_source_names, get_source, get_source_id,
    update_source_name)
from src.model.dataaccess.test import (create_test, delete_test, get_test,
    update_test_description, update_test_id, get_all_test_ids,
    get_all_test_names_and_descriptions, update_test_associations)
from src.model.dataaccess.usecase import (create_use_case, delete_use_case,
    get_all_use_case_ids, get_all_uc_names_and_descriptions, get_use_case,
    get_use_case_children_ids, get_top_level_use_case_ids, update_use_case_id,
    update_use_case_associations, update_use_case_description,
    update_use_case_parent_id, get_use_case_associated_requirements)

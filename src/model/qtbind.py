# -*- coding: utf-8 -*-

from PySide import QtCore

from src.model import dal


# single instance of the requirement model
_reqm = None
# single instance of the test model
_testm = None
# single instance of the use case model
_ucm = None


def get_requirement_model():
    """Returns a reference to the single instance of the requirement model.
    """
    global _reqm
    if not _reqm:
        _reqm = RequirementModel()
    return _reqm


def get_test_model():
    """Returns a reference to the single instance of the test model.
    """
    global _testm
    if not _testm:
        _testm = TestModel()
    return _testm


def get_use_case_model():
    """Returns a reference to the single instance of the use case model.
    """
    global _ucm
    if not _ucm:
        _ucm = UseCaseModel()
    return _ucm


def get_use_case_list_model(requirement):
    return UseCaseListModel(requirement)


def get_test_list_model(requirement):
    return TestListModel(requirement)


def get_requirement_list_model(item):
    return RequirementListModel(item)


class RequirementModel(QtCore.QAbstractItemModel):
    """Abstract item model subclass used to represent the tree of requirements.
    """
    def __init__(self):
        super(RequirementModel, self).__init__()
        self._requirements = []
        self.initialize()

    def initialize(self):
        """Rebuilds the internal list of requirements based on the DB.
        """
        self.beginResetModel()
        self._requirements = dal.get_requirements()
        self.endResetModel()

    def flags(self, index=QtCore.QModelIndex()):
        if not index.isValid():
            return QtCore.Qt.ItemIsEnabled
        return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable

    def headerData(self, section, orientation, role=QtCore.Qt.DisplayRole):
        if (role == QtCore.Qt.DisplayRole and
                orientation == QtCore.Qt.Horizontal):
            if section == 0:
                return 'Nome'

    def index(self, row, column, parent=QtCore.QModelIndex()):
        if not self.hasIndex(row, column, parent):
            return QtCore.QModelIndex()
        item = parent.internalPointer()
        if not item:
            return self.createIndex(row, column, self._requirements[row])
        if column < self.columnCount() and row < len(item.children):
            return self.createIndex(row, column, item.children[row])

    def parent(self, index=QtCore.QModelIndex()):
        if not index.isValid():
            return QtCore.QModelIndex()
        item = index.internalPointer()
        parent = item.parent
        if not parent:
            return QtCore.QModelIndex()
        row = parent.children.index(item)
        return self.createIndex(row, 0, parent)

    def rowCount(self, parent=QtCore.QModelIndex()):
        if not parent.isValid():
            return len(self._requirements)
        item = parent.internalPointer()
        return len(item.children)

    def columnCount(self, unused_parent=QtCore.QModelIndex()):
        return 1

    def data(self, index=QtCore.QModelIndex(), role=QtCore.Qt.DisplayRole):
        if index.isValid() and role == QtCore.Qt.DisplayRole:
            section = index.column()
            item = index.internalPointer()
            if section == 0:
                return item.req_id


class UseCaseModel(QtCore.QAbstractItemModel):
    """Abstract item model subclass used to represent the tree of use cases.
    """
    def __init__(self):
        super(UseCaseModel, self).__init__()
        self._use_cases = []
        self.initialize()

    def initialize(self):
        """Rebuilds the internal list of use cases based on the DB.
        """
        self.beginResetModel()
        self._use_cases = dal.get_ucs()
        self.endResetModel()

    def flags(self, index=QtCore.QModelIndex()):
        if not index.isValid():
            return QtCore.Qt.ItemIsEnabled
        return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable

    def headerData(self, section, orientation, role=QtCore.Qt.DisplayRole):
        if (role == QtCore.Qt.DisplayRole and
                orientation == QtCore.Qt.Horizontal):
            if section == 0:
                return 'Nome'

    def index(self, row, column, parent=QtCore.QModelIndex()):
        if not self.hasIndex(row, column, parent):
            return QtCore.QModelIndex()
        item = parent.internalPointer()
        if not item:
            return self.createIndex(row, column, self._use_cases[row])
        if column < self.columnCount() and row < len(item.children):
            return self.createIndex(row, column, item.children[row])

    def parent(self, index=QtCore.QModelIndex()):
        if not index.isValid():
            return QtCore.QModelIndex()
        item = index.internalPointer()
        parent = item.parent
        if not parent:
            return QtCore.QModelIndex()
        row = parent.children.index(item)
        return self.createIndex(row, 0, parent)

    def rowCount(self, parent=QtCore.QModelIndex()):
        if not parent.isValid():
            return len(self._use_cases)
        if parent.column() > 0:
            return 0
        item = parent.internalPointer()
        return len(item.children)

    def columnCount(self, unused_parent=QtCore.QModelIndex()):
        return 1

    def data(self, index=QtCore.QModelIndex(), role=QtCore.Qt.DisplayRole):
        if index.isValid() and role == QtCore.Qt.DisplayRole:
            section = index.column()
            item = index.internalPointer()
            if section == 0:
                return item.uc_id


class TestModel(QtCore.QAbstractItemModel):
    """Abstract item model subclass used to represent the list of system tests.
    """
    def __init__(self):
        super(TestModel, self).__init__()
        self._tests = []
        self.initialize()

    def initialize(self):
        """Rebuilds the internal list of system tests based on the DB.
        """
        self.beginResetModel()
        self._tests = dal.get_tests()
        self.endResetModel()

    def flags(self, index=QtCore.QModelIndex()):
        if not index.isValid():
            return QtCore.Qt.ItemIsEnabled
        return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable

    def headerData(self, section, orientation, role=QtCore.Qt.DisplayRole):
        if (role == QtCore.Qt.DisplayRole and
                orientation == QtCore.Qt.Horizontal):
            if section == 0:
                return 'Nome'

    def index(self, row, column, parent=QtCore.QModelIndex()):
        if not self.hasIndex(row, column, parent):
            return QtCore.QModelIndex()
        if column < self.columnCount() and row < len(self._tests):
            return self.createIndex(row, column, self._tests[row])
        return QtCore.QModelIndex()

    def parent(self, index=QtCore.QModelIndex()):
        if not index.isValid() or index.internalPointer() is None:
            return QtCore.QModelIndex()
        item = index.internalPointer()
        row = self._tests.index(item)
        return self.createIndex(row, 0, None)

    def rowCount(self, parent=QtCore.QModelIndex()):
        if not parent.isValid() or parent.internalPointer() is None:
            return len(self._tests)
        return 0

    def columnCount(self, unused_parent=QtCore.QModelIndex()):
        return 1

    def data(self, index=QtCore.QModelIndex(), role=QtCore.Qt.DisplayRole):
        if index.isValid() and role == QtCore.Qt.DisplayRole:
            section = index.column()
            item = index.internalPointer()
            if section == 0:
                return item.test_id


class UseCaseListModel(QtCore.QAbstractItemModel):
    def __init__(self, item):
        super(UseCaseListModel, self).__init__()
        self._uc_data_list = dal.get_all_uc_name_and_description()
        self.associated_uc_ids = [uc.uc_id for uc in item.use_cases]

    def flags(self, index=QtCore.QModelIndex()):
        if not index.isValid():
            return QtCore.Qt.ItemIsEnabled
        return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsUserCheckable

    def headerData(self, section, orientation, role=QtCore.Qt.DisplayRole):
        if (role == QtCore.Qt.DisplayRole and
                orientation == QtCore.Qt.Horizontal):
            if section == 0:
                return u'Nome'
            if section == 1:
                return u'Descrizione'
            if section == 2:
                return u'Associato'

    def rowCount(self, index=QtCore.QModelIndex()):
        if index.internalPointer() in self._uc_data_list:
            return 0
        return len(self._uc_data_list)

    def columnCount(self, unused_index=QtCore.QModelIndex()):
        return 3

    def index(self, row, column, unused_parent=QtCore.QModelIndex()):
        return self.createIndex(row, column, self._uc_data_list[row])

    def parent(self, unused_index=QtCore.QModelIndex()):
        return QtCore.QModelIndex()

    def data(self, index=QtCore.QModelIndex(), role=QtCore.Qt.DisplayRole):
        uc_item = index.internalPointer()
        section = index.column()
        if role == QtCore.Qt.DisplayRole:
            if section == 0:
                return uc_item['uc_id']
            if section == 1:
                return uc_item['description']
        if role == QtCore.Qt.CheckStateRole:
            if section == 2:
                if uc_item['uc_id'] in self.associated_uc_ids:
                    return QtCore.Qt.Checked
                return QtCore.Qt.Unchecked

    def setData(self, index, value, role):
        section = index.column()
        uc_id = index.internalPointer()['uc_id']
        if role == QtCore.Qt.CheckStateRole and section == 2:
            if (value == QtCore.Qt.Checked and
                    uc_id not in self.associated_uc_ids):
                self.associated_uc_ids.append(uc_id)
                self.dataChanged.emit(index, index)
                return True
            if (value == QtCore.Qt.Unchecked and
                    uc_id in self.associated_uc_ids):
                self.associated_uc_ids.remove(uc_id)
                self.dataChanged.emit(index, index)
                return True
        return False


class TestListModel(QtCore.QAbstractItemModel):
    def __init__(self, item):
        super(TestListModel, self).__init__()
        self._test_data_list = dal.get_all_test_name_and_description()
        self.associated_test_ids = [test.test_id for test in item.tests]

    def flags(self, index=QtCore.QModelIndex()):
        if not index.isValid():
            return QtCore.Qt.ItemIsEnabled
        return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsUserCheckable

    def headerData(self, section, orientation, role=QtCore.Qt.DisplayRole):
        if (role == QtCore.Qt.DisplayRole and
                orientation == QtCore.Qt.Horizontal):
            if section == 0:
                return u'Nome'
            if section == 1:
                return u'Descrizione'
            if section == 2:
                return u'Associato'

    def rowCount(self, index=QtCore.QModelIndex()):
        if index.internalPointer() in self._test_data_list:
            return 0
        return len(self._test_data_list)

    def columnCount(self, unused_index=QtCore.QModelIndex()):
        return 3

    def index(self, row, column, unused_parent=QtCore.QModelIndex()):
        return self.createIndex(row, column, self._test_data_list[row])

    def parent(self, unused_index=QtCore.QModelIndex()):
        return QtCore.QModelIndex()

    def data(self, index=QtCore.QModelIndex(), role=QtCore.Qt.DisplayRole):
        test_item = index.internalPointer()
        section = index.column()
        if role == QtCore.Qt.DisplayRole:
            if section == 0:
                return test_item['test_id']
            if section == 1:
                return test_item['description']
        if role == QtCore.Qt.CheckStateRole:
            if section == 2:
                if test_item['test_id'] in self.associated_test_ids:
                    return QtCore.Qt.Checked
                return QtCore.Qt.Unchecked

    def setData(self, index, value, role):
        section = index.column()
        test_id = index.internalPointer()['test_id']
        if role == QtCore.Qt.CheckStateRole and section == 2:
            if (value == QtCore.Qt.Checked and
                    test_id not in self.associated_test_ids):
                self.associated_test_ids.append(test_id)
                self.dataChanged.emit(index, index)
                return True
            if (value == QtCore.Qt.Unchecked and
                    test_id in self.associated_test_ids):
                self.associated_test_ids.remove(test_id)
                self.dataChanged.emit(index, index)
                return True
        return False


class RequirementListModel(QtCore.QAbstractItemModel):
    def __init__(self, item):
        super(RequirementListModel, self).__init__()
        self._req_data_list = dal.get_all_requirement_name_and_description()
        self.associated_req_ids = [req.req_id for req in item.requirements]

    def flags(self, index=QtCore.QModelIndex()):
        if not index.isValid():
            return QtCore.Qt.ItemIsEnabled
        return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsUserCheckable

    def headerData(self, section, orientation, role=QtCore.Qt.DisplayRole):
        if (role == QtCore.Qt.DisplayRole and
                orientation == QtCore.Qt.Horizontal):
            if section == 0:
                return u'Nome'
            if section == 1:
                return u'Descrizione'
            if section == 2:
                return u'Associato'

    def rowCount(self, index=QtCore.QModelIndex()):
        if index.internalPointer() in self._req_data_list:
            return 0
        return len(self._req_data_list)

    def columnCount(self, unused_index=QtCore.QModelIndex()):
        return 3

    def index(self, row, column, unused_parent=QtCore.QModelIndex()):
        return self.createIndex(row, column, self._req_data_list[row])

    def parent(self, unused_index=QtCore.QModelIndex()):
        return QtCore.QModelIndex()

    def data(self, index=QtCore.QModelIndex(), role=QtCore.Qt.DisplayRole):
        req_item = index.internalPointer()
        section = index.column()
        if role == QtCore.Qt.DisplayRole:
            if section == 0:
                return req_item['req_id']
            if section == 1:
                return req_item['description']
        if role == QtCore.Qt.CheckStateRole:
            if section == 2:
                if req_item['req_id'] in self.associated_req_ids:
                    return QtCore.Qt.Checked
                return QtCore.Qt.Unchecked

    def setData(self, index, value, role):
        section = index.column()
        req_id = index.internalPointer()['req_id']
        if role == QtCore.Qt.CheckStateRole and section == 2:
            if (value == QtCore.Qt.Checked and
                    req_id not in self.associated_req_ids):
                self.associated_req_ids.append(req_id)
                self.dataChanged.emit(index, index)
                return True
            if (value == QtCore.Qt.Unchecked and
                    req_id in self.associated_req_ids):
                self.associated_req_ids.remove(req_id)
                self.dataChanged.emit(index, index)
                return True
        return False

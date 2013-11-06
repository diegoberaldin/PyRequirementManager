# -*- coding: utf-8 -*-

from PySide import QtCore

from src.model import dal


# single instance of the requirement model
_reqm = None
# single instance of the test model
_testm = None
# single instance of the use case model
_ucm = None


class ItemNode(object):
    def __init__(self, item_id, parent):
        self.item_id = item_id
        self.children = []
        self.parent = parent


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


class ItemModel(QtCore.QAbstractItemModel):
    """Abstract item model subclass used to represent a forest of items.
    """
    def __init__(self):
        super(ItemModel, self).__init__()
        self._item_forest = []
        self.initialize()

    @classmethod
    def _generate_tree(cls, item_id, parent_id=None):
        item = ItemNode(item_id, parent_id)
        children_list = cls._get_children(item_id)
        for child_id in children_list:
            item.children.append(cls._generate_tree(child_id, item))
        return item

    @classmethod
    def _get_children(cls, item_id):
        raise NotImplementedError('Implement me!')

    @classmethod
    def _get_top_level_items(cls):
        raise NotImplementedError('Implement me!')

    def initialize(self):
        """Rebuilds the internal data structure based on the DB.
        """
        self.beginResetModel()
        self._item_forest = []
        for item_id in self._get_top_level_items():
            # creates the forest as a list of trees
            self._item_forest.append(self._generate_tree(item_id))
        self.endResetModel()

    def flags(self, index=QtCore.QModelIndex()):
        if not index.isValid():
            return QtCore.Qt.ItemIsEnabled
        return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable

    def headerData(self, section, orientation, role=QtCore.Qt.DisplayRole):
        if (role == QtCore.Qt.DisplayRole and
                orientation == QtCore.Qt.Horizontal):
            if section == 0:
                return u'Nome'

    def index(self, row, column, parent=QtCore.QModelIndex()):
        if not self.hasIndex(row, column, parent):
            return QtCore.QModelIndex()
        item = parent.internalPointer()
        if not item:
            return self.createIndex(row, column, self._item_forest[row])
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
            return len(self._item_forest)
        item = parent.internalPointer()
        return len(item.children)

    def columnCount(self, unused_parent=QtCore.QModelIndex()):
        return 1

    def data(self, index=QtCore.QModelIndex(), role=QtCore.Qt.DisplayRole):
        if index.isValid() and role == QtCore.Qt.DisplayRole:
            section = index.column()
            item = index.internalPointer()
            if section == 0:
                return item.item_id


class RequirementModel(ItemModel):
    def __init__(self):
        super(RequirementModel, self).__init__()

    @classmethod
    def _get_children(cls, item_id):
        return dal.get_requirement_children_ids(item_id)

    @classmethod
    def _get_top_level_items(cls):
        return dal.get_top_level_requirement_ids()


class UseCaseModel(ItemModel):
    def __init__(self):
        super(UseCaseModel, self).__init__()

    @classmethod
    def _get_children(cls, item_id):
        return dal.get_use_case_children_ids(item_id)

    @classmethod
    def _get_top_level_items(cls):
        return dal.get_top_level_use_case_ids()


class TestModel(ItemModel):
    """Abstract item model subclass used to represent the list of system tests.
    """
    def __init__(self):
        super(TestModel, self).__init__()

    @classmethod
    def _get_children(cls, unused_item_id):
        return []

    @classmethod
    def _get_top_level_items(cls):
        return dal.get_top_level_test_ids()


class ItemListModel(QtCore.QAbstractItemModel):
    def __init__(self, item):
        super(ItemListModel, self).__init__()
        self._item_data_list = self._get_item_names_and_descriptions()
        self.associated_item_ids = self._get_associated_item_ids(item)

    @classmethod
    def _get_item_names_and_descriptions(cls):
        raise NotImplementedError('Implement me!')

    @classmethod
    def _get_associated_item_ids(cls, item):
        raise NotImplementedError('Implement me!')

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
        if index.internalPointer() in self._item_data_list:
            return 0
        return len(self._item_data_list)

    def columnCount(self, unused_index=QtCore.QModelIndex()):
        return 3

    def index(self, row, column, unused_parent=QtCore.QModelIndex()):
        return self.createIndex(row, column, self._item_data_list[row])

    def parent(self, unused_index=QtCore.QModelIndex()):
        return QtCore.QModelIndex()

    def data(self, index=QtCore.QModelIndex(), role=QtCore.Qt.DisplayRole):
        item_data = index.internalPointer()
        section = index.column()
        if role == QtCore.Qt.DisplayRole:
            if section == 0:
                return item_data['id']
            if section == 1:
                return item_data['description']
        if role == QtCore.Qt.CheckStateRole:
            if section == 2:
                if item_data['id'] in self.associated_item_ids:
                    return QtCore.Qt.Checked
                return QtCore.Qt.Unchecked

    def setData(self, index, value, role):
        section = index.column()
        item_id = index.internalPointer()['id']
        if role == QtCore.Qt.CheckStateRole and section == 2:
            if (value == QtCore.Qt.Checked and
                    item_id not in self.associated_item_ids):
                self.associated_item_ids.append(item_id)
                self.dataChanged.emit(index, index)
                return True
            if (value == QtCore.Qt.Unchecked and
                    item_id in self.associated_item_ids):
                self.associated_item_ids.remove(item_id)
                self.dataChanged.emit(index, index)
                return True
        return False


class UseCaseListModel(ItemListModel):
    def __init__(self, item):
        super(UseCaseListModel, self).__init__(item)

    @classmethod
    def _get_item_names_and_descriptions(cls):
        return dal.get_all_uc_names_and_descriptions()

    @classmethod
    def _get_associated_item_ids(cls, item):
        return [uc.uc_id for uc in item.use_cases]


class TestListModel(ItemListModel):
    def __init__(self, item):
        super(TestListModel, self).__init__(item)

    @classmethod
    def _get_item_names_and_descriptions(cls):
        return dal.get_all_test_names_and_descriptions()

    @classmethod
    def _get_associated_item_ids(cls, item):
        return [test.test_id for test in item.tests]


class RequirementListModel(ItemListModel):
    def __init__(self, item):
        super(RequirementListModel, self).__init__(item)

    @classmethod
    def _get_item_names_and_descriptions(cls):
        return dal.get_all_requirement_names_and_descriptions()

    @classmethod
    def _get_associated_item_ids(cls, item):
        [req.req_id for req in item.requirements]

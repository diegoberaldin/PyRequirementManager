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
    """This is used to represent an item (requirement, test or use case...) in
    a tree-like data structure with parents an children. These objects are
    used as internal data structures for ItemModels.
    """
    def __init__(self, item_id, parent=None):
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
    """Returns a use case list model for the given requirement.
    """
    return UseCaseListModel(requirement)


def get_test_list_model(requirement):
    """Returns a test list model for the given requirement
    """
    return TestListModel(requirement)


def get_requirement_list_model(item):
    """Returns a requirement list model for the given item (test or use case).
    """
    return RequirementListModel(item)


class ItemModel(QtCore.QAbstractItemModel):
    """Abstract item model subclass used to represent a forest of items.
    """
    def __init__(self):
        super(ItemModel, self).__init__()
        self._item_forest = []
        self.initialize()

    @classmethod
    def _generate_tree(cls, item_id, parent=None):
        """Given an item with the given ID, it recursively generates a tree of
        ItemNodes rooted in the item with the given ID. It internally uses the
        _get_children method to obtain a list of the ID of the item's children.
        """
        item = ItemNode(item_id, parent)
        children_list = cls._get_children(item_id)
        for child_id in children_list:
            item.children.append(cls._generate_tree(child_id, item))
        return item

    @classmethod
    def _get_children(cls, item_id):
        """This hook method should be implemented by subclasses to obtain a
        list of item IDs corresponding to the children of the item with the
        given item ID.
        """
        raise NotImplementedError('Implement me!')

    @classmethod
    def _find_in_tree(cls, item, item_id):
        """Returns a reference to the ItemNode with the given item_id if it is
        found in the tree rooted in the given item, None otherwise.
        """
        if item.item_id == item_id:
            return item
        for child in item.children:
            rv = cls._find_in_tree(child, item_id)
            if rv:  # stop recurring if the desired item has been found
                return rv

    def _search_forest(self, item_id):
        """Search the whole list of trees for a node with the given item ID.
        """
        for tree in self._item_forest:
            rv = self._find_in_tree(tree, item_id)
            if rv:  # stop iterating once the item has been found
                return rv

    def append_child_to_parent(self, item_id, parent_id=None):
        """Appends a new item in the correct place in the model, notifying the
        associated views of the change happened.
        """
        if not parent_id:  # adding a top level item
            child_count = len(self._item_forest)
            parent_index = QtCore.QModelIndex()  # this is the ROOT! :)
            self.beginInsertRows(parent_index, child_count, child_count)
            new_child = ItemNode(item_id)
            self._item_forest.append(new_child)
            self.endInsertRows()
        else:  # adding an item as a leaf in some tree (where the parent is)
            parent = self._search_forest(parent_id)
            parent_index = self.createIndex(0, 0, parent)
            child_count = len(parent.children)
            self.beginInsertRows(parent_index, child_count, child_count)
            new_child = ItemNode(item_id, parent)
            parent.children.append(new_child)
            self.endInsertRows()

    def update_item_id(self, old_id, new_id):
        """Changes the ID of the item with the given old ID to the new one.
        """
        item = self._search_forest(old_id)
        index = self.createIndex(0, 0, item)
        item.item_id = new_id
        self.dataChanged.emit(index, index)

    def delete_item(self, item_id):
        """Deletes an item by removing the data from the structure (notifying
        the view about rows being removed) and, if the item had any children,
        moves them to become top level items (as this is what happens in the
        DB since the parent_id field is set to null).
        """
        item = self._search_forest(item_id)
        index = self.createIndex(0, 0, item)
        parent = item.parent
        parent_index = self.parent(index)
        # remove the item from its parent's children
        if parent:
            row = parent.children.index(item)
        else:
            row = self._item_forest.index(item)
        self.beginRemoveRows(parent_index, row, row)
        if parent:
            parent.children.remove(item)
        else:
            self._item_forest.remove(item)
        self.endRemoveRows()
        # adds the children to the root of the model (they have no parent)
        root_index = QtCore.QModelIndex()
        tree_count = len(self._item_forest)
        self.beginInsertRows(root_index, tree_count,
                tree_count + len(item.children) - 1)
        while item.children:
            child = item.children.pop()
            child.parent = None
            self._item_forest.append(child)
        self.endInsertRows()
        del item

    @classmethod
    def _get_top_level_items(cls):
        """This hook method should be subclassed to obtain a list of those IDs
        corresponding to items which have no parent.
        """
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
        """Returns an integer defining item properties, valid index will always
        point to items that are enabled and selectable.
        """
        if not index.isValid():
            return QtCore.Qt.ItemIsEnabled
        return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable

    def headerData(self, section, orientation, role=QtCore.Qt.DisplayRole):
        """Returns te names of the columns that will be displayed in the view.
        """
        if (role == QtCore.Qt.DisplayRole and
                orientation == QtCore.Qt.Horizontal):
            if section == 0:
                return u'Nome'

    def index(self, row, column, parent=QtCore.QModelIndex()):
        """Allows views to go one step further in the tree starting from
        the parent index, going down from the invisible root to first level
        (i.e. orphaned) items or to some child of a parent item.
        """
        if not self.hasIndex(row, column, parent):
            return QtCore.QModelIndex()
        if not parent.isValid():
            # descending from the tree 'root', so access first level items
            return self.createIndex(row, column, self._item_forest[row])
        children = parent.internalPointer().children
        if column < self.columnCount() and row < len(children):
            # access further level items
            return self.createIndex(row, column, children[row])

    def parent(self, index=QtCore.QModelIndex()):
        """Allows views to go one step backward in the tree structure, i.e.
        obtaining a new index that points to the parent of the current item.
        """
        if not index.isValid():
            return QtCore.QModelIndex()
        item = index.internalPointer()
        parent = item.parent
        if not parent:  # can't go backwards past the root
            return QtCore.QModelIndex()
        row = parent.children.index(item)
        return self.createIndex(row, 0, parent)

    def rowCount(self, parent=QtCore.QModelIndex()):
        """This boils down to the number of children that the item pointed by
        the parent index has or the number of trees in the forest if the index
        corresponds to the 'root' of the model or is invalid.
        """
        if not parent.isValid() or not parent.internalPointer():
            return len(self._item_forest)
        item = parent.internalPointer()
        return len(item.children)

    def columnCount(self, unused_parent=QtCore.QModelIndex()):
        """These models only have one column, no matter what the parent is.
        """
        return 1

    def data(self, index=QtCore.QModelIndex(), role=QtCore.Qt.DisplayRole):
        """Allow views to access the data stored inside the items pointed by
        model indexes, depending on which column the current index has.
        """
        if index.isValid() and role == QtCore.Qt.DisplayRole:
            section = index.column()
            item = index.internalPointer()
            if section == 0:
                return item.item_id


class RequirementModel(ItemModel):
    """This is used to store the requirement forest (list of trees).
    """
    def __init__(self):
        super(RequirementModel, self).__init__()

    @classmethod
    def _get_children(cls, item_id):
        """Returns an iterable with all the children of a given requirement.
        """
        return dal.get_requirement_children_ids(item_id)

    @classmethod
    def _get_top_level_items(cls):
        """Returns an iterable of all those requirements that have no parent.
        """
        return dal.get_top_level_requirement_ids()


class UseCaseModel(ItemModel):
    """This is used to store the use case forest (list of trees).
    """
    def __init__(self):
        super(UseCaseModel, self).__init__()

    @classmethod
    def _get_children(cls, item_id):
        """Returns an iterable with all the children of a given requirement.
        """
        return dal.get_use_case_children_ids(item_id)

    @classmethod
    def _get_top_level_items(cls):
        """Returns an iterable of all those use cases that have no parent.
        """
        return dal.get_top_level_use_case_ids()


class TestModel(ItemModel):
    """Abstract item model subclass used to represent the list of system tests.
    """
    def __init__(self):
        super(TestModel, self).__init__()

    @classmethod
    def _get_children(cls, unused_item_id):
        """Tests have no children (flat model) so this is always an empty list.
        """
        return []

    @classmethod
    def _get_top_level_items(cls):
        """Returns an iterable of all those tests that have no parent.
        """
        return dal.get_top_level_test_ids()


class ItemListModel(QtCore.QAbstractItemModel):
    """This is the base class for all 'flat' models used to represent a list of
    items (requirements, tests or use cases) that are associated to other items
    of the business model (requirements to use cases and vice versa, tests to
    requirements and vice versa).
    """
    def __init__(self, item):
        super(ItemListModel, self).__init__()
        self._item_data_list = self._get_item_names_and_descriptions()
        self.associated_item_ids = self._get_associated_item_ids(item)

    @classmethod
    def _get_item_names_and_descriptions(cls):
        """This must be implemented by subclasses to obtain a sequence of
        dictionaries having the 'id' and 'description' keys which represent
        the items being listed.
        """
        raise NotImplementedError('Implement me!')

    @classmethod
    def _get_associated_item_ids(cls, item):
        """Gets a list of the IDs of those items that are linked to the given
        item, e.g. the list of use case IDs that are linked to a requirement.
        """
        raise NotImplementedError('Implement me!')

    def flags(self, index=QtCore.QModelIndex()):
        """Items of this model are selectable and enabled by default.
        """
        if not index.isValid():
            return QtCore.Qt.ItemIsEnabled
        return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsUserCheckable

    def headerData(self, section, orientation, role=QtCore.Qt.DisplayRole):
        """Provides views with the required information for displaying headers.
        """
        if (role == QtCore.Qt.DisplayRole and
                orientation == QtCore.Qt.Horizontal):
            if section == 0:
                return u'Nome'
            if section == 1:
                return u'Descrizione'
            if section == 2:
                return u'Associato'

    def rowCount(self, index=QtCore.QModelIndex()):
        """Since this is a flat model, indexes pointing to first level items
        have no children, whereas if the index corresponds to the model 'root',
        it has as many children as are the elements in the internal data list.
        """
        if index.internalPointer() in self._item_data_list:
            return 0
        return len(self._item_data_list)

    def columnCount(self, unused_index=QtCore.QModelIndex()):
        """These models have a fixed number of columns.
        """
        return 3

    def index(self, row, column, unused_parent=QtCore.QModelIndex()):
        """The only way to go down in such a model is from the root to one of
        the first level items, so it returns the corresponding index.
        """
        return self.createIndex(row, column, self._item_data_list[row])

    def parent(self, unused_index=QtCore.QModelIndex()):
        """The only way to go up is from a first level item to the model 'root'
        so it returns an invalid index (i.e. an index pointing to the root).
        """
        return QtCore.QModelIndex()

    def data(self, index=QtCore.QModelIndex(), role=QtCore.Qt.DisplayRole):
        """Allow views to access the information that is stored inside the
        dictionaries depending on the column that is being displayed.
        """
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
        """This model is editable to a very limited extent, i.e. only items in
        the third column can be modified by checking or unchecking the
        corresponding checkbox.
        """
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
    """This is used to represent the use cases for a given requirement.
    """
    def __init__(self, item):
        super(UseCaseListModel, self).__init__(item)

    @classmethod
    def _get_item_names_and_descriptions(cls):
        """Returns IDs and descriptions of all uses cases.
        """
        return dal.get_all_uc_names_and_descriptions()

    @classmethod
    def _get_associated_item_ids(cls, item):
        """Returns an iterable containing the IDs of all those use cases that
        are linked to the given requirement item.
        """
        return [uc.uc_id for uc in item.use_cases]


class TestListModel(ItemListModel):
    """This is used to represent the tests for a given requirement.
    """
    def __init__(self, item):
        super(TestListModel, self).__init__(item)

    @classmethod
    def _get_item_names_and_descriptions(cls):
        """Returns IDs and descriptions of all tests.
        """
        return dal.get_all_test_names_and_descriptions()

    @classmethod
    def _get_associated_item_ids(cls, item):
        """Returns an iterable containing the IDs of all those tests that
        are linked to the given requirement item.
        """
        return [test.test_id for test in item.tests]


class RequirementListModel(ItemListModel):
    """This is used to represent the requirement list that can be associated to
    a given use case or to a test.
    """
    def __init__(self, item):
        super(RequirementListModel, self).__init__(item)

    @classmethod
    def _get_item_names_and_descriptions(cls):
        """Returns IDs and descriptions of all requirements.
        """
        return dal.get_all_requirement_names_and_descriptions()

    @classmethod
    def _get_associated_item_ids(cls, item):
        """Returns an iterable containing the IDs of all those requirements
        that are linked to the given item (either a use case or a test).
        """
        [req.req_id for req in item.requirements]

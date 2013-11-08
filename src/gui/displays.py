# -*- coding: utf-8 -*-

from PySide import QtCore, QtGui

from src import model as mdl
from src.gui.util import EnumTranslator


# size of the first column in embedded views
_1ST_COLUMN_WIDTH = 100
# size of the second column in embedded views
_2ND_COLUMN_WIDTH = 400
# size of the third column in embedded views
_3RD_COLUMN_WIDTH = 50


class ItemDisplay(QtGui.QWidget):
    """Base class for those widget which are used to display items in the
    central area of the window, it contains the hook methods which subclassed
    should override in order to behave properly.
    """
    # signal used to inform the parent that some content has been modified
    content_changed = QtCore.Signal()
    # signal used to inform the controller about new events
    fire_event = QtCore.Signal(str, dict)

    def __init__(self, item=None, parent=None):
        super(ItemDisplay, self).__init__(parent)
        self.item = item
        self.setLayout(QtGui.QFormLayout(self))
        self._create_content()

    def _create_content(self):
        """Creates the content of the widget (grid of label and input fields).
        """
        pass

    def save(self):
        """Makes the data persistent by dispatching the correct events.
        """
        pass

    @QtCore.Slot(QtCore.QModelIndex)
    def _handle_view_pressed(self, index):
        """Informs the parent widget (observer) that a checkbox has been
        toggled so the content of the display has changed and needs to be
        saved in order to become persistent.
        """
        if index.column() == 2:
            self.content_changed.emit()


class RequirementDisplay(ItemDisplay):
    """Widget which is used to display a requirement in the central area.
    """
    def __init__(self, requirement, parent):
        super(RequirementDisplay, self).__init__(requirement, parent)

    def _create_content(self):
        """Creates the form that is shown in the requirement display.
        """
        et = EnumTranslator()
        # form fields
        name_label = QtGui.QLabel(self.tr('Name'), self)
        self._name_input = QtGui.QLineEdit(self)
        self._name_input.setText(self.item.req_id)
        description_label = QtGui.QLabel(self.tr('Description'), self)
        self._description_input = QtGui.QPlainTextEdit(self)
        self._description_input.setPlainText(self.item.description)
        priority_label = QtGui.QLabel(self.tr('Priority'), self)
        self._priority_input = QtGui.QComboBox(self)
        self._priority_input.setModel(et.get_translated_priority_list_model())
        self._priority_input.setCurrentIndex(
                mdl.PRIORITY_LIST.index(self.item.priority))
        type_label = QtGui.QLabel(self.tr('Type'), self)
        self._type_input = QtGui.QComboBox(self)
        self._type_input.setModel(et.get_translated_type_list_model())
        self._type_input.setCurrentIndex(
                mdl.TYPE_LIST.index(self.item.req_type))
        source_label = QtGui.QLabel(self.tr('Source'), self)
        self._source_input = QtGui.QComboBox(self)
        sources = mdl.get_all_source_names()
        self._source_input.setModel(
                QtGui.QStringListModel(sources))
        self._source_input.setCurrentIndex(
                sources.index(self.item.source.name))
        parent_id_label = QtGui.QLabel(self.tr('Parent'), self)
        self._parent_id_input = QtGui.QComboBox(self)
        requirement_ids = mdl.get_all_req_ids()
        requirement_ids.insert(0, None)
        requirement_ids.remove(self.item.req_id)
        self._parent_id_input.setModel(QtGui.QStringListModel(requirement_ids))
        self._parent_id_input.setCurrentIndex(
                    requirement_ids.index(self.item.parent_id))
        uc_label = QtGui.QLabel(self.tr('Use cases'), self)
        self._uc_input = QtGui.QTreeView(self)
        self._uc_input.setModel(mdl.get_use_case_list_model(self.item))
        self._uc_input.setAlternatingRowColors(True)
        self._uc_input.header().resizeSection(0, _1ST_COLUMN_WIDTH)
        self._uc_input.header().resizeSection(1, _2ND_COLUMN_WIDTH)
        self._uc_input.header().resizeSection(2, _3RD_COLUMN_WIDTH)
        test_label = QtGui.QLabel(self.tr('Tests'), self)
        self._test_input = QtGui.QTreeView(self)
        self._test_input.setModel(mdl.get_test_list_model(self.item))
        self._test_input.setAlternatingRowColors(True)
        self._test_input.header().resizeSection(0, _1ST_COLUMN_WIDTH)
        self._test_input.header().resizeSection(1, _2ND_COLUMN_WIDTH)
        self._test_input.header().resizeSection(2, _3RD_COLUMN_WIDTH)
        # puts it all together
        self.layout().addRow(name_label, self._name_input)
        self.layout().addRow(description_label, self._description_input)
        self.layout().addRow(priority_label, self._priority_input)
        self.layout().addRow(type_label, self._type_input)
        self.layout().addRow(source_label, self._source_input)
        self.layout().addRow(parent_id_label, self._parent_id_input)
        self.layout().addRow(uc_label, self._uc_input)
        self.layout().addRow(test_label, self._test_input)
        # signal connections
        self._description_input.textChanged.connect(self.content_changed)
        self._name_input.textChanged.connect(self.content_changed)
        self._parent_id_input.currentIndexChanged.connect(self.content_changed)
        self._priority_input.currentIndexChanged.connect(self.content_changed)
        self._source_input.currentIndexChanged.connect(self.content_changed)
        self._test_input.clicked.connect(self._handle_view_pressed)
        self._type_input.currentIndexChanged.connect(self.content_changed)
        self._uc_input.clicked.connect(self._handle_view_pressed)

    def save(self):
        """Dispatches a series of events to inform the controller about those
        (and only those) changes that have been operated by the user.
        """
        new_req_id = self._name_input.text()
        new_description = self._description_input.toPlainText()
        new_priority = mdl.PRIORITY_LIST[self._priority_input.currentIndex()]
        new_type = mdl.TYPE_LIST[self._type_input.currentIndex()]
        new_source = self._source_input.currentText()
        new_parent_id = self._parent_id_input.currentText() or None
        if self.item.req_id != new_req_id:
            self.fire_event.emit('update_requirement_id',
                    {'req_id': self.item.req_id, 'new_req_id': new_req_id})
            self.item.req_id = new_req_id
        if self.item.description != new_description:
            self.fire_event.emit('update_requirement_description',
                    {'req_id': new_req_id,
                    'description': new_description})
        if self.item.priority != new_priority:
            self.fire_event.emit('update_requirement_priority',
                    {'req_id': new_req_id, 'priority': new_priority})
        if self.item.req_type != new_type:
            self.fire_event.emit('update_requirement_type',
                    {'req_id': new_req_id, 'req_type': new_type})
        if self.item.source.name != new_source:
            self.fire_event.emit('update_requirement_source',
                    {'req_id': new_req_id, 'source_name': new_source})
        if self.item.parent_id != new_parent_id:
            self.fire_event.emit('update_requirement_parent_id',
                    {'req_id': new_req_id, 'parent_id': new_parent_id})
        # these are performed always (changes will be detected later)
        self.fire_event.emit('update_requirement_associations', {
                'req_id': new_req_id, 'newly_associated_tests':
                self._test_input.model().associated_item_ids,
                'newly_associated_use_cases':
                self._uc_input.model().associated_item_ids})


class UseCaseDisplay(ItemDisplay):
    """Widget which is used to display a use case in the central area.
    """
    def __init__(self, use_case, parent):
        super(UseCaseDisplay, self).__init__(use_case, parent)

    def _create_content(self):
        """Creates the form that is shown in the use case display.
        """
        # form fields
        name_label = QtGui.QLabel(self.tr('Name'), self)
        self._name_input = QtGui.QLineEdit(self)
        self._name_input.setText(self.item.uc_id)
        description_label = QtGui.QLabel(self.tr('Description'), self)
        self._description_input = QtGui.QPlainTextEdit(self)
        self._description_input.setPlainText(self.item.description)
        parent_id_label = QtGui.QLabel(self.tr('Parent'), self)
        self._parent_id_input = QtGui.QComboBox(self)
        uc_ids = mdl.get_all_uc_ids()
        uc_ids.insert(0, None)
        uc_ids.remove(self.item.uc_id)
        self._parent_id_input.setModel(QtGui.QStringListModel(uc_ids))
        self._parent_id_input.setCurrentIndex(
                uc_ids.index(self.item.parent_id))
        requirements_label = QtGui.QLabel(self.tr('Requirements'), self)
        self._requirements_input = QtGui.QTreeView(self)
        self._requirements_input.setModel(
                mdl.get_requirement_list_model(self.item))
        self._requirements_input.setAlternatingRowColors(True)
        self._requirements_input.header().resizeSection(0, _1ST_COLUMN_WIDTH)
        self._requirements_input.header().resizeSection(1, _2ND_COLUMN_WIDTH)
        self._requirements_input.header().resizeSection(2, _3RD_COLUMN_WIDTH)
        # puts it all together
        self.layout().addRow(name_label, self._name_input)
        self.layout().addRow(description_label, self._description_input)
        self.layout().addRow(parent_id_label, self._parent_id_input)
        self.layout().addRow(requirements_label, self._requirements_input)
        # signal connections
        self._description_input.textChanged.connect(self.content_changed)
        self._name_input.textChanged.connect(self.content_changed)
        self._parent_id_input.currentIndexChanged.connect(self.content_changed)
        self._requirements_input.clicked.connect(self._handle_view_pressed)

    def save(self):
        """Dispatches a series of events to inform the controller about those
        (and only those) changes that have been operated by the user.
        """
        new_uc_id = self._name_input.text()
        new_description = self._description_input.toPlainText()
        new_parent_id = self._parent_id_input.currentText() or None
        if self.item.uc_id != new_uc_id:
            self.fire_event.emit('update_use_case_id',
                    {'uc_id': self.item.uc_id, 'new_uc_id': new_uc_id})
            self.item.uc_id = new_uc_id
        if self.item.description != new_description:
            self.fire_event.emit('update_use_case_description',
                    {'uc_id': new_uc_id, 'description': new_description})
        if self.item.parent_id != new_parent_id:
            self.fire_event.emit('update_use_case_parent_id',
                    {'uc_id': new_uc_id, 'parent_id': new_parent_id})
        self.fire_event.emit('update_use_case_associations', {
                'uc_id': new_uc_id, 'newly_associated_requirements':
                self._requirements_input.model().associated_item_ids})


class TestDisplay(ItemDisplay):
    """Widget which is used to display a test in the central area.
    """
    def __init__(self, test, parent):
        super(TestDisplay, self).__init__(test, parent)

    def _create_content(self):
        """Creates the form that is shown in the test display.
        """
        # form fields
        test_id_label = QtGui.QLabel(self.tr('Name'), self)
        self._test_id_input = QtGui.QLineEdit(self)
        self._test_id_input.setText(self.item.test_id)
        description_label = QtGui.QLabel(self.tr('Description'), self)
        self._description_input = QtGui.QPlainTextEdit(self)
        self._description_input.setPlainText(self.item.description)
        requirements_label = QtGui.QLabel(self.tr('Requirements'), self)
        self._requirements_input = QtGui.QTreeView(self)
        self._requirements_input.setModel(
                mdl.get_requirement_list_model(self.item))
        self._requirements_input.setAlternatingRowColors(True)
        self._requirements_input.header().resizeSection(0, _1ST_COLUMN_WIDTH)
        self._requirements_input.header().resizeSection(1, _2ND_COLUMN_WIDTH)
        self._requirements_input.header().resizeSection(2, _3RD_COLUMN_WIDTH)
        # puts it all together
        self.layout().addRow(test_id_label, self._test_id_input)
        self.layout().addRow(description_label, self._description_input)
        self.layout().addRow(requirements_label, self._requirements_input)
        # signal connections
        self._description_input.textChanged.connect(self.content_changed)
        self._requirements_input.clicked.connect(self._handle_view_pressed)
        self._test_id_input.textChanged.connect(self.content_changed)

    def save(self):
        """Dispatches a series of events to inform the controller about those
        (and only those) changes that have been operated by the user.
        """
        new_test_id = self._test_id_input.text()
        new_description = self._description_input.toPlainText()
        if self.item.test_id != new_test_id:
            self.fire_event.emit('update_test_id',
                    {'test_id': self.item.test_id, 'new_test_id': new_test_id})
            self.item.test_id = new_test_id
        if self.item.description != new_description:
            self.fire_event.emit('update_test_description',
                    {'test_id': new_test_id, 'description': new_description})
        self.fire_event.emit('update_test_associations', {
                'test_id': new_test_id, 'newly_associated_requirements':
                self._requirements_input.model().associated_item_ids})


class SourceDisplay(ItemDisplay):
    def __init__(self, source, parent):
        super(SourceDisplay, self).__init__(source, parent)

    def _create_content(self):
        # form fields
        name_label = QtGui.QLabel(self.tr('Name'), self)
        self._name_input = QtGui.QLineEdit(self)
        self._name_input.setText(self.item.name)
        # puts it all together
        self.layout().addRow(name_label, self._name_input)
        # signal connections
        self._name_input.textChanged.connect(self.content_changed)

    def save(self):
        new_source_name = self._name_input.text()
        if self.item.name != new_source_name:
            self.fire_event.emit('update_source_name',
                    {'source_id': self.item.source_id,
                    'source_name': new_source_name})

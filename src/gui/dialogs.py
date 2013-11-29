# -*- coding: utf-8 -*-

"""This module contains the definitions of the dialogs that are used e.g. for
item creation in the graphical user interface.
"""

from PySide import QtCore, QtGui

from src import model as mdl
from src.gui.util import EnumTranslator

import os


class CreateItemDialog(QtGui.QDialog):
    """Abstract base class for all dialogs used to create new items (i.e.
    requirements, use cases and tests). All such dialogs must expose a 'data'
    attribute where the information is stored as a dictionary. Moreover, the
    hook method '_create_form' must be implemented by subclasses in order to
    have the content of the dialog window built correctly.
    """
    def __init__(self, parent):
        super(CreateItemDialog, self).__init__(parent)
        self.data = None
        self.setLayout(QtGui.QFormLayout(self))
        self._create_form()
        self._create_button_box()

    def _create_form(self):
        """Hook method used to create the input form for the new item.
        """
        raise NotImplementedError('Implement me!')

    def _create_button_box(self):
        """Creates a button box for the dialog with a Cancel button connected
        to the reject slot and an OK button connected to the accept slot.
        """
        button_box = QtGui.QDialogButtonBox(self)
        button_box.addButton(
                QtGui.QDialogButtonBox.Ok).clicked.connect(self.accept)
        button_box.addButton(
                QtGui.QDialogButtonBox.Cancel).clicked.connect(self.reject)
        self.layout().addWidget(button_box)


class CreateRequirementDialog(CreateItemDialog, EnumTranslator):
    """Dialog window used to create a new requirement.
    """
    def __init__(self, parent):
        super(CreateRequirementDialog, self).__init__(parent)
        self.setWindowTitle(self.tr('New requirement'))

    def _create_form(self):
        """Implements the base class method to create a suitable form.
        """
        et = EnumTranslator()
        # form fields
        req_id_label = QtGui.QLabel(self.tr('Name'), self)
        self._req_id_input = QtGui.QLineEdit(self)
        self._req_id_input.textChanged.connect(self._handle_id_input_changed)
        description_label = QtGui.QLabel(self.tr('Description'), self)
        self._description_input = QtGui.QPlainTextEdit(self)
        req_type_label = QtGui.QLabel(self.tr('Type'), self)
        self._req_type_input = QtGui.QComboBox(self)
        self._req_type_input.setModel(et.get_translated_type_list_model())
        priority_label = QtGui.QLabel(self.tr('Priority'), self)
        self._priority_input = QtGui.QComboBox(self)
        self._priority_input.setModel(et.get_translated_priority_list_model())
        source_label = QtGui.QLabel(self.tr('Source'), self)
        self._source_input = QtGui.QComboBox(self)
        self._source_input.setModel(QtGui.QStringListModel(
                mdl.get_all_source_names()))
        parent_id_label = QtGui.QLabel(self.tr('Parent'), self)
        self._parent_id_input = QtGui.QComboBox(self)
        req_id_list = mdl.get_all_requirement_ids()
        req_id_list.insert(0, None)
        self._parent_id_input.setModel(QtGui.QStringListModel(req_id_list))
        # puts it all together
        self.layout().addRow(req_id_label, self._req_id_input)
        self.layout().addRow(description_label, self._description_input)
        self.layout().addRow(req_type_label, self._req_type_input)
        self.layout().addRow(priority_label, self._priority_input)
        self.layout().addRow(source_label, self._source_input)
        self.layout().addRow(parent_id_label, self._parent_id_input)

    @QtCore.Slot()
    def _handle_id_input_changed(self, text):
        """Guesses what the name of the parent requirement may be by extracting
        the part before the dot (.) and, if it corresponds to some existing
        requirements, sets the combobox input index to point to that element.
        """
        chop_idx = text.rfind('.')
        guessed_parent_id = text[:chop_idx]
        id_list = self._parent_id_input.model().stringList()
        if guessed_parent_id and guessed_parent_id in id_list:
            index = id_list.index(guessed_parent_id)
            self._parent_id_input.setCurrentIndex(index)

    def accept(self):
        """Extracts the information provided by the user in the input form and
        populates the internal 'data' dictionary for the parent to use later.
        """
        self.data = {'req_id': self._req_id_input.text(),
                'description': self._description_input.toPlainText(),
                'req_type': mdl.TYPE_LIST[self._req_type_input.currentIndex()],
                'priority':
                 mdl.PRIORITY_LIST[self._priority_input.currentIndex()],
                'source_id':
                        mdl.get_source_id(self._source_input.currentText()),
                'parent_id': self._parent_id_input.currentText() or None}
        super(CreateRequirementDialog, self).accept()


class CreateUseCaseDialog(CreateItemDialog):
    """Dialog window used to create a new use case.
    """
    def __init__(self, parent):
        super(CreateUseCaseDialog, self).__init__(parent)
        self.setWindowTitle(self.tr('New use case'))

    def _create_form(self):
        """Implements the base class method to create a suitable form.
        """
        # form fields
        uc_id_label = QtGui.QLabel(self.tr('Name'), self)
        self._uc_id_input = QtGui.QLineEdit(self)
        self._uc_id_input.textChanged.connect(self._handle_id_input_changed)
        description_label = QtGui.QLabel(self.tr('Description'), self)
        self._description_input = QtGui.QPlainTextEdit(self)
        parent_id_label = QtGui.QLabel(self.tr('Parent'), self)
        self._parent_id_input = QtGui.QComboBox(self)
        uc_id_list = mdl.get_all_use_case_ids()
        uc_id_list.insert(0, None)
        self._parent_id_input.setModel(
                QtGui.QStringListModel(uc_id_list))
        # puts it all together
        self.layout().addRow(uc_id_label, self._uc_id_input)
        self.layout().addRow(description_label, self._description_input)
        self.layout().addRow(parent_id_label, self._parent_id_input)

    @QtCore.Slot()
    def _handle_id_input_changed(self, text):
        """Guesses what the name of the parent use case may be by extracting
        the part before the dot (') and, if it corresponds to some existing
        requirements, sets the combobox input index to point to that element.
        """
        chop_idx = text.rfind('.')
        guessed_parent_id = text[:chop_idx]
        id_list = self._parent_id_input.model().stringList()
        if guessed_parent_id and guessed_parent_id in id_list:
            index = id_list.index(guessed_parent_id)
            self._parent_id_input.setCurrentIndex(index)

    def accept(self):
        """Extracts the information provided by the user in the input form and
        populates the internal 'data' dictionary for the parent to use later.
        """
        self.data = {'uc_id': self._uc_id_input.text(),
                'image': None,
                'description': self._description_input.toPlainText(),
                'parent_id': self._parent_id_input.currentText() or None}
        super(CreateUseCaseDialog, self).accept()


class CreateTestDialog(CreateItemDialog):
    """Dialog window used to create a new test.
    """
    def __init__(self, parent):
        super(CreateTestDialog, self).__init__(parent)
        self.setWindowTitle(self.tr('New test'))

    def _create_form(self):
        """Implements the base class method to create a suitable form.
        """
        # form fields
        test_id_label = QtGui.QLabel(self.tr('Name'), self)
        self._test_id_input = QtGui.QLineEdit(self)
        description_label = QtGui.QLabel(self.tr('Description'), self)
        self._description_input = QtGui.QPlainTextEdit(self)
        # puts it all together
        self.layout().addRow(test_id_label, self._test_id_input)
        self.layout().addRow(description_label, self._description_input)

    def accept(self):
        """Extracts the information provided by the user in the input form and
        populates the internal 'data' dictionary for the parent to use later.
        """
        self.data = {'test_id': self._test_id_input.text(),
                'description': self._description_input.toPlainText()}
        super(CreateTestDialog, self).accept()


class CreateSourceDialog(CreateItemDialog):
    """This dialog is used to create a new requirement source.
    """
    def __init__(self, parent):
        super(CreateSourceDialog, self).__init__(parent)
        self.setWindowTitle(self.tr(u'New requirement source'))

    def _create_form(self):
        """Implements the base class method to create a suitable form.
        """
        name_label = QtGui.QLabel(self.tr('Name'), self)
        self._name_input = QtGui.QLineEdit(self)
        self.layout().addRow(name_label, self._name_input)

    def accept(self):
        """Extracts the information provided by the user in the input form and
        populates the internal 'data' dictionary for the parent to use later.
        """
        self.data = {'source_name': self._name_input.text()}
        super(CreateSourceDialog, self).accept()


class PrintRequirementDialog(QtGui.QDialog):
    def __init__(self, parent):
        super(PrintRequirementDialog, self).__init__(parent)
        self.setLayout(QtGui.QVBoxLayout(self))
        self.setMinimumWidth(350)
        self._create_form()
        # button box
        button_box = QtGui.QDialogButtonBox(self)
        button_box.addButton(
                QtGui.QDialogButtonBox.Ok).clicked.connect(self.accept)
        button_box.addButton(
                QtGui.QDialogButtonBox.Cancel).clicked.connect(self.reject)

        self.layout().addWidget(button_box, 3, 2)

    def _create_form(self):
        et = EnumTranslator()
        form = QtGui.QWidget(self)
        form.setLayout(QtGui.QGridLayout(form))
        type_label = QtGui.QLabel(self.tr('Type'), self)
        self._type_input = QtGui.QComboBox(self)
        self._type_input.setModel(et.get_translated_type_list_model())
        priority_label = QtGui.QLabel(self.tr('Priority'), self)
        self._priority_input = QtGui.QComboBox(self)
        self._priority_input.setModel(et.get_translated_priority_list_model())
        path_label = QtGui.QLabel(self.tr('Path'), self)
        self._path_input = QtGui.QLineEdit(self)
        self._path_input.setEnabled(False)
        choose_button = QtGui.QPushButton(self.tr('Browse'), self)
        choose_button.clicked.connect(self._handle_choose_button_clicked)
        # puts it all together
        form.layout().addWidget(type_label, 0, 0)
        form.layout().addWidget(self._type_input, 0, 1)
        form.layout().addWidget(priority_label, 1, 0)
        form.layout().addWidget(self._priority_input, 1, 1)
        form.layout().addWidget(path_label, 2, 0)
        form.layout().addWidget(self._path_input, 2, 1)
        form.layout().addWidget(choose_button, 2, 2)
        self.layout().addWidget(form)

    @QtCore.Slot()
    def _handle_choose_button_clicked(self):
        path = QtGui.QFileDialog.getSaveFileName(self,
                    self.tr('Choose location'), os.path.expanduser('~'))
        if path[0]:
            self._path_input.setText(path[0])
        else:
            self._path_input.setText('')

    def accept(self):
        if self._path_input.text():
            self.req_type = mdl.TYPE_LIST[self._type_input.currentIndex()]
            self.priority = mdl.PRIORITY_LIST[
                    self._priority_input.currentIndex()]
            self.path = self._path_input.text()
            super(PrintRequirementDialog, self).accept()
        else:
            self.reject()

# -*- coding: utf-8 -*-
from PySide import QtGui

from src import model as mdl


class CreateItemDialog(QtGui.QDialog):
    def __init__(self, parent):
        super(CreateItemDialog, self).__init__(parent)
        self.data = None
        self.setLayout(QtGui.QFormLayout(self))
        self._create_form()

    def _create_form(self):
        raise NotImplementedError('Implement me!')


class CreateRequirementDialog(CreateItemDialog):
    def __init__(self, parent):
        super(CreateRequirementDialog, self).__init__(parent)
        self.setWindowTitle(u'Nuovo requisito')

    def _create_form(self):
        # form fields
        req_id_label = QtGui.QLabel(u'Nome', self)
        self._req_id_input = QtGui.QLineEdit(self)
        description_label = QtGui.QLabel(u'Descrizione', self)
        self._description_input = QtGui.QPlainTextEdit(self)
        req_type_label = QtGui.QLabel(u'Tipologia', self)
        self._req_type_input = QtGui.QComboBox(self)
        self._req_type_input.setModel(QtGui.QStringListModel(mdl.TYPE_LIST))
        priority_label = QtGui.QLabel(u'Priorità', self)
        self._priority_input = QtGui.QComboBox(self)
        self._priority_input.setModel(QtGui.QStringListModel(
                mdl.PRIORITY_LIST))
        source_label = QtGui.QLabel(u'Fonte', self)
        self._source_input = QtGui.QComboBox(self)
        self._source_input.setModel(QtGui.QStringListModel(
                mdl.get_all_source_names()))
        parent_id_label = QtGui.QLabel(u'Genitore', self)
        self._parent_id_input = QtGui.QComboBox(self)
        req_id_list = mdl.get_all_req_ids()
        req_id_list.insert(0, None)
        self._parent_id_input.setModel(QtGui.QStringListModel(req_id_list))
        # puts it all together
        self.layout().addRow(req_id_label, self._req_id_input)
        self.layout().addRow(description_label, self._description_input)
        self.layout().addRow(req_type_label, self._req_type_input)
        self.layout().addRow(priority_label, self._priority_input)
        self.layout().addRow(source_label, self._source_input)
        self.layout().addRow(parent_id_label, self._parent_id_input)
        # button box
        button_box = QtGui.QDialogButtonBox(self)
        button_box.addButton(
                QtGui.QDialogButtonBox.Ok).clicked.connect(self.accept)
        button_box.addButton(
                QtGui.QDialogButtonBox.Cancel).clicked.connect(self.reject)
        self.layout().addWidget(button_box)

    def accept(self):
        self.data = {'req_id': self._req_id_input.text(),
                'description': self._description_input.toPlainText(),
                'req_type': self._req_type_input.currentText(),
                'priority': self._priority_input.currentText(),
                'source_id':
                        mdl.get_source_id(self._source_input.currentText()),
                'parent_id': self._parent_id_input.currentText() or None}
        super(CreateRequirementDialog, self).accept()


class CreateUseCaseDialog(CreateItemDialog):
    def __init__(self, parent):
        super(CreateUseCaseDialog, self).__init__(parent)
        self.setWindowTitle(u'Nuovo caso d\'uso')

    def _create_form(self):
        # form fields
        uc_id_label = QtGui.QLabel(u'Nome', self)
        self._uc_id_input = QtGui.QLineEdit(self)
        description_label = QtGui.QLabel(u'Descrizione', self)
        self._description_input = QtGui.QPlainTextEdit(self)
        parent_id_label = QtGui.QLabel(u'Genitore', self)
        self._parent_id_input = QtGui.QComboBox(self)
        uc_id_list = mdl.get_all_uc_ids()
        uc_id_list.insert(0, None)
        self._parent_id_input.setModel(
                QtGui.QStringListModel(uc_id_list))
        # puts it all together
        self.layout().addRow(uc_id_label, self._uc_id_input)
        self.layout().addRow(description_label, self._description_input)
        self.layout().addRow(parent_id_label, self._parent_id_input)
        # button box
        button_box = QtGui.QDialogButtonBox(self)
        button_box.addButton(
                QtGui.QDialogButtonBox.Ok).clicked.connect(self.accept)
        button_box.addButton(
                QtGui.QDialogButtonBox.Cancel).clicked.connect(self.reject)
        self.layout().addWidget(button_box)

    def accept(self):
        self.data = {'uc_id': self._uc_id_input.text(),
                'image': None,
                'description': self._description_input.toPlainText(),
                'parent_id': self._parent_id_input.currentText() or None}
        super(CreateUseCaseDialog, self).accept()


class CreateTestDialog(CreateItemDialog):
    def __init__(self, parent):
        super(CreateTestDialog, self).__init__(parent)
        self.setWindowTitle(u'Nuovo test')

    def _create_form(self):
        # form fields
        test_id_label = QtGui.QLabel(u'Nome', self)
        self._test_id_input = QtGui.QLineEdit(self)
        description_label = QtGui.QLabel(u'Descrizione', self)
        self._description_input = QtGui.QPlainTextEdit(self)
        # puts it all together
        self.layout().addRow(test_id_label, self._test_id_input)
        self.layout().addRow(description_label, self._description_input)
        # button box
        button_box = QtGui.QDialogButtonBox(self)
        button_box.addButton(
                QtGui.QDialogButtonBox.Ok).clicked.connect(self.accept)
        button_box.addButton(
                QtGui.QDialogButtonBox.Cancel).clicked.connect(self.reject)
        self.layout().addWidget(button_box)

    def accept(self):
        self.data = {'test_id': self._test_id_input.text(),
                'description': self._description_input.toPlainText()
        }
        super(CreateTestDialog, self).accept()

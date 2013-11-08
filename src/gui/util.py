# -*- coding: utf-8 -*-

"""This module contains some utilities that are used in the GUI subsystem.
"""

from PySide import QtCore, QtGui

from src import model as mdl


class EnumTranslator(QtCore.QObject):
    """The methods contained in this class are used to display a translation of
    the model constants in the user interface.
    """
    def __init__(self):
        super(EnumTranslator, self).__init__()

    def _translate_type_to_ui(self, index):
        """Maps the type of requirements into localize-able strings.
        """
        if mdl.TYPE_LIST[index] == 'F':
            return self.tr('functional')
        if mdl.TYPE_LIST[index] == 'P':
            return self.tr('performance')
        if mdl.TYPE_LIST[index] == 'Q':
            return self.tr('quality metric')
        return self.tr('declarative')

    def _translate_priority_to_ui(self, index):
        """Maps the priority of requirements into localize-able strings.
        """
        if mdl.PRIORITY_LIST[index] == 'O':
            return self.tr('mandatory')
        if mdl.PRIORITY_LIST[index] == 'F':
            return self.tr('optional')
        return self.tr('desirable')

    def get_translated_type_list_model(self):
        """Returns a model containing the internationalized requirement types.
        """
        return QtGui.QStringListModel([self._translate_type_to_ui(i)
                for i in range(len(mdl.TYPE_LIST))])

    def get_translated_priority_list_model(self):
        """Returns a model with the internationalized requirement priorities.
        """
        return QtGui.QStringListModel([self._translate_priority_to_ui(i)
                for i in range(len(mdl.PRIORITY_LIST))])

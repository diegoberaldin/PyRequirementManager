# -*- coding: utf-8 -*-

"""This executable module is the application single entry point.
"""

import sys

from PySide import QtCore, QtGui

from src import controller, gui, model


class Application(QtGui.QApplication):
    """This is used as an abstraction for the application.
    """
    def __init__(self, args):
        super(Application, self).__init__(args)

    def run(self):
        """Initializes the controller and shows the main view.
        """
        model.initialize_db()
        model.dal.initialize_sources()
        self._controller = controller.ApplicationController()
        self._gui = gui.get_main_window(self._controller)
        self._gui.show()

if __name__ == '__main__':
    application = Application(sys.argv)
    # translates the application UI
    translator = QtCore.QTranslator()
    translator.load(':/i18n/{0}'.format(QtCore.QLocale.system().name()))
    application.installTranslator(translator)
    application.run()
    sys.exit(application.exec_())

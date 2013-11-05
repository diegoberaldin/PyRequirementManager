# -*- coding: utf-8 -*-

import logging.config
import sys

from PySide import QtGui

from src import controller, gui, model

# location of the logging configuration file
_LOGCONF = 'log.conf'


class Application(QtGui.QApplication):
    """This is used as an abstraction for the application.
    """
    def __init__(self, args):
        super(Application, self).__init__(args)

    def run(self):
        """Initializes the controller and shows the main view.
        """
        logging.config.fileConfig(_LOGCONF)
        model.initialize_db()
        model.dal.initialize_sources()
        self._controller = controller.ApplicationController()
        self._gui = gui.get_main_window(self._controller)
        self._gui.show()

if __name__ == '__main__':
    application = Application(sys.argv)
    application.run()
    sys.exit(application.exec_())

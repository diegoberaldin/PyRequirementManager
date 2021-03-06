# -*- coding: utf-8 -*-

"""This module contains the main window of the application and the definition
of its central (main) widget.
"""

from PySide import QtCore, QtGui

from src import APPNAME, model as mdl
from src.gui import dialogs as dlg, displays as dsp

import os

# window default width
_WINDOW_WIDTH = 900
# window default height
_WINDOW_HEIGHT = 500
# maximum left column width
_LEFT_COLUMN_WIDTH = 200
# single instance of the application main window
_mw = None


def get_main_window(controller=None):
    """Returns a reference to the main window (lazy initialization).
    """
    global _mw
    if not _mw:
        _mw = MainWindow(controller)
    return _mw


class MainWindow(QtGui.QMainWindow):
    """Main window of the application.
    """
    def __init__(self, controller):
        super(MainWindow, self).__init__()
        self.setWindowTitle(APPNAME)
        self._create_actions()
        self._create_menus()
        # inserts the main widget in the window layout
        self._main_widget = MainWidget(self)
        self._main_widget.fire_event.connect(controller.handle_event)
        self.setCentralWidget(self._main_widget)
        self.setMinimumSize(_WINDOW_WIDTH, _WINDOW_HEIGHT)

    def _create_actions(self):
        self._print_uc_list_action = QtGui.QAction(
                self.tr('Use case list'), self)
        self._print_uc_list_action.triggered.connect(
                self._handle_print_use_case_list)
        self._print_req_list_action = QtGui.QAction(
                self.tr('Requirement list'), self)
        self._print_req_list_action.triggered.connect(
                self._handle_print_req_list)
        self._print_uc_req_track = QtGui.QAction(
                self.tr('Use case - requirements'), self)
        self._print_uc_req_track.triggered.connect(
                self._handle_print_uc_req_track)

    def _create_menus(self):
        print_menu = QtGui.QMenu(self.tr('Print'), self)
        print_menu.addAction(self._print_uc_list_action)
        print_menu.addAction(self._print_req_list_action)
        track_menu = QtGui.QMenu(self.tr('Tracking'), print_menu)
        track_menu.addAction(self._print_uc_req_track)
        print_menu.addMenu(track_menu)
        self.menuBar().addMenu(print_menu)

    def display_message(self, message):
        """Displays an error message in the main user interface.
        """
        QtGui.QMessageBox.critical(self, self.tr('Error'), message)

    @QtCore.Slot()
    def _handle_print_use_case_list(self):
        ret = QtGui.QFileDialog.getSaveFileName(self,
                    self.tr('Select location'), os.path.expanduser('~'))
        if ret[0]:
            self._main_widget.fire_event.emit('print_use_case_list',
                {'target_path': ret[0]})

    @QtCore.Slot()
    def _handle_print_req_list(self):
        dialog = dlg.PrintRequirementDialog(self)
        if dialog.exec_():
            self._main_widget.fire_event.emit('print_requirement_list',
                    {'target_path': dialog.path, 'req_type': dialog.req_type,
                     'priority': dialog.priority})

    @QtCore.Slot()
    def _handle_print_uc_req_track(self):
        ret = QtGui.QFileDialog.getSaveFileName(self,
                    self.tr('Select location'), os.path.expanduser('~'))
        if ret[0]:
            self._main_widget.fire_event.emit('print_uc_req_track',
                    {'target_path': ret[0]})


class MainWidget(QtGui.QWidget):
    """Central widget which displays a list of items on the left and a central
    part where an item at a time is displayed and can be edited by the user.
    """
    # this signal is emitted to inform the controller about new events
    fire_event = QtCore.Signal(str, dict)

    def __init__(self, parent):
        super(MainWidget, self).__init__(parent)
        self.setLayout(QtGui.QVBoxLayout(self))
        self._create_actions()
        self._create_toolbar()
        self._create_central_part()

    def _create_actions(self):
        """Initializes the actions that will be used to create toolbars and
        menus. The actions correspond to creating a new item, saving it after
        it gets changed or deleting some existing item.
        """
        self._new_action = QtGui.QAction(
                self.style().standardIcon(QtGui.QStyle.SP_FileDialogNewFolder),
                self.tr('Create new item (Ctrl+N)'), self)
        self._new_action.setShortcut(QtGui.QKeySequence.New)
        self._new_action.triggered.connect(self._handle_new)
        self._save_action = QtGui.QAction(
                self.style().standardIcon(QtGui.QStyle.SP_DialogSaveButton),
                self.tr('Save item (Ctrl+S)'), self)
        self._save_action.setShortcut(QtGui.QKeySequence.Save)
        self._save_action.triggered.connect(self._handle_save)
        self._save_action.setEnabled(False)
        self._delete_action = QtGui.QAction(
                self.style().standardIcon(QtGui.QStyle.SP_TrashIcon),
                self.tr('Delete item (Del)'), self)
        self._delete_action.setShortcut(QtGui.QKeySequence.Delete)
        self._delete_action.triggered.connect(self._handle_delete)

    def _get_view_selector_model(self):
        """Returns a string list model for the content of the view selector.
        """
        return QtGui.QStringListModel([self.tr('Requirements'),
                self.tr('Use cases'), self.tr('Tests'), self.tr('Sources')])

    def _create_toolbar(self):
        """Creates the top toolbar of the central widget.
        """
        bar_widget = QtGui.QWidget(self)
        bar_widget.setLayout(QtGui.QHBoxLayout(bar_widget))
        tool_bar = QtGui.QToolBar(bar_widget)
        # combo box for selecting items to display
        self._view_selector = QtGui.QComboBox(tool_bar)
        self._view_selector.setModel(self._get_view_selector_model())
        self._view_selector.setCurrentIndex(0)
        self._view_selector.currentIndexChanged.connect(
                self._handle_selector_index_changed)
        # puts it all together
        tool_bar.addAction(self._new_action)
        tool_bar.addAction(self._save_action)
        tool_bar.addAction(self._delete_action)
        bar_widget.layout().addWidget(tool_bar)
        bar_widget.layout().addStretch()
        bar_widget.layout().addWidget(QtGui.QLabel(self.tr('Show'), tool_bar))
        bar_widget.layout().addWidget(self._view_selector)
        self.layout().addWidget(bar_widget)

    def _create_central_part(self):
        """Creates the central part, which is split into two columns.
        """
        self._splitter = QtGui.QSplitter(self)
        self._view = QtGui.QTreeView(self)
        self._view.setMaximumWidth(_LEFT_COLUMN_WIDTH)
        self._view.setAlternatingRowColors(True)
        # method override on-the-fly to keep backward compatibility
        self._view.selectionChanged = (
                lambda unused_selected, unused_deselected:
                self._handle_view_clicked())
        self._view.setModel(mdl.get_requirement_model())
        self._splitter.addWidget(self._view)
        self._display = dsp.ItemDisplay(parent=self)
        self._splitter.addWidget(self._display)
        self._splitter.setSizePolicy(QtGui.QSizePolicy.MinimumExpanding,
                QtGui.QSizePolicy.Expanding)
        self.layout().addWidget(self._splitter)

    @QtCore.Slot(int)
    def _handle_selector_index_changed(self, index):
        """Allows the left hand column to change its content depending on the
        selection made on the top toolbar.
        """
        if index == 0:
            self._view.setModel(mdl.get_requirement_model())
        elif index == 1:
            self._view.setModel(mdl.get_use_case_model())
        elif index == 2:
            self._view.setModel(mdl.get_test_model())
        elif index == 3:
            self._view.setModel(mdl.get_source_model())
        self._switch_display(dsp.ItemDisplay(parent=self))

    @QtCore.Slot()
    def _handle_new(self):
        """Allows the user to create a new item, the type of which will vary
        depending on the content of the view selector.
        """
        index = self._view_selector.currentIndex()
        if index == 0:  # new requirement
            dialog = dlg.CreateRequirementDialog(self)
            ret = dialog.exec_()
            if ret:
                self.fire_event.emit('create_requirement',
                        {'data': dialog.data})
        elif index == 1:  # new use case
            dialog = dlg.CreateUseCaseDialog(self)
            ret = dialog.exec_()
            if ret:
                self.fire_event.emit('create_use_case', {'data': dialog.data})
        elif index == 2:  # new test
            dialog = dlg.CreateTestDialog(self)
            ret = dialog.exec_()
            if ret:
                self.fire_event.emit('create_test', {'data': dialog.data})
        elif index == 3:  # new source
            dialog = dlg.CreateSourceDialog(self)
            ret = dialog.exec_()
            if ret:
                self.fire_event.emit('create_source', {'data': dialog.data})

    @QtCore.Slot()
    def _handle_display_content_changed(self):
        """When a sub-widget informs the central widget of some change having
        happened to its content, the save action is activated so that when the
        display changes its content will be persisted on disk.
        """
        self._save_action.setEnabled(True)

    @QtCore.Slot()
    def _handle_save(self):
        """Saves the content of the current display (deferring to the latter
        the responsibility of dispatching the correct events) and disables the
        save action since there is no need for it being active any longer.
        """
        if self._save_action.isEnabled():
            self._display.save()
        self._save_action.setEnabled(False)

    @QtCore.Slot()
    def _handle_delete(self):
        """Deletes the item which is currently being displayed in the central
        part (if any item at all is displayed).
        """
        current_item = self._display.item
        if not current_item:
            return
        if hasattr(current_item, 'req_id'):
            self.fire_event.emit('delete_requirement',
                    {'req_id': current_item.req_id})
        elif hasattr(current_item, 'uc_id'):
            self.fire_event.emit('delete_use_case',
                    {'uc_id': current_item.uc_id})
        elif hasattr(current_item, 'test_id'):
            self.fire_event.emit('delete_test',
                    {'test_id': current_item.test_id})
        elif hasattr(current_item, 'source_id'):
            self.fire_event.emit('delete_source',
                    {'source_id': current_item.source_id})
        self._switch_display(dsp.ItemDisplay(parent=self))

    @QtCore.Slot()
    def _handle_view_clicked(self):
        """Allows the central part to change its content depending on the
        selection that has been made on the left hand column.
        """
        selection = self._get_view_selection()
        if len(selection) == 1:
            item_id = selection.pop()
            index = self._view_selector.currentIndex()
            if index == 0:  # requirement
                if mdl.get_all_source_names():
                    requirement = mdl.get_requirement(item_id)
                    self._switch_display(dsp.RequirementDisplay(
                            requirement, self))
                else:
                    QtGui.QMessageBox.critical(self, self.tr('No source'),
                            self.tr('You have to create at least one source'
                            'in order to create a new requirement'))
            elif index == 1:  # use case
                use_case = mdl.get_use_case(item_id)
                self._switch_display(dsp.UseCaseDisplay(use_case, self))
            elif index == 2:  # test
                test = mdl.get_test(item_id)
                self._switch_display(dsp.TestDisplay(test, self))
            elif index == 3:
                source = mdl.get_source(item_id)
                self._switch_display(dsp.SourceDisplay(source, self))
            else:
                self._switch_display(dsp.ItemDisplay(parent=self))

    def _get_view_selection(self):
        """Extracts the selected item from the left hand column.
        """
        return [self._view.model().data(index)
                for index in self._view.selectedIndexes()
                if index.column() == 0]

    def _switch_display(self, new_display):
        """Handles the switch from one display to another.
        """
        if self._save_action.isEnabled():
            self._display.save()  # needed to make data persistent
        self._save_action.setEnabled(False)
        self._display.deleteLater()
        self._display = new_display
        self._splitter.addWidget(self._display)
        # signal connections
        new_display.fire_event.connect(self.fire_event)
        new_display.content_changed.connect(
                self._handle_display_content_changed)

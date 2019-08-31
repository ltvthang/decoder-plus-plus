# vim: ts=8:sts=8:sw=8:noexpandtab
#
# This file is part of Decoder++
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
import json

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QAction, QFileDialog

from core import Context
from core.plugin.plugin import PluginType
from ui import CodecTab
from ui.codec_frame import CodecFrame
from ui.dialog.hidden_dialog import HiddenDialog
from ui.main_window_tabs_widget import MainWindowTabsWidget


class MainWindowWidget(QWidget):

    def __init__(self, parent, context: 'core.context.Context', input: str = None):
        super(QWidget, self).__init__(parent)
        self._parent = parent
        self._context = context
        self._plugins = context.plugins()
        self._main_window = parent

        self.layout = QVBoxLayout(self)
        self._tabs = MainWindowTabsWidget(self._context, self._plugins)
        self._tabs.tabAdded.connect(self._tab_added_event)
        self._tabs.tabClosed.connect(self._tab_closed_event)
        self.layout.addWidget(self._tabs)
        self.setLayout(self.layout)

        self._init_shortcuts()
        self._tabs.newTab(input)
        self._tabs.setCurrentIndex(0)

    def _init_shortcuts(self):
        main_menu = self._parent.menuBar()
        self._file_menu = self._init_file_menu(main_menu)
        self._edit_menu = self._init_edit_menu(main_menu)
        self._view_menu = self._init_view_menu(main_menu)
        self._select_menu = self._init_select_menu(main_menu)
        self._tab_menu = self._init_tab_menu(main_menu)
        self._help_menu = self._init_help_menu(main_menu)

    def _init_help_menu(self, main_menu):
        help_menu = main_menu.addMenu('&Help')
        keyboard_shortcuts_action = QAction("&Keyboard Shortcuts", self)
        keyboard_shortcuts_action.triggered.connect(
            lambda: self._show_hidden_dialog(HiddenDialog.TAB_KEYBOARD_SHORTCUTS))
        help_menu.addAction(keyboard_shortcuts_action)
        about_action = QAction("&About", self)
        about_action.triggered.connect(self._show_hidden_dialog)
        help_menu.addAction(about_action)
        return help_menu

    def _init_edit_menu(self, main_menu):
        edit_menu = main_menu.addMenu('&Edit')

        self._register_shortcut(Context.Shortcut.EDIT_CUT,
                                "C&ut",
                                "Ctrl+X",
                                lambda: self._call_focused_frame(lambda focused_frame: focused_frame.cutSelectedInputText()),
                                edit_menu)
        self._register_shortcut(Context.Shortcut.EDIT_COPY,
                                "&Copy",
                                "Ctrl+C",
                                lambda: self._call_focused_frame(lambda focused_frame: focused_frame.copySelectedInputText()),
                                edit_menu)
        self._register_shortcut(Context.Shortcut.EDIT_PASTE,
                                "&Paste",
                                "Ctrl+P",
                                lambda: self._call_focused_frame(lambda focused_frame: focused_frame.pasteSelectedInputText()),
                                edit_menu)
        edit_menu.addSeparator()
        self._register_shortcut(Context.Shortcut.TOGGLE_SEARCH_FIELD,
                                "Toggle Search Field",
                                "Ctrl+F",
                                lambda: self._call_focused_frame(lambda focused_frame: focused_frame.toggleSearchField()),
                                edit_menu)
        return edit_menu

    def _init_view_menu(self, main_menu):
        view_menu = main_menu.addMenu('&View')
        self._register_shortcut(Context.Shortcut.SELECT_LOG_DOCK,
                                "Log View",
                                "Alt+Shift+L",
                                lambda: self._main_window._toggle_log_dock(),
                                view_menu)
        self._register_shortcut(Context.Shortcut.SELECT_HEX_DOCK,
                                "Hex View",
                                "Alt+Shift+X",
                                lambda: self._main_window._toggle_hex_dock(),
                                view_menu)
        return view_menu

    def _init_select_menu(self, main_menu):
        select_menu = main_menu.addMenu('&Select')
        #self._register_shortcut(Context.Shortcut.FOCUS_CODEC_SEARCH,
        #                        "Select Codec Search",
        #                        "Ctrl+Space",
        #                        lambda: self._tabs.focusCodecSearch(),
        #                        select_menu)
        self._register_shortcut(Context.Shortcut.FOCUS_DECODER,
                                "Select Decoder",
                                "Alt+Shift+D",
                                lambda: self._call_focused_frame(lambda focused_frame: focused_frame.focusComboBox(PluginType.DECODER)),
                                select_menu)
        self._register_shortcut(Context.Shortcut.FOCUS_ENCODER,
                                "Select Encoder",
                                "Alt+Shift+E",
                                lambda: self._call_focused_frame(lambda focused_frame: focused_frame.focusComboBox(PluginType.ENCODER)),
                                select_menu)
        self._register_shortcut(Context.Shortcut.FOCUS_HASHER,
                                "Select Hasher",
                                "Alt+Shift+H",
                                lambda: self._call_focused_frame(lambda focused_frame: focused_frame.focusComboBox(PluginType.HASHER)),
                                select_menu)
        self._register_shortcut(Context.Shortcut.FOCUS_SCRIPT,
                                "Select Script",
                                "Alt+Shift+S",
                                lambda: self._call_focused_frame(lambda focused_frame: focused_frame.focusComboBox(PluginType.SCRIPT)),
                                select_menu)

        select_menu.addSeparator()

        self._register_shortcut(Context.Shortcut.FOCUS_INPUT_TEXT,
                                "Select Text Field",
                                "Alt+Shift+I",
                                lambda: self._call_focused_frame(lambda focused_frame: focused_frame.focusInputText()),
                                select_menu)
        self._register_shortcut(Context.Shortcut.FOCUS_INPUT_TEXT_NEXT,
                                "Select Next Text Field",
                                "Alt+Down",
                                lambda: self._focus_input_text(lambda frame: frame.next()),
                                select_menu)
        self._register_shortcut(Context.Shortcut.FOCUS_INPUT_TEXT_PREVIOUS,
                                "Select Previous Text Field",
                                "Alt+Up",
                                lambda: self._focus_input_text(lambda frame: frame.previous()),
                                select_menu)
        return select_menu

    def _init_tab_menu(self, main_menu):
        tab_menu = main_menu.addMenu('&Tabs')
        self._register_shortcut(Context.Shortcut.TAB_RENAME,
                                "Rename Tab",
                                "Alt+Shift+R",
                                lambda: self._tabs.tabBar().renameTab(),
                                tab_menu)
        self._register_shortcut(Context.Shortcut.TAB_NEXT,
                                "Next Tab",
                                "Ctrl+Tab",
                                lambda: self._tabs.nextTab(),
                                tab_menu)
        self._register_shortcut(Context.Shortcut.TAB_PREVIOUS,
                                "Previous Tab",
                                "Ctrl+Shift+Tab",
                                lambda: self._tabs.previousTab(),
                                tab_menu)

        tab_menu.addSeparator()
        self._tabs_select_action = []

        def select_tab(index):
            return lambda: self._tabs.selectTab(index)

        for tab_num in range(1, 10):
            action = self._register_shortcut(Context.Shortcut.TAB_SELECT_.format(tab_num),
                                    "Select Tab {}".format(tab_num),
                                    "Alt+{}".format(tab_num),
                                    select_tab(tab_num - 1),
                                    tab_menu)
            action.setVisible(False)
            self._tabs_select_action.append(action)
        return tab_menu

    def _init_file_menu(self, main_menu):
        file_menu = main_menu.addMenu('&File')
        self._register_shortcut(Context.Shortcut.TAB_NEW,
                                "New Tab", "Ctrl+T",
                                lambda: self._tabs.newTab(),
                                file_menu)
        self._register_shortcut(Context.Shortcut.TAB_CLOSE,
                                "Close Tab",
                                "Ctrl+W",
                                lambda: self._tabs.closeTab(),
                                file_menu)
        file_menu.addSeparator()
        self._register_shortcut(Context.Shortcut.OPEN_FILE,
                                "Open File", "Ctrl+O",
                                lambda: self._open_file(),
                                file_menu)
        self._register_shortcut(Context.Shortcut.SAVE_AS_FILE,
                                "Save as File", "Ctrl+S",
                                lambda: self._save_as_file(),
                                file_menu)
        file_menu.addSeparator()
        self._register_shortcut(Context.Shortcut.FILE_EXIT,
                                "E&xit",
                                "Ctrl+Q",
                                lambda: self._parent.close(),
                                file_menu)
        return file_menu

    def _register_shortcut(self, id, text, shortcut_key, callback, menu) -> QAction:
        action = self._context.registerShortcut(id, text, shortcut_key, callback, self)
        menu.addAction(action)
        return action

    def _call_focused_frame(self, callback):
        focused_frame = self._get_focused_frame()
        if focused_frame:
            callback(focused_frame)

    def _get_focused_frame(self) -> CodecFrame:
        return self._tabs.currentWidget().getFocusedFrame()

    def _focus_input_text(self, callback):
        frame = self._get_focused_frame()
        if frame:
            frame = callback(frame) or frame
            frame.focusInputText()
            self._tabs.currentWidget().ensureWidgetVisible(frame)

    def _show_hidden_dialog(self, tab_select: str=None):
        """ Shows the hidden dialog. """
        hidden_dialog = HiddenDialog(self, self._context, tab_select)
        hidden_dialog.exec_()

    def _open_file(self):
        filename, _ = QFileDialog.getOpenFileName(self, 'Open File')
        if filename:
            try:
                with open(filename) as f:
                    save_file = json.loads(f.read())
                    for tab_config in save_file:
                        index, tab = self.newTab()
                        self._tabs.renameTab(index, tab_config["name"])
                        previous_frame = None
                        for frame_config in tab_config["frames"]:
                            if previous_frame is None:
                                # New tabs contain one empty frame
                                frame = tab.getFrames()[0]
                                frame.setInputText(frame_config["text"])
                            else:
                                frame = tab.newFrame(frame_config["text"], frame_config["title"], previous_frame)
                            frame.fromDict(frame_config)
                            previous_frame = frame
                self._context.logger().info("Successfully loaded {}!".format(filename))
            except Exception as e:
                self._context.logger().error("Unexpected error loading file. {}".format(e))

    def _save_as_file(self):
        filename, _ = QFileDialog.getSaveFileName(self, 'Save As File')
        if filename:
            try:
                self._context.saveAsFile(filename, str(json.dumps(self._tabs.toDict())))
                self._context.logger().info("Successfully saved session in {}!".format(filename))
            except Exception as e:
                self._context.logger().error("Unexpected error saving file. {}".format(e))

    def _tab_added_event(self, index, name):
        if 0 <= index < len(self._tabs_select_action):
            self._tabs_select_action[index].setVisible(True)

    def _tab_closed_event(self, index, name):
        for index in range(0, len(self._tabs_select_action)):
            self._tabs_select_action[index].setVisible(index < self._tabs.tabCount())

    def newTab(self, input: str = None) -> (int, CodecTab):
        """
        Opens a new tab and writes input into first codec-frame.
        :param input: The input which should be placed into the first codec-frame.
        """
        return self._tabs.newTab(input)

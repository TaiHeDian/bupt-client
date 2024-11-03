"""
Title: Ui.py
Author: 吴烨辰
LastEditors: 高迎新
"""
from PyQt5 import QtCore, QtGui, QtWidgets


def _set_fixed_size_policy(widget):
    """Set fixed size policy for widget"""
    policy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
    policy.setHorizontalStretch(0)
    policy.setVerticalStretch(0)
    widget.setSizePolicy(policy)


def _set_expanding_size_policy(widget):
    """Set expanding size policy for widget"""
    policy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
    policy.setHorizontalStretch(0)
    policy.setVerticalStretch(0)
    widget.setSizePolicy(policy)


class UiDialog(object):
    def setup_ui(self, dialog):
        self._setup_main_window(dialog)
        self._setup_top_section()
        self._setup_plot_section()
        self._setup_bottom_section()
        self._finalize_layout(dialog)

    def _setup_main_window(self, dialog):
        """Initialize main window settings"""
        dialog.setObjectName('dialog')
        dialog.resize(1115, 910)
        self.main_layout = QtWidgets.QVBoxLayout(dialog)
        self.main_layout.setObjectName('main_layout')
        self.main_container = QtWidgets.QWidget(dialog)
        self.main_container.setObjectName('main_container')
        self.container_layout = QtWidgets.QVBoxLayout(self.main_container)
        self.container_layout.setObjectName('container_layout')

    def _setup_top_section(self):
        """Setup top section with input fields and connection buttons"""
        self.top_section = QtWidgets.QWidget(self.main_container)
        self._configure_top_section_size()
        self.top_grid = QtWidgets.QGridLayout(self.top_section)

        # Add status text field
        self.status_field = self._create_text_field(12)
        self.top_grid.addWidget(self.status_field, 0, 2, 1, 1)

        # Add input text field
        self.input_field = self._create_input_field()
        self.top_grid.addWidget(self.input_field, 2, 2, 1, 1)

        # Add buttons
        self.connect_button = self._create_button("连接设备", (0, 60), (0, 3, 2, 2))
        self.start_button = self._create_button("开始", (200, 60), (2, 3, 1, 1))
        self.stop_button = self._create_button("停止", (200, 60), (2, 4, 1, 1))

        # Add spacers
        self.top_grid.addItem(
            QtWidgets.QSpacerItem(
                20, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum
            ), 0, 5, 1, 1
        )
        self.top_grid.addItem(
            QtWidgets.QSpacerItem(
                20, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum
            ), 0, 0, 1, 1
        )
        self.container_layout.addWidget(self.top_section)

    def _setup_plot_section(self):
        """Setup middle plot section"""
        self.plot_widget = QtWidgets.QWidget(self.main_container)
        _set_expanding_size_policy(self.plot_widget)
        self.plot_widget.setObjectName('plot_widget')
        self.container_layout.addWidget(self.plot_widget)

    def _setup_bottom_section(self):
        """Setup bottom section with data button"""
        self.bottom_section = QtWidgets.QWidget(self.main_container)
        self._configure_bottom_section_size()

        self.bottom_layout = QtWidgets.QHBoxLayout(self.bottom_section)
        self.data_button = self._create_button("所有数据", (200, 75))

        self.bottom_layout.addItem(
            QtWidgets.QSpacerItem(
                40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum
            )
        )
        self.bottom_layout.addWidget(self.data_button)
        self.bottom_layout.addItem(
            QtWidgets.QSpacerItem(
                40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum
            )
        )

        self.container_layout.addWidget(self.bottom_section)

    def _create_text_field(self, font_size):
        """Create a text edit field with specified font size"""
        text_field = QtWidgets.QTextEdit(self.top_section)
        font = QtGui.QFont()
        font.setPointSize(font_size)
        text_field.setFont(font)
        return text_field

    def _create_input_field(self):
        """Create main input text field"""
        input_field = QtWidgets.QTextEdit(self.top_section)
        _set_expanding_size_policy(input_field)
        input_field.setMinimumSize(QtCore.QSize(300, 0))
        input_field.setMaximumSize(QtCore.QSize(2000, 75))
        input_field.setFont(QtGui.QFont('', 12))
        return input_field

    def _create_button(self, text, size=(0, 0), grid_pos=None):
        """Create a button with specified parameters"""
        button = QtWidgets.QPushButton(self.top_section)
        button.setMinimumSize(QtCore.QSize(size[0], size[1]))
        if size[0]:
            button.setMaximumSize(QtCore.QSize(size[0], size[1]))
            _set_fixed_size_policy(button)
        button.setText(text)
        if grid_pos:
            self.top_grid.addWidget(button, *grid_pos)
        return button

    def _configure_top_section_size(self):
        """Configure size for top section"""
        _set_expanding_size_policy(self.top_section)
        self.top_section.setMaximumSize(QtCore.QSize(16777215, 150))
        self.top_section.setObjectName('top_section')

    def _configure_bottom_section_size(self):
        """Configure size for bottom section"""
        _set_expanding_size_policy(self.bottom_section)
        self.bottom_section.setMaximumSize(QtCore.QSize(16777215, 100))
        self.bottom_section.setObjectName('bottom_section')

    def _finalize_layout(self, dialog):
        """Finalize layout and set translations"""
        self.main_layout.addWidget(self.main_container)
        self.set_text(dialog)
        QtCore.QMetaObject.connectSlotsByName(dialog)

    def set_text(self, dialog):
        """Set text translations"""
        _translate = QtCore.QCoreApplication.translate
        dialog.setWindowTitle(_translate('dialog', '便携压力测试设备'))
        self.start_button.setText(_translate('dialog', '开始'))
        self.stop_button.setText(_translate('dialog', '停止'))
        self.connect_button.setText(_translate('dialog', '连接设备'))
        self.data_button.setText(_translate('dialog', '所有数据'))

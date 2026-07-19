from PyQt6.QtCore import QSize, Qt
from PyQt6.QtGui import QCursor, QFont
from PyQt6.QtWidgets import (
    QAbstractItemView,
    QFrame,
    QGridLayout,
    QHeaderView,
    QLabel,
    QPushButton,
    QStyle,
    QTableWidget,
    QTextEdit,
    QToolButton,
    QVBoxLayout,
    QWidget,
)


LEFT_PANEL_WIDTH = 200


class MainWindowUI:
    def setup_ui(self, window):
        window.setFixedSize(640, 580)

        self.central_widget = QWidget(window)
        self.central_widget.setObjectName("centralWidget")
        window.setCentralWidget(self.central_widget)

        main_layout = QGridLayout(self.central_widget)
        main_layout.setContentsMargins(20, 16, 20, 16)
        main_layout.setHorizontalSpacing(20)
        main_layout.setVerticalSpacing(12)
        main_layout.setColumnStretch(0, 0)
        main_layout.setColumnStretch(1, 1)
        main_layout.setRowStretch(1, 1)

        self.header_widget = QWidget()
        self.header_widget.setObjectName("headerWidget")
        header_layout = QGridLayout(self.header_widget)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setHorizontalSpacing(8)
        header_layout.setColumnMinimumWidth(0, 32)
        header_layout.setColumnMinimumWidth(2, 32)
        header_layout.setColumnStretch(1, 1)

        self.title_label = QLabel("接龙文本生成器 - 随机排序版")
        self.title_label.setObjectName("titleLabel")
        title_font = QFont("思源黑体 CN Bold")
        self.title_label.setFont(title_font)
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(self.title_label, 0, 1)

        self.help_button = QToolButton()
        self.help_button.setObjectName("helpButton")
        self.help_button.setIcon(window.style().standardIcon(QStyle.StandardPixmap.SP_MessageBoxQuestion))
        self.help_button.setIconSize(QSize(22, 22))
        self.help_button.setFixedSize(24, 24)
        self.help_button.setToolTip("使用说明")
        self.help_button.setAccessibleName("使用说明")
        self.help_button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        header_layout.addWidget(self.help_button, 0, 2, Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

        main_layout.addWidget(self.header_widget, 0, 0, 1, 2)

        self.control_frame = QFrame()
        self.control_frame.setObjectName("controlFrame")
        self.control_frame.setFixedWidth(LEFT_PANEL_WIDTH)
        control_layout = QVBoxLayout(self.control_frame)
        control_layout.setContentsMargins(0, 4, 0, 0)
        control_layout.setSpacing(8)
        main_layout.addWidget(self.control_frame, 1, 0)

        # ========== Buttons ==========

        button_font = QFont("思源黑体 CN Normal")

        self.import_button = QPushButton("导入名单")
        self.import_button.setObjectName("importButton")
        self.import_button.setFont(button_font)
        self.import_button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.import_button.setFixedHeight(42)
        control_layout.addWidget(self.import_button)

        self.shuffle_button = QPushButton("刷新排序")
        self.shuffle_button.setObjectName("shuffleButton")
        self.shuffle_button.setFont(button_font)
        self.shuffle_button.setFixedHeight(42)
        self.shuffle_button.setEnabled(False)
        control_layout.addWidget(self.shuffle_button)

        self.export_button = QPushButton("导出为 TXT")
        self.export_button.setObjectName("exportButton")
        self.export_button.setFont(button_font)
        self.export_button.setFixedHeight(42)
        self.export_button.setEnabled(False)
        control_layout.addWidget(self.export_button)

        # ========== Data Information ==========

        info_font = QFont("思源黑体 CN Normal")

        self.file_label = QLabel("当前文件：未选择")
        self.file_label.setObjectName("fileLabel")
        self.file_label.setFont(info_font)
        self.file_label.setWordWrap(True)
        self.file_label.setFixedWidth(LEFT_PANEL_WIDTH)
        control_layout.addSpacing(12)
        control_layout.addWidget(self.file_label)

        self.summary_label = QLabel("名单条数：0")
        self.summary_label.setObjectName("summaryLabel")
        self.summary_label.setFont(info_font)
        self.summary_label.setWordWrap(True)
        self.summary_label.setFixedWidth(LEFT_PANEL_WIDTH)
        control_layout.addSpacing(8)
        control_layout.addWidget(self.summary_label)

        self.summary_table = QTableWidget(0, 2)
        self.summary_table.setObjectName("summaryTable")
        self.summary_table.setFont(info_font)
        self.summary_table.setHorizontalHeaderLabels(["第二列内容", "次数"])
        self.summary_table.verticalHeader().setVisible(False)
        self.summary_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.summary_table.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
        self.summary_table.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.summary_table.setFixedWidth(LEFT_PANEL_WIDTH)
        self.summary_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.summary_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)
        self.summary_table.setColumnWidth(1, 52)
        control_layout.addSpacing(10)
        control_layout.addWidget(self.summary_table, 1)

        # ========== Preview Window ==========

        self.preview_container = QWidget()
        self.preview_container.setObjectName("previewContainer")
        preview_layout = QVBoxLayout(self.preview_container)
        preview_layout.setContentsMargins(0, 4, 0, 0)
        preview_layout.setSpacing(6)
        main_layout.addWidget(self.preview_container, 1, 1)

        self.preview_text = QTextEdit()
        self.preview_text.setObjectName("previewText")
        self.preview_text.setFont(QFont("思源黑体 CN Normal"))
        self.preview_text.setReadOnly(True)
        self.preview_text.setLineWrapMode(QTextEdit.LineWrapMode.WidgetWidth)
        preview_layout.addWidget(self.preview_text, 1)

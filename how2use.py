from pathlib import Path

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QCursor
from PyQt6.QtWidgets import QDialog, QFrame, QHBoxLayout, QLabel, QPushButton, QTextEdit, QVBoxLayout


FILE_ENCODING = "utf-8"
RESOURCE_DIR = Path(__file__).parent / "resource"
INSTRUCTION_PATH = RESOURCE_DIR / "chain_text_gen_instruction.txt"


def load_instruction_contents():
    try:
        return INSTRUCTION_PATH.read_text(encoding=FILE_ENCODING)
    except FileNotFoundError:
        return f"未找到使用说明文件：{INSTRUCTION_PATH.name}"
    except OSError as exc:
        return f"读取使用说明失败：{exc}"


class UsageInstructionsDialog(QDialog):
    def __init__(self, parent=None, text_font=None):
        super().__init__(parent)

        self.setObjectName("usageDialog")
        self.setWindowTitle("使用说明")
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint, True)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setFixedSize(480, 380)
        self.setModal(False)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(0)

        self.card_frame = QFrame()
        self.card_frame.setObjectName("usageDialogCard")
        layout.addWidget(self.card_frame)

        card_layout = QVBoxLayout(self.card_frame)
        card_layout.setContentsMargins(16, 16, 16, 16)
        card_layout.setSpacing(12)

        title_label = QLabel("使用说明")
        title_label.setObjectName("usageTitleLabel")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_layout.addWidget(title_label)

        instruction_text = QTextEdit()
        instruction_text.setObjectName("usageInstructionText")
        if text_font:
            instruction_text.setFont(text_font)
        instruction_text.setReadOnly(True)
        instruction_text.setLineWrapMode(QTextEdit.LineWrapMode.WidgetWidth)
        instruction_text.setPlainText(load_instruction_contents())
        card_layout.addWidget(instruction_text, 1)

        button_layout = QHBoxLayout()
        button_layout.addStretch(1)

        self.confirm_button = QPushButton("我已了解")
        self.confirm_button.setObjectName("usageConfirmButton")
        self.confirm_button.setFixedSize(72, 32)
        self.confirm_button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.confirm_button.clicked.connect(self.accept)
        button_layout.addWidget(self.confirm_button)

        card_layout.addLayout(button_layout)


def show_usage_instructions(parent, current_dialog=None, text_font=None):
    if current_dialog and current_dialog.isVisible():
        current_dialog.raise_()
        current_dialog.activateWindow()
        return current_dialog

    dialog = UsageInstructionsDialog(parent, text_font=text_font)
    dialog.show()
    return dialog

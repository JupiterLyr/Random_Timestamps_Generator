import csv
import os
import random
from collections import Counter
from datetime import datetime
from pathlib import Path

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QCursor, QIcon
from PyQt6.QtWidgets import (
    QDialog,
    QFileDialog,
    QMessageBox,
    QTableWidgetItem,
    QTextEdit,
    QVBoxLayout,
    QMainWindow,
)

from ui import MainWindowUI


VERSION = "3.0.0"
FILE_ENCODING = "utf-8"
RESOURCE_DIR = Path(__file__).parent / "resource"
INSTRUCTION_PATH = RESOURCE_DIR / "chain_text_gen_instruction"
ICON_PATH = RESOURCE_DIR / "icon.png"
QSS_PATH = RESOURCE_DIR / "chain_text_gen.qss"


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.ui = MainWindowUI()
        self.ui.setup_ui(self)
        self._apply_stylesheet()

        if ICON_PATH.exists():
            self.setWindowIcon(QIcon(str(ICON_PATH)))
        else:
            QMessageBox.warning(self, "Icon not found", "图标文件缺失，无法成功加载！")

        self.window().setWindowTitle("接龙文本生成器 v" + VERSION)

        self.description_text = ""
        self.records = []
        self.shuffled_list = []
        self.instruction_contents = self._load_instruction_contents()
        self.usage_dialog = None

        self._connect_signals()
        self._update_summary_display()

    def _apply_stylesheet(self):
        try:
            self.setStyleSheet(QSS_PATH.read_text(encoding=FILE_ENCODING))
        except FileNotFoundError:
            return
        except OSError as exc:
            QMessageBox.warning(self, "样式表加载失败", f"无法加载样式表：{exc}")

    def _connect_signals(self):
        self.ui.import_button.clicked.connect(self._import_csv)
        self.ui.shuffle_button.clicked.connect(self._shuffle_records)
        self.ui.export_button.clicked.connect(self._export_txt)
        self.ui.help_button.clicked.connect(self._show_usage_instructions)

    def _import_csv(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "选择名单CSV文件，第一列为姓名，第二列为附加文字",
            "",
            "CSV files (*.csv);;All files (*.*)",
        )
        if not file_path:
            return

        raw_records = []
        try:
            with open(file_path, "r", encoding=FILE_ENCODING, newline="") as file:
                reader = csv.reader(file)
                raw_records = [row for row in reader if row]
        except UnicodeDecodeError:
            try:
                with open(file_path, "r", encoding="gbk", newline="") as file:
                    reader = csv.reader(file)
                    raw_records = [row for row in reader if row]
            except Exception as exc:
                QMessageBox.critical(self, "错误", f"读取CSV文件失败（编码错误）: {exc}")
                return
        except Exception as exc:
            QMessageBox.critical(self, "错误", f"读取CSV文件失败: {exc}")
            return

        if not raw_records:
            QMessageBox.warning(self, "警告", "CSV文件未检测到有效内容！")
            return

        first_row = raw_records[0]
        self.description_text = first_row[0].strip() if first_row else ""

        self.records = []
        for row in raw_records[1:]:
            if len(row) >= 2:
                name = row[0].strip()
                notes = row[1].strip()
            elif len(row) == 1:
                name = row[0].strip()
                notes = ""
            else:
                continue

            if name:
                self.records.append((name, notes))

        if not self.records:
            QMessageBox.warning(self, "警告", "未能解析到有效的名单数据（除第一行描述外无其他名单）")
            self._set_buttons_state(False)
            return

        self.ui.file_label.setText(f"当前文件：{Path(file_path).name}")
        self.ui.summary_label.setText(f"名单条数：{len(self.records)}")
        self._update_summary_display()
        self._set_buttons_state(True)
        self._shuffle_records()

    def _build_summary_items(self):
        notes_counter = Counter(notes for _, notes in self.records if notes)
        if notes_counter:
            return sorted(notes_counter.items(), key=lambda item: (-item[1], item[0]))
        return [("无非空内容", "")]

    def _update_summary_display(self):
        self.ui.summary_table.setRowCount(0)
        for note, count in self._build_summary_items():
            row = self.ui.summary_table.rowCount()
            self.ui.summary_table.insertRow(row)
            self.ui.summary_table.setItem(row, 0, QTableWidgetItem(str(note)))
            self.ui.summary_table.setItem(row, 1, QTableWidgetItem(str(count)))

    def _load_instruction_contents(self):
        try:
            return INSTRUCTION_PATH.read_text(encoding=FILE_ENCODING)
        except FileNotFoundError:
            return f"未找到使用说明文件：{INSTRUCTION_PATH.name}"
        except OSError as exc:
            return f"读取使用说明失败：{exc}"

    def _show_usage_instructions(self):
        if self.usage_dialog and self.usage_dialog.isVisible():
            self.usage_dialog.raise_()
            self.usage_dialog.activateWindow()
            return

        self.usage_dialog = QDialog(self)
        self.usage_dialog.setWindowTitle("使用说明")
        self.usage_dialog.setFixedSize(480, 360)
        self.usage_dialog.setModal(False)

        layout = QVBoxLayout(self.usage_dialog)
        layout.setContentsMargins(16, 16, 16, 16)

        instruction_text = QTextEdit()
        instruction_text.setFont(self.ui.summary_label.font())
        instruction_text.setReadOnly(True)
        instruction_text.setLineWrapMode(QTextEdit.LineWrapMode.WidgetWidth)
        instruction_text.setPlainText(self.instruction_contents)
        layout.addWidget(instruction_text)

        self.usage_dialog.show()

    def _shuffle_records(self):
        if not self.records:
            return

        random.seed(int(datetime.now().timestamp() * 1000) & 0xFFFFFFFF)
        self.shuffled_list = list(self.records)
        random.shuffle(self.shuffled_list)
        self._update_preview_display()

    def _update_preview_display(self):
        lines = []

        if self.description_text:
            lines.extend([self.description_text, ""])

        display_limit = min(20, len(self.shuffled_list))
        for index in range(display_limit):
            name, notes = self.shuffled_list[index]
            line_content = f"{name}-{notes}" if notes else name
            lines.append(f"{index + 1}.{line_content}")

        if len(self.shuffled_list) > 20:
            lines.extend(
                [
                    "",
                    f"... 仅预览展示前20行，其余 {len(self.shuffled_list) - 20} 行将在导出时完整写入 ...",
                ]
            )

        self.ui.preview_text.setPlainText("\n".join(lines))

    def _export_txt(self):
        if not self.shuffled_list:
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "选择保存排序结果的位置",
            "",
            "Text files (*.txt);;All files (*.*)",
        )
        if not file_path:
            return

        if Path(file_path).suffix == "":
            file_path = f"{file_path}.txt"

        try:
            with open(file_path, "w", encoding=FILE_ENCODING, newline="") as file:
                if self.description_text:
                    file.write(f"{self.description_text}\n\n")

                for index, (name, notes) in enumerate(self.shuffled_list, 1):
                    line_content = f"{name}-{notes}" if notes else name
                    file.write(f"{index}.{line_content}\n")
        except Exception as exc:
            QMessageBox.critical(self, "错误", f"文件保存失败: {exc}")
            return

        answer = QMessageBox.question(
            self,
            "完成",
            f"已成功导出 {len(self.shuffled_list)} 条记录。\n是否打开该文件？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if answer == QMessageBox.StandardButton.Yes:
            try:
                os.startfile(file_path)
            except OSError as exc:
                QMessageBox.warning(self, "警告", f"打开文件失败: {exc}")

    def _set_buttons_state(self, enabled):
        cursor = QCursor(Qt.CursorShape.PointingHandCursor if enabled else Qt.CursorShape.ArrowCursor)
        for button in (self.ui.shuffle_button, self.ui.export_button):
            button.setEnabled(enabled)
            button.setCursor(cursor)

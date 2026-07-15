import csv
import os
import random
import tkinter as tk
from collections import Counter
from datetime import datetime
from pathlib import Path
from tkinter import filedialog, font as tkfont, messagebox, ttk

VERSION = "2.4"
FILE_ENCODING = "utf-8"
INFO_TEXT_WIDTH = 160


class NameRandomizer:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title(f"接龙文本生成器 v{VERSION}")
        try:
            self.root.iconbitmap(Path(__file__).parent / 'resource/icon.ico')
        except Exception:
            messagebox.showwarning("Icon not found", "图标文件缺失，无法成功加载！")  # 若无图标文件则忽略
        self.root.geometry("640x580")
        self.root.resizable(False, False)

        # 核心数据存储
        self.description_text = ""  # 存储第一行第一个单元格的描述性文字
        self.records = []  # 原始解析数据 [(name, notes), ...]
        self.shuffled_list = []  # 打乱后的数据 [(name, notes), ...]
        self.instruction_contents = self._load_instruction_contents()

        # 界面变量
        self.file_var = tk.StringVar(value="当前文件：未选择")
        self.summary_var = tk.StringVar(value="名单条数：0")
        self.usage_window = None

        self._build_ui()
        self._update_summary_display()

    def _build_ui(self):
        """UI构建"""
        self.root.grid_columnconfigure(0, weight=0)
        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_rowconfigure(1, weight=1)

        tk.Label(
            self.root,
            text="接龙文本生成器 - 随机排序版",
            font=("黑体", 14),
            justify="center"
        ).grid(row=0, column=0, columnspan=2, pady=(16, 12))

        control_frame = tk.Frame(self.root, padx=20, pady=4)
        control_frame.grid(row=1, column=0, sticky="nsw")
        control_frame.grid_columnconfigure(0, weight=1)
        control_frame.grid_rowconfigure(5, weight=1)

        preview_container = tk.Frame(self.root, padx=0, pady=4)
        preview_container.grid(row=1, column=1, sticky="nsew", padx=(0, 20), pady=(0, 16))
        preview_container.grid_rowconfigure(1, weight=1)
        preview_container.grid_columnconfigure(0, weight=1)

        tk.Button(control_frame, text="导入名单", command=self._import_csv,
            font=("宋体", 12), cursor="hand2", width=16, height=2
        ).grid(row=0, column=0, sticky="ew", pady=4)

        self.btn_shuffle = tk.Button(control_frame, text="刷新排序", command=self._shuffle_records,
            font=("宋体", 12), width=16, height=2, state="disabled")
        self.btn_shuffle.grid(row=1, column=0, sticky="ew", pady=4)

        self.btn_export = tk.Button(control_frame, text="导出为 TXT", command=self._export_txt,
            font=("宋体", 12), width=16, height=2, state="disabled")
        self.btn_export.grid(row=2, column=0, sticky="ew", pady=4)

        tk.Message(control_frame, textvariable=self.file_var, font=("宋体", 11),
            justify="left", anchor="nw", width=INFO_TEXT_WIDTH
        ).grid(row=3, column=0, sticky="w", pady=(16, 0))

        tk.Message(control_frame, textvariable=self.summary_var, font=("宋体", 11),
            justify="left", anchor="nw", width=INFO_TEXT_WIDTH
        ).grid(row=4, column=0, sticky="w", pady=(12, 0))

        summary_frame = tk.Frame(control_frame)
        summary_frame.grid(row=5, column=0, sticky="nsew", pady=(6, 0))
        summary_frame.grid_rowconfigure(0, weight=1)
        summary_frame.grid_columnconfigure(0, weight=1)

        table_style = ttk.Style()
        table_style.configure("Summary.Treeview", font=("宋体", 11), rowheight=24)
        table_style.configure("Summary.Treeview.Heading", font=("宋体", 11))

        self.summary_table = ttk.Treeview(
            summary_frame,
            columns=("note", "count"),
            show="headings",
            height=1,
            style="Summary.Treeview"
        )
        self.summary_table.heading("note", text="第二列内容")
        self.summary_table.heading("count", text="次数")
        self.summary_table.column("note", width=110, anchor="w")
        self.summary_table.column("count", width=50, anchor="center", stretch=False)

        summary_scrollbar = tk.Scrollbar(summary_frame, command=self.summary_table.yview)
        self.summary_table.config(yscrollcommand=summary_scrollbar.set)

        self.summary_table.grid(row=0, column=0, sticky="nsew")
        summary_scrollbar.grid(row=0, column=1, sticky="ns")

        help_font = tkfont.Font(family="宋体", size=10, underline=True)
        help_frame = tk.Frame(control_frame)
        help_frame.grid(row=6, column=0, sticky="ew", pady=(10, 0))
        help_frame.grid_columnconfigure(0, weight=1)

        help_label = tk.Label(help_frame, text="使用说明", font=help_font,
            fg="#1A5FB4", cursor="hand2")
        help_label.grid(row=0, column=0)
        help_label.bind("<Button-1>", self._show_usage_instructions)

        tk.Label(preview_container, text="当前顺序预览（仅展示前 20 行）",
            font=("宋体", 12), anchor="w").grid(row=0, column=0, sticky="w", pady=(0, 6))

        preview_frame = tk.Frame(preview_container)
        preview_frame.grid(row=1, column=0, sticky="nsew")
        preview_frame.grid_rowconfigure(0, weight=1)
        preview_frame.grid_columnconfigure(0, weight=1)

        self.preview_text = tk.Text(preview_frame, font=("宋体", 10), state="disabled", bg="#F5F5F5", wrap="word")
        scrollbar = tk.Scrollbar(preview_frame, command=self.preview_text.yview)
        self.preview_text.config(yscrollcommand=scrollbar.set)

        self.preview_text.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")

    def _import_csv(self):
        """导入并解析CSV文件"""
        file_path = filedialog.askopenfilename(
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            title="选择名单CSV文件，第一列为姓名，第二列为附加文字"
        )
        if not file_path:
            return

        raw_records = []
        # 兼容 UTF-8(含BOM) 与 GBK 编码
        try:
            with open(file_path, "r", encoding=FILE_ENCODING, newline="") as f:
                reader = csv.reader(f)
                for row in reader:
                    if row:
                        raw_records.append(row)
        except UnicodeDecodeError:
            try:
                raw_records = []
                with open(file_path, "r", encoding="gbk") as f:
                    reader = csv.reader(f)
                    for row in reader:
                        if row:
                            raw_records.append(row)
            except Exception as e:
                messagebox.showerror("错误", f"读取CSV文件失败（编码错误）: {e}")
                return
        except Exception as e:
            messagebox.showerror("错误", f"读取CSV文件失败: {e}")
            return

        if not raw_records:
            messagebox.showwarning("警告", "CSV文件未检测到有效内容！")
            return

        # 提取第一行第一个单元格内容作为描述性文字
        first_row = raw_records[0]
        self.description_text = first_row[0].strip() if len(first_row) > 0 else ""

        # 过滤并提取名单字段（从第二行 raw_records[1:] 开始作为排序名单）
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
            if name:  # 必须保证姓名不为空
                self.records.append((name, notes))

        if not self.records:
            messagebox.showwarning("警告", "未能解析到有效的名单数据（除第一行描述外无其他名单）")
            self._set_buttons_state("disabled")
            return

        self.file_var.set(f"当前文件：{Path(file_path).name}")
        self.summary_var.set(f"名单条数：{len(self.records)}")
        self._update_summary_display()
        self._set_buttons_state("normal")
        self._shuffle_records()

    def _build_summary_items(self):
        """构建第二列统计结果，仅统计第二列非空内容的出现次数"""
        notes_counter = Counter(notes for _, notes in self.records if notes)
        if notes_counter:
            return sorted(notes_counter.items(), key=lambda item: (-item[1], item[0]))
        return [("无非空内容", "")]

    def _update_summary_display(self):
        """刷新第二列统计结果展示区"""
        for item_id in self.summary_table.get_children():
            self.summary_table.delete(item_id)

        for note, count in self._build_summary_items():
            self.summary_table.insert("", tk.END, values=(note, count))

    def _load_instruction_contents(self):
        """读取使用说明文本"""
        instruction_path = Path(__file__).parent / "resource/chain_text_gen_instruction"
        try:
            return instruction_path.read_text(encoding=FILE_ENCODING)
        except FileNotFoundError:
            return f"未找到使用说明文件：{instruction_path.name}"
        except OSError as e:
            return f"读取使用说明失败：{e}"

    def _show_usage_instructions(self, _event=None):
        """打开使用说明窗口"""
        if self.usage_window and self.usage_window.winfo_exists():
            self.usage_window.focus_force()
            return

        self.usage_window = tk.Toplevel(self.root)
        self.usage_window.title("使用说明")
        self.usage_window.geometry("480x360")
        self.usage_window.resizable(False, False)
        self.usage_window.transient(self.root)

        container = tk.Frame(self.usage_window, padx=16, pady=16)
        container.pack(fill=tk.BOTH, expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        instruction_text = tk.Text(
            container,
            font=("宋体", 11),
            wrap="word",
            state="normal",
            bg="#F5F5F5"
        )
        instruction_scrollbar = tk.Scrollbar(container, command=instruction_text.yview)
        instruction_text.config(yscrollcommand=instruction_scrollbar.set)
        instruction_text.insert("1.0", self.instruction_contents)
        instruction_text.config(state="disabled")

        instruction_text.grid(row=0, column=0, sticky="nsew")
        instruction_scrollbar.grid(row=0, column=1, sticky="ns")

    def _shuffle_records(self):
        """对名单执行随机洗牌并更新界面预览"""
        if not self.records:
            return

        # 使用当前毫秒级时间作为随机数种子确保真正的随机
        random.seed(int(datetime.now().timestamp() * 1000) & 0xffffffff)

        # 复制数据并洗牌
        self.shuffled_list = list(self.records)
        random.shuffle(self.shuffled_list)

        # 更新预览窗口
        self._update_preview_display()

    def _update_preview_display(self):
        """刷新文本预览窗口内容"""
        self.preview_text.config(state="normal")
        self.preview_text.delete("1.0", tk.END)

        # 1. 首先在顶端插入描述性文字（不参与排序，不加序号）
        if self.description_text:
            self.preview_text.insert(tk.END, f"{self.description_text}\n\n")

        # 2. 展示前20行名单数据
        display_limit = min(20, len(self.shuffled_list))
        for idx in range(display_limit):
            name, notes = self.shuffled_list[idx]
            line_content = f"{name}-{notes}" if notes else name
            self.preview_text.insert(tk.END, f"{idx + 1}.{line_content}\n")

        # 提示更多未显示的内容
        if len(self.shuffled_list) > 20:
            self.preview_text.insert(
                tk.END, f"\n... 仅预览展示前20行，其余 {len(self.shuffled_list) - 20} 行将在导出时完整写入 ..."
            )

        self.preview_text.config(state="disabled")

    def _export_txt(self):
        """将乱序后的名单加上序号导出为TXT"""
        if not self.shuffled_list:
            return

        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
            title="选择保存排序结果的位置"
        )
        if not file_path:
            return

        try:
            with open(file_path, "w", encoding="utf-8", newline="") as f:
                # 写入置顶的描述性文字
                if self.description_text:
                    f.write(f"{self.description_text}\n\n")

                # 写入带序号的乱序名单
                for idx, (name, notes) in enumerate(self.shuffled_list, 1):
                    line_content = f"{name}-{notes}" if notes else name
                    f.write(f"{idx}.{line_content}\n")
        except Exception as e:
            messagebox.showerror("错误", f"文件保存失败: {e}")
            return

        if messagebox.askyesno("完成", f"已成功导出 {len(self.shuffled_list)} 条记录。\n是否打开该文件？"):
            os.startfile(file_path)

    def _set_buttons_state(self, state):
        """统一管理按钮的状态激活以及手型光标的展现"""
        cursor_style = "hand2" if state == "normal" else "arrow"
        self.btn_shuffle.config(state=state, cursor=cursor_style)
        self.btn_export.config(state=state, cursor=cursor_style)

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    app = NameRandomizer()
    app.run()

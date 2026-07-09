import csv
import os
import random
import tkinter as tk
from datetime import datetime
from pathlib import Path
from tkinter import filedialog, messagebox

VERSION = "2.1"


class NameRandomizer:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title(f"接龙文本生成器 v{VERSION}")
        try:
            self.root.iconbitmap(Path(__file__).parent / 'icon.ico')
        except Exception:
            pass  # 若无图标文件则忽略
        self.root.geometry("400x480")
        self.root.resizable(False, False)

        # 核心数据存储
        self.description_text = ""  # 存储第一行第一个单元格的描述性文字
        self.records = []  # 原始解析数据 [(name, notes), ...]
        self.shuffled_list = []  # 打乱后的数据 [(name, notes), ...]

        # 界面变量
        self.status_var = tk.StringVar(value="请先导入名单 CSV 文件")

        self._build_ui()

    def _build_ui(self):
        """UI构建"""
        # 标题
        tk.Label(self.root, text="接龙文本生成器 - 随机排序版", font=("黑体", 14), justify="center"
                 ).pack(pady=15)

        # 按钮控制区
        btn_frame = tk.Frame(self.root)
        btn_frame.pack(fill=tk.X, padx=20, pady=5)

        tk.Button(btn_frame, text="导入名单", command=self._import_csv, font=("宋体", 12), cursor="hand2", width=12,
                  height=2
                  ).grid(row=0, column=0, padx=5, pady=5)

        self.btn_shuffle = tk.Button(btn_frame, text="刷新排序", command=self._shuffle_records,
                                     font=("宋体", 12), width=12, height=2, state="disabled")
        self.btn_shuffle.grid(row=0, column=1, padx=5, pady=5)

        self.btn_export = tk.Button(btn_frame, text="导出为 TXT", command=self._export_txt,
                                    font=("宋体", 12), width=12, height=2, state="disabled")
        self.btn_export.grid(row=0, column=2, padx=5, pady=5)

        # 状态指示
        tk.Label(self.root, textvariable=self.status_var, font=("宋体", 10), fg="gray"
                 ).pack(pady=5)

        # 预览区分割线与标签
        tk.Label(self.root, text="当前顺序预览 (仅展示前 20 行):", font=("宋体", 12)
                 ).pack(anchor="w", padx=20, pady=(10, 2))

        # 带滚动条的预览窗口
        preview_frame = tk.Frame(self.root)
        preview_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 15))

        self.preview_text = tk.Text(preview_frame, font=("宋体", 10), state="disabled", bg="#F5F5F5", wrap="word")
        scrollbar = tk.Scrollbar(preview_frame, command=self.preview_text.yview)
        self.preview_text.config(yscrollcommand=scrollbar.set)

        self.preview_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

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
            with open(file_path, "r", encoding="utf-8-sig") as f:
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
            self.status_var.set("导入失败")
            self._set_buttons_state("disabled")
            return

        self.status_var.set(f"已导入 {len(self.records)} 条数据")
        self._set_buttons_state("normal")
        self._shuffle_records()

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
            with open(file_path, "w", encoding="utf-8") as f:
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

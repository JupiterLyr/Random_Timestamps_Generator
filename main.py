import os
import random
import tkinter as tk
import webbrowser
from datetime import date, datetime, timedelta
from pathlib import Path
from time import time
from tkinter import filedialog, messagebox
from typing import Optional, Tuple

VERSION = "1.2"


class RandomTimeGenerator:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title(f"随机时间戳生成器 v{VERSION}")
        self.root.iconbitmap(Path(__file__).parent / 'icon.ico')
        self.root.geometry("384x380")
        self.root.resizable(False, False)

        # 变量及其默认值
        first_day, last_day = self.current_month_range()
        self.start_date = tk.StringVar(value=first_day.strftime("%Y-%m-%d"))
        self.start_time = tk.StringVar(value="08:00:00")
        self.end_date = tk.StringVar(value=last_day.strftime("%Y-%m-%d"))
        self.end_time = tk.StringVar(value="18:30:00")
        self.count = tk.StringVar(value="10")

        self._build_ui()

    def _build_ui(self):
        """UI构建"""
        tk.Label(self.root, text="随机时间戳生成器", font=("黑体", 14), justify="center"
                 ).grid(row=0, column=0, columnspan=2, pady=15)

        labels = [
            ("起始日期 (YYYY-MM-DD)", self.start_date),
            ("起始时间 (hh:mm:ss)",   self.start_time),
            ("终止日期 (YYYY-MM-DD)", self.end_date),
            ("终止时间 (hh:mm:ss)",   self.end_time),
            ("生成个数",              self.count)
        ]
        for idx, (text, var) in enumerate(labels):
            tk.Label(self.root, text=text, font=("宋体", 11)).grid(row=idx+1, column=0, padx=10, pady=5, sticky="w")
            tk.Entry(self.root, textvariable=var, width=20, font=("宋体", 11)).grid(row=idx+1, column=1, padx=10, pady=5)

        tk.Button(self.root, text="生成时间戳", command=self.__generate,
                  bg="#4CAF50", fg="white", font=("黑体", 13, "bold"), cursor="hand2"
                  ).grid(row=6, column=0, columnspan=2, pady=20, padx=10, sticky="ew")

        tk.Label(self.root,
                 text="使用说明:\n1. 输入日期时间范围\n2. 输入要生成的个数\n3. 点击生成并选择保存位置",
                 justify="left", fg="gray"
                 ).grid(row=7, column=0, columnspan=2, padx=10, pady=10, sticky="w")

        contact_label = tk.Label(self.root, text="✉", justify="right", fg="blue", font=("宋体", 20), cursor="hand2")
        contact_label.grid(row=7, column=0, columnspan=2, padx=10, pady=0, sticky="se")
        contact_label.bind("<Button-1>", lambda e: self.contact_me())

    def __generate(self):
        """按要求生成时间戳并保存"""
        try:
            start_dt = datetime.strptime(f"{self.start_date.get()} {self.start_time.get()}", "%Y-%m-%d %H:%M:%S")
            end_dt = datetime.strptime(f"{self.end_date.get()} {self.end_time.get()}", "%Y-%m-%d %H:%M:%S")
        except ValueError:
            messagebox.showerror("错误", "日期时间格式错误！请检查\n1. 是否满足YYYY-MM-DD和hh:mm:ss格式；\n2. 月份和日期是否合理。")
            return
        if start_dt >= end_dt:
            messagebox.showerror("错误", "起始日期时间必须早于终止日期时间！")
            return
        try:
            count = int(self.count.get())
            if count <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("错误", "生成个数必须为大于 0 的整数！")
            return

        # 生成随机时间
        random.seed(int(time() * 1e3) & 0xffffffff)  # 毫秒级，截取8位十六进制以兼容旧版随机数库
        delta = int((end_dt - start_dt).total_seconds())
        timestamps = [(start_dt + timedelta(seconds=random.randint(0, delta)))
                      .strftime("%Y-%m-%d %H:%M:%S") for _ in range(count)]

        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("CSV files (UTF-8)", "*.csv"), ("All files", "*.*")],
            title="请选择生成文件的保存位置")
        if not file_path:
            return
        with open(file_path, "w", encoding="utf-8") as f:
            f.writelines(f"{ts}\n" for ts in timestamps)

        if messagebox.askyesno("完成", f"已生成 {count} 个时间戳并保存至:\n{file_path}\n是否打开生成的文件？"):
            os.startfile(file_path)

    @staticmethod
    def current_month_range(today: Optional[date] = None) -> Tuple[date, date]:
        """按元组返回 today 所在月的第一天和最后一天日期"""
        if today is None:
            today = date.today()
        first = today.replace(day=1)
        # 取下月 1 号再减 1 天
        if first.month == 12:  # 12 月特殊处理
            next_month = first.replace(year=first.year + 1, month=1)
        else:
            next_month = first.replace(month=first.month + 1)
        last = next_month - timedelta(days=1)
        return first, last

    @staticmethod
    def contact_me():
        if_send = tk.messagebox.askquestion(title="联系作者",
                                            message="即将给 jupiterlyr@foxmail.com 发送邮件，是否继续？")
        if if_send == 'yes':
            webbrowser.open("mailto:'jupiterlyr@foxmail.com'")

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    app = RandomTimeGenerator()
    app.run()

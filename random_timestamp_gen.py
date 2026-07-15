import os
import random
import tkinter as tk
import webbrowser
from datetime import date, datetime, timedelta
from pathlib import Path
from time import time
from tkinter import filedialog, messagebox
from typing import Optional, Tuple

VERSION = "1.3"


class RandomTimeGenerator:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title(f"随机时间戳生成器 v{VERSION}")
        self.root.iconbitmap(Path(__file__).parent / 'resource/icon.ico')
        self.root.geometry("380x475")
        self.root.resizable(False, False)

        # 变量及其默认值
        first_day, last_day = self.current_month_range()
        self.start_date = tk.StringVar(value=first_day.strftime("%Y-%m-%d"))
        self.start_time = tk.StringVar(value="08:00:00")
        self.end_date = tk.StringVar(value=last_day.strftime("%Y-%m-%d"))
        self.end_time = tk.StringVar(value="18:30:00")
        self.count = tk.StringVar(value="10")
        self.checkbox_skip_time_period = tk.BooleanVar(value=False)
        self.forbidden_start_hour = tk.StringVar(value="00")
        self.forbidden_end_hour = tk.StringVar(value="00")

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
            ("生成个数 (不超过99999)", self.count)
        ]
        for idx, (text, var) in enumerate(labels[:-1]):
            tk.Label(self.root, text=text, font=("宋体", 11)).grid(row=idx+1, column=0, padx=10, pady=5, sticky="w")
            tk.Entry(self.root, textvariable=var, width=20, font=("宋体", 11)).grid(row=idx+1, column=1, padx=10, pady=5)
        tk.Label(self.root, text=labels[-1][0], font=("宋体", 11)).grid(row=5, column=0, padx=10, pady=5, sticky="w")
        self.entry_count = tk.Entry(self.root, textvariable=self.count, width=20, font=("宋体", 11))
        self.entry_count.grid(row=5, column=1, padx=10, pady=5)

        self.skip_checkbox = tk.Checkbutton(self.root, text="跳过特定时间段", font=("宋体", 11),
                                            variable=self.checkbox_skip_time_period, command=self._toggle_forbidden_hours)
        self.skip_checkbox.grid(row=6, column=0, columnspan=2, padx=10, pady=5, sticky="w")

        hour_options = [f"{i:02d}" for i in range(24)]
        self.forbidden_frame = tk.Frame(self.root)
        self.forbidden_frame.grid(row=7, column=0, columnspan=2, padx=10, pady=5, sticky="w")

        tk.Label(self.forbidden_frame, text="禁用时间从", font=("宋体", 11)).pack(side=tk.LEFT)
        self.forbidden_start_menu = tk.OptionMenu(self.forbidden_frame, self.forbidden_start_hour, *hour_options)
        self.forbidden_start_menu.config(font=("宋体", 11), width=4, state="disabled")
        self.forbidden_start_menu.pack(side=tk.LEFT, padx=2)

        tk.Label(self.forbidden_frame, text="时到", font=("宋体", 11)).pack(side=tk.LEFT)
        self.forbidden_end_menu = tk.OptionMenu(self.forbidden_frame, self.forbidden_end_hour, *hour_options)
        self.forbidden_end_menu.config(font=("宋体", 11), width=4, state="disabled")
        self.forbidden_end_menu.pack(side=tk.LEFT, padx=2)
        tk.Label(self.forbidden_frame, text="时", font=("宋体", 11)).pack(side=tk.LEFT)

        tk.Button(self.root, text="生成时间戳", command=self.__generate,
                  bg="#4CAF50", fg="white", font=("黑体", 13, "bold"), cursor="hand2"
                  ).grid(row=8, column=0, columnspan=2, pady=20, padx=10, sticky="ew")

        tk.Label(self.root,
                 text="使用说明:\n1. 输入日期时间范围\n2. 输入要生成的个数\n3. 点击生成并选择保存位置\n4. 选择是否跳过特定时间段（若是则设置时间范围）",
                 justify="left", fg="gray"
                 ).grid(row=9, column=0, columnspan=2, padx=10, pady=10, sticky="w")

        contact_label = tk.Label(self.root, text="✉", justify="right", fg="blue", font=("宋体", 20), cursor="hand2")
        contact_label.grid(row=9, column=0, columnspan=2, padx=10, pady=0, sticky="se")
        contact_label.bind("<Button-1>", lambda e: self.contact_me())

    def _toggle_forbidden_hours(self):
        """配置跳过的时间段"""
        if self.checkbox_skip_time_period.get():
            self.forbidden_start_menu.config(state="normal", cursor="hand2")
            self.forbidden_end_menu.config(state="normal", cursor="hand2")
        else:
            self.forbidden_start_menu.config(state="disabled", cursor="arrow")
            self.forbidden_end_menu.config(state="disabled", cursor="arrow")

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
        count = self.count.get()
        try:
            count = int(float(count))
            if count <= 0:
                raise ValueError(0)
            elif count > 99999:
                raise ValueError(1)
        except ValueError as e:
            if e.args[0] == 1:
                messagebox.showerror("错误", "生成个数不能超过 99999！")
            elif e.args[0] == 0:
                messagebox.showerror("错误", "生成个数必须为大于 0 的整数！")
            else:
                messagebox.showerror("错误", str(e))
            return
        else:
            self.entry_count.delete(0, tk.END)
            self.entry_count.insert(tk.END, str(count))

        # 处理禁用时段
        skip_period = self.checkbox_skip_time_period.get()
        forbidden_start_h = int(self.forbidden_start_hour.get()) if skip_period else -1
        forbidden_end_h = int(self.forbidden_end_hour.get()) if skip_period else -1

        # 生成随机时间
        timestamps = []
        random.seed(int(time() * 1e3) & 0xffffffff)  # 毫秒级，截取8位十六进制以兼容旧版随机数库
        delta = int((end_dt - start_dt).total_seconds())

        attempts = 0
        max_attempts = count * 10  # 防止无限循环，最多尝试总个数的10倍多
        while len(timestamps) < count and attempts < max_attempts:
            random_seconds = random.randint(0, delta)
            generated_dt = start_dt + timedelta(seconds=random_seconds)
            current_hour = generated_dt.hour

            if skip_period:
                is_forbidden = False
                if forbidden_start_h <= forbidden_end_h:  # 一般禁用情况
                    if forbidden_start_h <= current_hour < forbidden_end_h:
                        is_forbidden = True
                else:  # 过0点的禁用情况
                    if current_hour >= forbidden_start_h or current_hour < forbidden_end_h:
                        is_forbidden = True

                if is_forbidden:  # 不符合条件，重新生成时间戳
                    attempts += 1
                    continue

            timestamps.append(generated_dt.strftime("%Y-%m-%d %H:%M:%S"))
            attempts += 1

        if len(timestamps) < count:
            messagebox.showwarning("警告",
                                   f"由于禁用时间段过于严格，未能生成{count}个时间戳。实际生成了{len(timestamps)}个。")

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

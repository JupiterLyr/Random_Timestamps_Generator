# 接龙文本生成器

一个基于 PyQt6 的桌面工具，用于将 CSV 名单随机排序，并生成适合群接龙使用的 TXT 文本。

## 功能

- 导入 UTF-8 或 GBK 编码的 CSV 名单。
- 随机排列名单，并支持重复刷新排序结果。
- 统计第二列附加文字的出现次数。
- 在导出前预览排序结果。
- 将完整结果导出为 UTF-8 编码的 TXT 文件，或复制到剪贴板（仅在线工具支持）。

## 环境要求

- Python 3.8 或更高版本
- PyQt6

安装依赖：

```bash
pip install PyQt6
```

## 运行桌面版本

在项目根目录执行：

```bash
python main.py
```

## CSV 格式

CSV 文件的第一行第一列作为接龙说明文字。从第二行开始，每行填写一条名单：

```csv
本次接龙名单
张三,早班
李四,晚班
王五,
```

- 第一列为姓名，姓名为空的行会被忽略。
- 第二列为可选的附加文字；为空时，导出内容只显示姓名，不添加连接符 `-`。
- 文件至少应包含一行说明文字和一行有效名单。

## 项目结构

```text
随机时间戳生成器/
├── main.py
├── mainwindow.py
├── ui.py
├── how2use.py
├── LICENSE
├── README.md
├── others/
│   ├── chain_text_gen.py
│   └── random_timestamp_gen.py
├── resource/
│   ├── chain_text_gen.qss
│   ├── chain_text_gen_instruction.txt
│   ├── icon.ico
│   └── icon.png
└── web/
    ├── app.js
    ├── index.html
    ├── instruction.txt
    └── styles.css
```

## 许可证

本项目使用 [MIT License](LICENSE)。

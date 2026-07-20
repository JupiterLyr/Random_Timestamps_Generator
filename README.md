# 项目说明

本仓库包含两个独立的小工具：

1. [群接龙文本生成器](#section-1)
2. [随机时间戳生成器](#section-2)

<div id="section-1"></div>

## 群接龙文本生成器

一个用于整理 CSV 名单、随机排序并生成群接龙文本的工具，提供两种形式：

- 客户端：基于 PyQt6 的桌面版本。
- Web 端：可在浏览器中直接访问使用的在线版本，[<u>点击此处前往</u>](https://jupiterlyr.github.io/Random_Timestamps_Generator/)。

### 客户端

客户端代码位于项目根目录，主要包括：

- `main.py`
- `mainwindow.py`
- `ui.py`
- `how2use.py`
- `resource/`

功能特点：

- 导入 UTF-8 或 GBK 编码的 CSV 名单。
- 随机排列名单，并支持重复刷新排序结果。
- 统计第二列附加文字的出现次数。
- 在导出前预览排序结果。
- 将完整结果导出为 UTF-8 编码的 TXT 文件。

环境要求：

- Python 3.8 或更高版本
- PyQt6

安装依赖：

```bash
pip install PyQt6
```

运行客户端：

```bash
python main.py
```

### Web 端

Web 端代码位于 `web/` 目录，可在线访问。

主要文件：

- `web/index.html`
- `web/app.js`
- `web/styles.css`
- `web/instruction.txt`

功能特点：

- 浏览器内导入并处理名单。
- 生成适合群接龙使用的文本内容，功能与客户端相同。
- 支持将结果复制到剪贴板，也支持直接下载为 TXT。

### CSV 格式

CSV 文件的第一行第一列作为接龙说明文字。从第二行开始，每行填写一条名单：

示例模板可直接[<u>点击下载</u>](./resource/data_template.csv?raw=1)，或访问 `resource/data_template.csv` 手动下载。

```csv
本次接龙名单
张三,早班
李四,
王五,晚班
```

- 除首行外，第一列为姓名，姓名为空的行会被忽略。
- 第二列为可选的附加文字；为空时，导出内容只显示姓名，不添加连接符 `-`。
- 文件至少应包含一行说明文字和一行有效名单。

<div id="section-2"></div>

## 随机时间戳生成器

这是一个单文件工具，代码位于 `others/random_timestamp_gen.py`。

该工具与群接龙文本生成器相互独立，用于生成随机时间戳。

运行方式：

```bash
python others/random_timestamp_gen.py
```

## 项目结构

```text
projects/
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

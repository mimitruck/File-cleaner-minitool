# File-cleaner-minitool (Data Cleaner GUI)

A lightweight open-source desktop tool to **preview** and **clean** tabular data (CSV / Excel) with a simple GUI built on **PySide6** + **pandas**.

一个轻量级开源桌面小工具：用于 **预览** 与 **清洗** 表格数据（CSV / Excel），GUI 基于 **PySide6** + **pandas**。

---

## NOTICE / 重要声明

**本项目为个人独立开发，与任何雇主无关，不包含任何公司内部数据或机密信息。**  
**This is an independent personal project and is not affiliated with any employer. It contains no proprietary or confidential company data.**

---

## Features / 功能

- Load CSV / Excel (**.csv / .xlsx / .xls**)  
  支持载入 CSV / Excel（**.csv / .xlsx / .xls**）
- Preview first N rows (configurable)  
  可设置预览前 N 行
- Convert dtype for a selected column (**string / int / float / datetime**)  
  对选中列进行类型转换（**string / int / float / datetime**）
- Regex-based cleaning for a selected column (pattern + replacement)  
  对选中列进行正则清洗（pattern + replacement）
- Save as **CSV / XLSX**  
  导出为 **CSV / XLSX**

---

## Requirements / 环境要求

- Python **3.10+** recommended（推荐 Python **3.10+**）
- Windows / macOS / Linux  
  （Windows 上测试体验最佳 / Best tested on Windows）

---

## Installation / 安装依赖

### 1) Install dependencies / 安装依赖

```bash
pip install -r requirements.txt
```


---

## Run / 运行方式

### Windows PowerShell


```powershell
cd "C:\path\to\File-cleaner-minitool\data_cleaner_minitool"
$env:PYTHONPATH = "src"
python -m data_cleaner_minitool
```

### Windows PowerShell

```powershell
cd "C:\path\to\File-cleaner-minitool\data_cleaner_minitool"; $env:PYTHONPATH="src"; python -m data_cleaner_minitool
```

---

## Usage / 使用说明（GUI）

1. Click **Select File** to open a CSV/Excel file  
   点击 **Select File** 选择 CSV/Excel 文件
2. Set **Preview rows** to control how many rows to display  
   设置 **Preview rows** 控制预览行数
3. Choose a **Column**, select target type in **To**, then click **Convert**  
   选择 **Column** → 选择 **To** 类型 → 点击 **Convert**
4. Enter a regex in **Regex** and replacement text in **repl** (can be empty), then click **Clean**  
   在 **Regex** 输入正则，在 **repl** 输入替换内容（可为空）→ 点击 **Clean**
5. Choose export format in **Export**, then click **Save As** to save  
   在 **Export** 选择导出格式 → 点击 **Save As** 保存

---

## Notes / 说明

- Regex cleaning is applied after: `to string → lower → strip → replace → collapse spaces`  
  正则清洗流程：`转 string → 小写 → 去首尾空格 → 正则替换 → 合并多余空格`
- Large files may be slow to preview (GUI preview uses `head(n)`)  
  大文件预览可能较慢（预览仅显示 `head(n)`）

---

## License / 许可证

MIT License — see `LICENSE.txt`.

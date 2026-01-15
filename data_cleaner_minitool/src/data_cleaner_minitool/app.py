# src/data_cleaner_minitool/app.py
from __future__ import annotations

import os
from typing import Optional

import pandas as pd
from PySide6.QtCore import Slot
from PySide6.QtWidgets import (
    QComboBox,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSpinBox,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from .core import clean_text_series, convert_column, ensure_extension, export_df, read_path


class MainWindow(QMainWindow):
    """
    小工具：文件预览 + 选列类型转换 + 正则清洗 + 导出
    Utility: Preview + dtype convert + regex clean + export
    """

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Data Cleaner GUI (PySide6 + pandas)")
        self.resize(1100, 600)

        # 保存当前 DataFrame（加载后才能操作）
        # Hold current df in memory (required for operations)
        self.df: Optional[pd.DataFrame] = None

        # 保存路径（可选）
        self.input_path: str = ""
        self.output_path: str = ""

        # ---- central + root layout ----
        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)

        # =========================
        # Row 1: Load file
        # =========================
        row_load = QHBoxLayout()
        root.addLayout(row_load)

        self.btn_pick = QPushButton("Select File")
        self.btn_pick.clicked.connect(self.pick_file)
        row_load.addWidget(self.btn_pick)

        self.in_edit = QLineEdit()
        self.in_edit.setPlaceholderText("Input file path...")
        row_load.addWidget(self.in_edit, stretch=1)

        # =========================
        # Row 2: Preview + Convert + Clean
        # =========================
        row_ops = QHBoxLayout()
        root.addLayout(row_ops)

        row_ops.addWidget(QLabel("Preview rows:"))
        self.pre_spin = QSpinBox()
        self.pre_spin.setRange(1, 500)
        self.pre_spin.setValue(10)
        self.pre_spin.setFixedWidth(70)
        self.pre_spin.valueChanged.connect(self.show_preview)  # auto refresh
        row_ops.addWidget(self.pre_spin)

        row_ops.addSpacing(10)

        row_ops.addWidget(QLabel("Column:"))
        self.col_combo = QComboBox()
        self.col_combo.setMinimumWidth(180)
        row_ops.addWidget(self.col_combo)

        row_ops.addWidget(QLabel("To:"))
        self.type_combo = QComboBox()
        self.type_combo.addItems(["string", "int", "float", "datetime"])
        row_ops.addWidget(self.type_combo)

        self.btn_convert = QPushButton("Convert")
        self.btn_convert.clicked.connect(self.convert_selected)
        row_ops.addWidget(self.btn_convert)

        row_ops.addSpacing(12)

        row_ops.addWidget(QLabel("Regex:"))
        self.regex_edit = QLineEdit()
        self.regex_edit.setPlaceholderText(r"e.g. [^0-9a-z\s]")
        self.regex_edit.setFixedWidth(220)
        row_ops.addWidget(self.regex_edit)

        row_ops.addWidget(QLabel("repl:"))
        self.repl_edit = QLineEdit()
        self.repl_edit.setPlaceholderText("space or empty")
        self.repl_edit.setFixedWidth(90)
        row_ops.addWidget(self.repl_edit)

        self.btn_clean = QPushButton("Clean")
        self.btn_clean.clicked.connect(self.clean_selected)
        row_ops.addWidget(self.btn_clean)

        row_ops.addStretch(1)

        # =========================
        # Row 3: Export
        # =========================
        row_export = QHBoxLayout()
        root.addLayout(row_export)

        row_export.addWidget(QLabel("Export:"))

        self.out_type = QComboBox()
        self.out_type.addItems(["csv", "xlsx"])
        self.out_type.setFixedWidth(80)
        row_export.addWidget(self.out_type)

        self.out_edit = QLineEdit()
        self.out_edit.setPlaceholderText("Output file path...")
        row_export.addWidget(self.out_edit, stretch=1)

        self.btn_choose_out = QPushButton("Save As")
        self.btn_choose_out.clicked.connect(self.save_as)
        row_export.addWidget(self.btn_choose_out)

        

        # =========================
        # Preview Table
        # =========================
        root.addWidget(QLabel("Data Preview:"))

        self.preview = QTableWidget()
        self.preview.setSortingEnabled(False)  # ✅ 预览通常不需要排序，减少开销
        root.addWidget(self.preview)

        self.set_ops_enabled(False)

    # -------------------------
    # helper / helpers
    # -------------------------
    def set_ops_enabled(self, enabled: bool) -> None:
        """
        启用/禁用需要 df 的控件
        Enable/disable controls that require df
        """
        self.pre_spin.setEnabled(enabled)
        self.col_combo.setEnabled(enabled)
        self.type_combo.setEnabled(enabled)
        self.btn_convert.setEnabled(enabled)
        self.regex_edit.setEnabled(enabled)
        self.repl_edit.setEnabled(enabled)
        self.btn_clean.setEnabled(enabled)
        self.out_type.setEnabled(enabled)
        self.out_edit.setEnabled(enabled)
        self.btn_choose_out.setEnabled(enabled)
        

    def _require_df(self) -> bool:
        """
        统一判断 df 是否可用（避免到处写 if self.df is None）
        Return False if df is not loaded
        """
        if self.df is None:
            QMessageBox.information(self, "Info", "No data loaded yet. Please select a file first.")
            return False
        return True

    def populate_columns(self) -> None:
        """
        将 df.columns 填充到列选择下拉框
        Fill column dropdown from df.columns
        """
        assert self.df is not None
        self.col_combo.clear()
        self.col_combo.addItems([str(c) for c in self.df.columns])

    # -------------------------
    # Slots / callbacks
    # -------------------------
    @Slot()
    def pick_file(self) -> None:
        """
        选择文件 -> 读取 -> 列下拉框 -> 刷新预览
        Pick file -> read -> populate columns -> refresh preview
        """
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Choose file",
            "",
            "Data Files (*.csv *.xlsx *.xls);;All Files (*.*)",
        )
        if not path:
            return

        self.input_path = path
        self.in_edit.setText(path)

        try:
            self.df = read_path(path)
            self.populate_columns()
            self.set_ops_enabled(True)
            self.show_preview()
        except Exception as e:
            self.df = None
            self.set_ops_enabled(False)
            QMessageBox.critical(self, "Read Error", str(e))

    @Slot()
    def show_preview(self) -> None:
        """
        把 df.head(n) 渲染到 QTableWidget
        Render df.head(n) to QTableWidget
        """
        if self.df is None or self.df.empty:
            self.preview.clear()
            self.preview.setRowCount(0)
            self.preview.setColumnCount(0)
            return

        n = int(self.pre_spin.value())
        pre_df = self.df.head(n)

        rows = len(pre_df)
        cols = len(pre_df.columns)

        # 先整体设置结构，减少 UI 抖动
        # Set table structure first to reduce UI churn
        self.preview.setUpdatesEnabled(False)
        self.preview.clear()
        self.preview.setRowCount(rows)
        self.preview.setColumnCount(cols)
        self.preview.setHorizontalHeaderLabels([str(c) for c in pre_df.columns])

        for r in range(rows):
            for c in range(cols):
                v = pre_df.iat[r, c]
                if isinstance(v, pd.Timestamp):
                    v = v.strftime("%Y-%m-%d %H:%M:%S")
                item = QTableWidgetItem("" if pd.isna(v) else str(v))
                self.preview.setItem(r, c, item)

        self.preview.setUpdatesEnabled(True)
        self.preview.resizeColumnsToContents()

    @Slot()
    def convert_selected(self) -> None:
        """
        类型转换 Convert dtype on selected column
        """
        if not self._require_df():
            return

        col = self.col_combo.currentText().strip()
        target = self.type_combo.currentText().strip()
        if not col:
            QMessageBox.information(self, "Info", "Please choose a column.")
            return

        try:
            convert_column(self.df, col, target)  # in-place
            self.show_preview()
        except Exception as e:
            QMessageBox.critical(self, "Convert Error", str(e))

    @Slot()
    def clean_selected(self) -> None:
        """
        正则清洗 Apply regex cleaning on selected column
        """
        if not self._require_df():
            return

        col = self.col_combo.currentText().strip()
        pattern = self.regex_edit.text().strip()
        repl = self.repl_edit.text()

        if not col:
            QMessageBox.information(self, "Info", "Please choose a column.")
            return
        if not pattern:
            QMessageBox.information(self, "Info", "Please enter a regex pattern.")
            return

        try:
            self.df[col] = clean_text_series(self.df[col], pattern=pattern, repl=repl)
            self.show_preview()
        except Exception as e:
            QMessageBox.critical(self, "Clean Error", str(e))

    @Slot()
    def choose_output_path(self) -> None:
        """
        选择输出文件路径（不写文件）
        Choose output file path (does not write yet)
        """
        fmt = self.out_type.currentText().strip().lower()
        default_name = f"output.{fmt}"
        filter_str = "CSV (*.csv);;All Files (*.*)" if fmt == "csv" else "Excel (*.xlsx);;All Files (*.*)"

        path, _ = QFileDialog.getSaveFileName(
            self,
            "Save file",
            os.path.join(os.getcwd(), default_name),
            filter_str,
        )
        if not path:
            return

        path = ensure_extension(path, fmt)  # type: ignore[arg-type]
        self.output_path = path
        self.out_edit.setText(path)

   
    @Slot()
    def save_as(self) -> None:
        if self.df is None:
            QMessageBox.information(self, "Info", "No data loaded yet.")
            return

        fmt = self.out_type.currentText().strip().lower()
        default_name = f"output.{fmt}"
        filter_str = "CSV (*.csv);;All Files (*.*)" if fmt == "csv" else "Excel (*.xlsx);;All Files (*.*)"

        path, _ = QFileDialog.getSaveFileName(
            self,
            "Save file",
            os.path.join(os.getcwd(), default_name),
            filter_str,
        )
        if not path:
            return

        path = ensure_extension(path, fmt)
        self.out_edit.setText(path)
        try:
   
            if fmt == "csv":
                self.df.to_csv(path, index=False)
            else:
                self.df.to_excel(path, index=False)

  
            if not os.path.exists(path):
                QMessageBox.warning(self, "Not Found", f"File not found:\n{path}")
                return

 
            QMessageBox.information(self, "Saved", f"Saved to:\n{path}")
            os.startfile(os.path.dirname(path))

        except Exception as e:
            QMessageBox.critical(self, "Export Error", f"{type(e).__name__}: {e}")


      
       


    

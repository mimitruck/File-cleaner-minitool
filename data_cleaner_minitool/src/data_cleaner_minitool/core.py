# src/data_cleaner_gui/core.py
from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Literal

import pandas as pd

SupportedExt = Literal[".csv", ".xlsx", ".xls"]
ExportFmt = Literal["csv", "xlsx"]


@dataclass(frozen=True)
class FileSpec:
    """
    文件规格 / File specification
    """
    path: str
    ext: SupportedExt


def detect_file(path: str) -> FileSpec:
    """
    检测文件扩展名（仅允许 csv/xlsx/xls）
    Detect file extension (allow csv/xlsx/xls only)
    """
    ext = os.path.splitext(path)[1].lower()
    if ext not in (".csv", ".xlsx", ".xls"):
        raise ValueError(f"Unsupported file type: {ext}")
    return FileSpec(path=path, ext=ext)  # type: ignore[arg-type]


def read_path(path: str) -> pd.DataFrame:
    """
    读取文件到 DataFrame（支持 csv/xlsx/xls）
    Read file into a DataFrame (supports csv/xlsx/xls)
    """
    spec = detect_file(path)
    if spec.ext == ".csv":
        return pd.read_csv(spec.path)
    # xlsx/xls
    return pd.read_excel(spec.path)


def convert_column(df: pd.DataFrame, col: str, target: str) -> None:
    """
    将 df 的某一列转换为指定类型（原地修改 df）
    Convert ONE column to target dtype (in-place)

    target: "int" | "float" | "datetime" | "string"
    """
    if col not in df.columns:
        raise KeyError(f"Column not found: {col}")

    if target == "int":
        # pandas 可空整型 Int64，允许 NaN
        df[col] = pd.to_numeric(df[col], errors="coerce").astype("Int64")
    elif target == "float":
        df[col] = pd.to_numeric(df[col], errors="coerce")
    elif target == "datetime":
        df[col] = pd.to_datetime(df[col], errors="coerce")
    elif target == "string":
        df[col] = df[col].astype("string")
    else:
        raise ValueError(f"Unknown target type: {target}")


def clean_text_series(col: pd.Series, pattern: str, repl: str = " ") -> pd.Series:
    """
    文本清洗流水线 Text cleaning pipeline:
    1) cast to string
    2) lower + strip
    3) regex replace pattern -> repl
    4) collapse whitespace

    注意 / Note:
    - pattern 为空则跳过正则替换
    - repl 允许空字符串
    """
    s = col.astype("string").str.lower().str.strip()

    if pattern and pattern.strip():
        s = s.str.replace(pattern, repl, regex=True)

    s = s.str.replace(r"\s+", " ", regex=True).str.strip()
    return s


def ensure_extension(path: str, fmt: ExportFmt) -> str:
    """
    如果用户没写扩展名，按格式自动补全
    If user did not type extension, append based on fmt
    """
    low = path.lower()
    if fmt == "csv" and not low.endswith(".csv"):
        return path + ".csv"
    if fmt == "xlsx" and not low.endswith(".xlsx"):
        return path + ".xlsx"
    return path


def export_df(df: pd.DataFrame, path: str, fmt: ExportFmt) -> None:
    """
    导出 DataFrame
    Export DataFrame
    """
    if fmt == "csv":
        df.to_csv(path, index=False)
    elif fmt == "xlsx":
        df.to_excel(path, index=False)
    else:
        raise ValueError(f"Unknown export format: {fmt}")

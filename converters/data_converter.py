# FileMorph/converters/data_converter.py
from pathlib import Path

import pandas as pd

from converters.base import BaseConverter


class DataConverter(BaseConverter):
    @property
    def supported_input_formats(self) -> list[str]:
        return ["csv", "json", "xlsx"]

    @property
    def supported_output_formats(self) -> list[str]:
        return ["csv", "json", "xlsx"]

    def convert(self, src: Path, dst: Path, options: dict) -> None:
        src_ext = src.suffix.lower().lstrip(".")
        dst_ext = dst.suffix.lower().lstrip(".")

        dataframe = self._read_to_dataframe(src, src_ext, options)
        self._write_from_dataframe(dataframe, dst, dst_ext, options)

    def _read_to_dataframe(self, src: Path, src_ext: str, options: dict) -> pd.DataFrame:
        delimiter = options.get("delimiter", ",") or ","
        encoding = options.get("encoding", "utf-8") or "utf-8"
        sheet_name = options.get("sheet_name", "Sheet1") or "Sheet1"

        if src_ext == "csv":
            return pd.read_csv(src, sep=delimiter, encoding=encoding)

        if src_ext == "json":
            return pd.read_json(src)

        if src_ext == "xlsx":
            return pd.read_excel(src, sheet_name=sheet_name)

        raise ValueError(f"Неподдерживаемый входной формат данных: {src_ext}")

    def _write_from_dataframe(
        self,
        dataframe: pd.DataFrame,
        dst: Path,
        dst_ext: str,
        options: dict
    ) -> None:
        delimiter = options.get("delimiter", ",") or ","
        encoding = options.get("encoding", "utf-8") or "utf-8"
        sheet_name = options.get("sheet_name", "Sheet1") or "Sheet1"

        if dst_ext == "csv":
            dataframe.to_csv(dst, index=False, sep=delimiter, encoding=encoding)
            return

        if dst_ext == "json":
            dataframe.to_json(dst, orient="records", force_ascii=False, indent=2)
            return

        if dst_ext == "xlsx":
            dataframe.to_excel(dst, index=False, sheet_name=sheet_name)
            return

        raise ValueError(f"Неподдерживаемый выходной формат данных: {dst_ext}")
import csv
from typing import List, Dict
import re
from unidecode import unidecode
from io import StringIO
from datetime import datetime


class SimpleDF:
    def __init__(self, rows=None, columns=None):
        self.rows = rows or []
        if columns is not None:
            self.columns = list(columns)
        elif self.rows:
            self.columns = list(self.rows[0].keys())
        else:
            self.columns = []
        self._normalize_rows()

    def __len__(self):
        return len(self.rows)

    def __getitem__(self, idx):
        return self.rows[idx]  # df[i]["col"]
    
    def _normalize_rows(self):
        for row in self.rows:
            for col in self.columns:
                row.setdefault(col, None)

    @classmethod
    def from_records(cls, records, columns=None):
        return cls(rows=records, columns=columns)
    
    @classmethod
    def read_tsv(cls, path, encoding="utf-16", sep="\t"):
        import csv
        with open(path, newline="", encoding=encoding) as f:
            reader = csv.DictReader(f, delimiter=sep)
            rows = list(reader)
            columns = reader.fieldnames
        return cls(rows, columns)
    
    @classmethod
    def from_tsv_text(cls, text, sep="\t", normalize=True, clean_spaces=True):
        reader = csv.DictReader(StringIO(text), delimiter=sep)
        rows = list(reader)
        columns = reader.fieldnames or []

        df = cls(rows=rows, columns=columns)

        if normalize:
            df.normalize_columns()

        if clean_spaces:
            df.clean_all_spaces()
        return df

    def iterrows(self):
        for i, row in enumerate(self.rows):
            yield i, row

    # Agrega una columna si no existe
    def add_column(self, name, default=None):
        if name in self.columns:
            return
        self.columns.append(name)
        for row in self.rows:
            row[name] = default

    # Establece el valor de una columna existente
    def set_column(self, col, value=None):
        """
        Set an existing column to the same value for all rows.
        """
        if col not in self.columns:
            raise KeyError(f"Column '{col}' does not exist")
        for row in self.rows:
            row[col] = value

    # Si la columna no existe la agrega
    def ensure_column(self, col, default=None):
        if col not in self.columns:
            self.columns.append(col)
            for row in self.rows:
                row[col] = default

    def add_row(self, row):
        for col in self.columns:
            row.setdefault(col, None)
        self.rows.append(row)

    def save(self, path, encoding="utf-16", sep="\t"):
        with open(path, "w", newline="", encoding=encoding) as f:
            writer = csv.DictWriter(f, fieldnames=self.columns, delimiter=sep)
            writer.writeheader()
            writer.writerows(self.rows)

    def apply_cell(self, func):
        for row in self.rows:
            for k, v in row.items():
                row[k] = func(v)

    # def rename_columns(self, new_columns):
    #     if len(new_columns) != len(self.columns):
    #         raise ValueError("Column count mismatch")
    #     mapping = dict(zip(self.columns, new_columns))
    #     for row in self.rows:
    #         for old, new in mapping.items():
    #             row[new] = row.pop(old)
    #     self.columns = new_columns

    def rename_columns(self, mapping: dict, strict=True):
        """
        Rename selected columns using a dict mapping.
        mapping:
            {
                "currentColumn": "newColumn",
                ...
            }
        strict:
            - True  -> raise if source column does not exist or target already exists
            - False -> silently skip invalid mappings
        """
        if not mapping:
            return
        # Validate mapping
        valid_map = {}
        for old, new in mapping.items():
            if old not in self.columns:
                if strict:
                    raise KeyError(f"Column '{old}' does not exist")
                continue
            if new in self.columns and new != old:
                if strict:
                    raise KeyError(f"Target column '{new}' already exists")
                continue
            valid_map[old] = new
        if not valid_map:
            return
        # Update columns (preserve order)
        self.columns = [
            valid_map.get(col, col) for col in self.columns
        ]
        # Update rows
        for row in self.rows:
            for old, new in valid_map.items():
                if old in row and old != new:
                    row[new] = row.pop(old)

    def clean_all_spaces(self):
        for row in self.rows:
            for k, v in row.items():
                if isinstance(v, str):
                    row[k] = re.sub(r"\s+", " ", v).strip()

    def index_by(self, key):
        return {row[key]: row for row in self.rows if row.get(key) is not None}
    
    @staticmethod
    def _to_camel_case(name: str) -> str:
        parts = name.split("_")
        return parts[0] + "".join(p.capitalize() for p in parts[1:])

    @staticmethod
    def _is_camel_case(name: str) -> bool:
        return bool(re.fullmatch(r"[a-z]+(?:[A-Z][a-z0-9]*)*", name))


    def normalize_columns(self):
        """
        Normalize column names AND update row keys accordingly.
        """
        col_map = {}

        for c in self.columns:
            new_c = c
            new_c = new_c.replace("[", " ").replace("]", " ").replace(".", " ")
            new_c = new_c.strip()
            new_c = new_c.replace(" ", "_").lower()
            new_c = unidecode(new_c)

            col_map[c] = new_c

        # Update columns list
        self.columns = list(col_map.values())

        # Update every row's keys
        for row in self.rows:
            for old, new in col_map.items():
                if old in row:
                    row[new] = row.pop(old)

    def normalizeColumns(self):
        """
        Convert column names to camelCase AND update row keys accordingly.
        Already-camelCase columns are left untouched.
        """
        col_map = {}

        for c in self.columns:
            # If already camelCase → keep it
            if self._is_camel_case(c):
                col_map[c] = c
                continue

            base = c
            base = base.replace("[", " ").replace("]", " ").replace(".", " ")
            base = base.strip().lower()
            base = unidecode(base)
            base = re.sub(r"\s+", "_", base)

            camel = self._to_camel_case(base)
            col_map[c] = camel

        # Update columns list (preserve order)
        self.columns = list(col_map.values())

        # Update every row's keys
        for row in self.rows:
            for old, new in col_map.items():
                if old in row and old != new:
                    row[new] = row.pop(old)
    
    def remove_columns(self, cols, strict=False):
        """
        Remove one or more columns from the dataframe.

        cols: str | list[str] | tuple[str] | set[str]
        strict: if True, raise KeyError if any column does not exist
        """
        if isinstance(cols, str):
            cols = [cols]
        else:
            cols = list(cols)

        missing = [c for c in cols if c not in self.columns]
        if missing and strict:
            raise KeyError(f"Columns not found: {missing}")

        to_remove = set(c for c in cols if c in self.columns)

        if not to_remove:
            return

        # Update columns list
        self.columns = [c for c in self.columns if c not in to_remove]

        # Remove keys from rows
        for row in self.rows:
            for c in to_remove:
                row.pop(c, None)

    def remove_column(self, col, strict=False):
        self.remove_columns(col, strict=strict)
"""Test stubs for optional database drivers.

The unit tests exercise pure conversion helpers only, so CI does not need live
Oracle or PostgreSQL connections. Runtime users should still install the real
packages from requirements.txt.
"""

import sys
import types
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


if "oracledb" not in sys.modules:
    oracledb = types.ModuleType("oracledb")

    def _missing_connect(*args, **kwargs):
        raise RuntimeError("oracledb.connect is not available in unit tests")

    oracledb.connect = _missing_connect
    sys.modules["oracledb"] = oracledb


if "psycopg" not in sys.modules:
    psycopg = types.ModuleType("psycopg")

    def _missing_connect(*args, **kwargs):
        raise RuntimeError("psycopg.connect is not available in unit tests")

    class _Identifier:
        def __init__(self, *parts):
            self.parts = parts

    class _SQL:
        def __init__(self, text):
            self.text = text

        def format(self, *args, **kwargs):
            return self

        def join(self, values):
            return self

    sql = types.SimpleNamespace(SQL=_SQL, Identifier=_Identifier)
    psycopg.connect = _missing_connect
    psycopg.sql = sql
    sys.modules["psycopg"] = psycopg

# Oracle to PostgreSQL Custom Migrator

A custom Python-based Oracle to PostgreSQL migration/conversion tool.

This project is **not Ora2Pg**. It connects directly to an Oracle database, reads metadata and data, generates PostgreSQL SQL files, and can optionally apply parts of the migration to PostgreSQL.

> Important: Oracle Data Pump `.dmp` files are binary Oracle dump files. This tool does not parse `.dmp` files directly. Import the dump into an Oracle database first, then run this migrator against that Oracle schema.

## Features

The tool can generate PostgreSQL SQL for:

- Tables
- Table data using PostgreSQL `COPY`
- Views
- Indexes
- Foreign keys
- Synonyms as PostgreSQL view replacements
- Basic range/list/hash partitions
- Triggers as PostgreSQL trigger functions
- Procedures and functions as PL/pgSQL routines
- Packages as standalone `package__routine` routines

## Limitations

Oracle and PostgreSQL do not have identical database engines, SQL dialects, or procedural languages. This tool performs **best-effort conversion**, especially for PL/SQL code.

Manual review is required for:

- Oracle packages and package-level state
- Package variables, constants, records, collections, and custom types
- Procedure/function parameters
- Complex triggers
- Autonomous transactions
- Dynamic SQL
- Cursors
- Exception handlers
- Oracle-specific functions
- `DECODE()`
- `CONNECT BY`
- `PIVOT`
- `MODEL`
- Oracle outer join operator `(+)`
- DB links
- Function-based indexes
- Advanced partitioning/subpartitioning

Do not use `--apply-code` until you have reviewed generated files.

## Requirements

### Minimum supported versions

| Component | Minimum supported version | Recommended version | Notes |
|---|---:|---:|---|
| Linux | Any modern Linux distribution | Ubuntu 22.04+ / Debian 12+ / RHEL 9+ | The project is intended for Linux CI and server use. |
| Python | 3.9+ | 3.11+ | Tested with Python 3.9.25 in GitHub Actions-compatible environments. |
| Oracle Database | 12.1+ | 19c+ | `python-oracledb` Thin mode requires Oracle Database 12.1 or newer. |
| PostgreSQL | 10+ | 14+ / 15+ / 16+ | PostgreSQL 10 is the practical minimum because the converter can generate declarative partition DDL. |
| pytest | 8.x | Latest stable | Used only for unit tests. |

### Python dependencies

- `oracledb`
- `psycopg[binary]`

You also need:

- Network access to an Oracle database
- Network access to a PostgreSQL database
- Permission to read Oracle data dictionary views for the source schema
- Permission to create schemas, tables, indexes, views, constraints, functions, procedures, and triggers in PostgreSQL if you use the apply options

Install dependencies:

```bash
pip install -r requirements.txt
```

Or install directly:

```bash
pip install oracledb "psycopg[binary]"
```

## Project files

```text
oracle-postgres-custom-migrator/
├── oracle_to_postgres_advanced.py
├── requirements.txt
├── README.md
├── tests/
├── .github/workflows/ci.yml
├── .gitignore
└── LICENSE
```

## Running tests

This repository includes unit tests for the pure conversion helpers. They do not require live Oracle or PostgreSQL databases.

```bash
python -m pip install pytest
pytest -q
```

`pytest` exits with code `5` when it finds zero tests. The included `tests/` directory prevents that GitHub Actions failure.

## Basic usage

Generate SQL files only:

```bash
python oracle_to_postgres_advanced.py \
  --oracle-user HR \
  --oracle-password oracle_password \
  --oracle-dsn "localhost:1521/ORCLPDB1" \
  --oracle-schema HR \
  --pg-schema public \
  --out-dir ./converted_pg_sql \
  --convert-partitions
```

This creates:

```text
converted_pg_sql/
├── 01_schema_tables.sql
├── 02_views.sql
├── 03_indexes.sql
├── 04_foreign_keys.sql
├── 05_synonyms_as_views.sql
├── 06_triggers_review.sql
├── 07_routines_review.sql
└── 08_packages_review.sql
```

## Apply tables and copy data

```bash
python oracle_to_postgres_advanced.py \
  --oracle-user HR \
  --oracle-password oracle_password \
  --oracle-dsn "localhost:1521/ORCLPDB1" \
  --oracle-schema HR \
  --pg-dsn "postgresql://postgres:postgres_password@localhost:5432/targetdb" \
  --pg-schema public \
  --out-dir ./converted_pg_sql \
  --drop-existing \
  --convert-partitions \
  --apply-tables \
  --copy-data
```

## Apply views, indexes, foreign keys, and synonyms

Run this after tables and data are loaded:

```bash
python oracle_to_postgres_advanced.py \
  --oracle-user HR \
  --oracle-password oracle_password \
  --oracle-dsn "localhost:1521/ORCLPDB1" \
  --oracle-schema HR \
  --pg-dsn "postgresql://postgres:postgres_password@localhost:5432/targetdb" \
  --pg-schema public \
  --out-dir ./converted_pg_sql \
  --apply-post-data-objects
```

## Review and optionally apply converted code

Generated procedural code is written to:

```text
converted_pg_sql/06_triggers_review.sql
converted_pg_sql/07_routines_review.sql
converted_pg_sql/08_packages_review.sql
```

Review and edit these files before applying them.

After review:

```bash
python oracle_to_postgres_advanced.py \
  --oracle-user HR \
  --oracle-password oracle_password \
  --oracle-dsn "localhost:1521/ORCLPDB1" \
  --oracle-schema HR \
  --pg-dsn "postgresql://postgres:postgres_password@localhost:5432/targetdb" \
  --pg-schema public \
  --out-dir ./converted_pg_sql \
  --apply-code
```

## Migrate selected tables only

```bash
python oracle_to_postgres_advanced.py \
  --oracle-user HR \
  --oracle-password oracle_password \
  --oracle-dsn "localhost:1521/ORCLPDB1" \
  --oracle-schema HR \
  --pg-dsn "postgresql://postgres:postgres_password@localhost:5432/targetdb" \
  --pg-schema public \
  --tables EMPLOYEES DEPARTMENTS JOBS \
  --apply-tables \
  --copy-data
```

## Useful options

| Option | Description |
|---|---|
| `--oracle-user` | Oracle username |
| `--oracle-password` | Oracle password |
| `--oracle-dsn` | Oracle DSN, for example `localhost:1521/ORCLPDB1` |
| `--oracle-schema` | Oracle schema owner |
| `--pg-dsn` | PostgreSQL connection string |
| `--pg-schema` | Target PostgreSQL schema, default `public` |
| `--out-dir` | Output directory for generated SQL files |
| `--tables` | Optional list of Oracle tables to migrate |
| `--batch-size` | Fetch/copy batch size, default `5000` |
| `--drop-existing` | Drop target tables before creating them |
| `--preserve-case` | Preserve Oracle object casing instead of lowercasing |
| `--convert-partitions` | Generate basic partition DDL |
| `--no-convert-views` | Skip view conversion |
| `--no-convert-indexes` | Skip index conversion |
| `--no-convert-foreign-keys` | Skip foreign-key conversion |
| `--no-convert-synonyms` | Skip synonym conversion |
| `--no-convert-triggers` | Skip trigger conversion |
| `--no-convert-routines` | Skip procedure/function conversion |
| `--no-convert-packages` | Skip package conversion |
| `--apply-tables` | Execute table DDL in PostgreSQL |
| `--copy-data` | Copy table data into PostgreSQL |
| `--apply-post-data-objects` | Apply views, indexes, foreign keys, and synonym views |
| `--apply-code` | Apply converted triggers/routines/packages after review |
| `--stop-on-error` | Stop immediately when applying SQL fails |

## Recommended migration order

1. Import Oracle `.dmp` into Oracle first, if your source is a dump file.
2. Generate SQL files only.
3. Review `01_schema_tables.sql`.
4. Apply tables.
5. Copy data.
6. Apply views, indexes, foreign keys, and synonym replacement views.
7. Review trigger/routine/package SQL files.
8. Manually fix procedural code where needed.
9. Apply converted code only after review.
10. Validate row counts, constraints, indexes, and application behavior.

## Example Oracle Data Pump flow

```bash
impdp HR/oracle_password@ORCLPDB1 \
  directory=DATA_PUMP_DIR \
  dumpfile=backup.dmp \
  logfile=import.log
```

Then run this migrator against schema `HR`.

## Security notes

Avoid putting passwords directly in shell history for production use. Prefer environment variables, a secrets manager, or your deployment system's secret storage.

## License

MIT License. See [LICENSE](LICENSE).

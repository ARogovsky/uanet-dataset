#!/usr/bin/env python3
"""
sanitize.py — produce the public UA Web Census release from the raw pg_dump.

The script streams the pg_dump *text-format* COPY block of the `raw_domains`
table directly (no PostgreSQL instance required), keeps only a vetted
whitelist of columns, coarsens the observation timestamp to a day, and writes
a sanitized Parquet (or CSV) file. Input may be a plain .sql or a gzipped
.sql.gz file.

Only the columns listed in OUTPUT_SCHEMA are read out (by their fixed position
in the source row). Every other source column — database bookkeeping fields,
internal pipeline state and any personal data — is discarded and never
materialized in the output.

Usage:
    python scripts/sanitize.py INPUT.sql.gz --out build/ua-web-census-2026.parquet
    python scripts/sanitize.py INPUT.sql.gz --format csv --out build/ua.csv
    python scripts/sanitize.py INPUT.sql.gz --sample 1000 --sample-out sample/ua_sample_1k.parquet
"""
from __future__ import annotations

import argparse
import datetime as dt
import gzip
import io
import random
import sys

# Number of tab-separated fields per row in the source COPY block. Rows that
# do not have exactly this many fields are skipped defensively.
RAW_NCOLS = 45

# Public schema: (output_name, source_index, type).
# `source_index` is the 0-based position of the column in the source row.
# Columns not listed here are intentionally dropped and never read.
# "observed_day" is derived from a millisecond epoch column (coarsened to day).
TEXT, INT, FLOAT, BOOL, DATE = "text", "int", "float", "bool", "date"
OUTPUT_SCHEMA = [
    ("domain", 0, TEXT),
    ("initial_domain", 3, TEXT),
    ("final_domain", 4, TEXT),
    ("ip_address", 5, TEXT),
    ("reverse_dns_name", 6, TEXT),
    ("http_status", 7, INT),
    ("http_status_text", 8, TEXT),
    ("response_time_seconds", 9, FLOAT),
    ("title", 10, TEXT),
    ("description", 12, TEXT),
    ("keywords", 11, TEXT),
    ("is_mobile_friendly", 13, BOOL),
    ("tls_version", 14, TEXT),
    ("cipher_suite", 15, TEXT),
    ("key_algorithm", 16, TEXT),
    ("ssl_cert_subject", 17, TEXT),
    ("ssl_cert_issuer", 18, TEXT),
    ("ssl_cert_valid_from_ms", 19, INT),
    ("ssl_cert_valid_to_ms", 20, INT),
    ("spf_record", 21, TEXT),
    ("dmarc_record", 22, TEXT),
    ("body_sha256", 25, TEXT),
    ("content_length", 26, INT),
    ("http_version", 27, TEXT),
    ("body_word_count", 28, INT),
    ("body_line_count", 29, INT),
    ("content_type", 30, TEXT),
    ("canonical_url", 31, TEXT),
    ("cert_fingerprint_sha256", 32, TEXT),
    ("cert_is_self_signed", 34, BOOL),
    ("cert_is_wildcard", 35, BOOL),
    ("cert_is_mismatched", 36, BOOL),
    ("meta_refresh_url", 37, TEXT),
    ("observed_day", 23, DATE),  # coarsened from ms epoch
]

COPY_PREFIX = "COPY public.raw_domains "

# pg_dump text-format backslash escapes within a field.
_UNESCAPE = {
    "b": "\b", "f": "\f", "n": "\n", "r": "\r",
    "t": "\t", "v": "\v", "\\": "\\",
}


def unescape(field: str) -> str | None:
    """Decode a single pg COPY text field. r'\\N' means SQL NULL."""
    if field == r"\N":
        return None
    if "\\" not in field:
        return field
    out, i, n = [], 0, len(field)
    while i < n:
        c = field[i]
        if c == "\\" and i + 1 < n:
            out.append(_UNESCAPE.get(field[i + 1], field[i + 1]))
            i += 2
        else:
            out.append(c)
            i += 1
    return "".join(out)


def to_bool(v):
    return None if v is None else (v == "t")


def to_int(v):
    if v is None:
        return None
    try:
        return int(v)
    except ValueError:
        return None


def to_float(v):
    if v is None:
        return None
    try:
        return float(v)
    except ValueError:
        return None


def to_day(v):
    if v is None:
        return None
    try:
        ms = int(v)
    except ValueError:
        return None
    return dt.datetime.fromtimestamp(ms / 1000, dt.timezone.utc).date()


_CAST = {TEXT: lambda v: v, INT: to_int, FLOAT: to_float, BOOL: to_bool, DATE: to_day}


def open_dump(path: str):
    if path.endswith(".gz"):
        return gzip.open(path, "rt", encoding="utf-8", errors="replace")
    return io.open(path, "rt", encoding="utf-8", errors="replace")


def iter_records(path: str):
    """Yield sanitized records (dict output_name -> value) from the dump."""
    in_copy = False
    with open_dump(path) as fh:
        for line in fh:
            if not in_copy:
                if line.startswith(COPY_PREFIX):
                    in_copy = True
                continue
            if line.startswith("\\."):
                break
            raw = line.rstrip("\n").split("\t")
            if len(raw) != RAW_NCOLS:
                # malformed / continuation line; skip defensively
                continue
            rec = {}
            for out_name, idx, typ in OUTPUT_SCHEMA:
                rec[out_name] = _CAST[typ](unescape(raw[idx]))
            yield rec


def build_table(records):
    import pyarrow as pa

    cols = {name: [] for name, _, _ in OUTPUT_SCHEMA}
    n = 0
    for rec in records:
        for name in cols:
            cols[name].append(rec[name])
        n += 1
    fields, arrays = [], []
    type_map = {
        TEXT: pa.string(), INT: pa.int64(), FLOAT: pa.float64(),
        BOOL: pa.bool_(), DATE: pa.date32(),
    }
    for name, _, typ in OUTPUT_SCHEMA:
        fields.append(pa.field(name, type_map[typ]))
        arrays.append(pa.array(cols[name], type=type_map[typ]))
    return pa.Table.from_arrays(arrays, schema=pa.schema(fields)), n


def write_parquet(records, out_path: str):
    import pyarrow.parquet as pq

    table, n = build_table(records)
    pq.write_table(table, out_path, compression="zstd")
    return n


def write_csv(records, out_path: str):
    import csv

    names = [name for name, _, _ in OUTPUT_SCHEMA]
    n = 0
    with open(out_path, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=names)
        w.writeheader()
        for rec in records:
            w.writerow({k: ("" if v is None else v) for k, v in rec.items()})
            n += 1
    return n


def reservoir_sample(records, k: int, seed: int):
    """Deterministic reservoir sample of k records over the whole stream."""
    rng = random.Random(seed)
    reservoir, seen = [], 0
    for rec in records:
        seen += 1
        if len(reservoir) < k:
            reservoir.append(rec)
        else:
            j = rng.randint(0, seen - 1)
            if j < k:
                reservoir[j] = rec
    return reservoir


def main(argv=None):
    p = argparse.ArgumentParser(description="Sanitize the raw UA dump for release.")
    p.add_argument("input", help="raw pg_dump file (.sql or .sql.gz)")
    p.add_argument("--out", help="full sanitized output path")
    p.add_argument("--format", choices=["parquet", "csv"], default="parquet")
    p.add_argument("--sample", type=int, default=0,
                   help="also write a random sample of N rows")
    p.add_argument("--sample-out", default="sample/ua_sample_1k.parquet")
    p.add_argument("--sample-seed", type=int, default=42)
    args = p.parse_args(argv)

    if not args.out and not args.sample:
        p.error("nothing to do: pass --out and/or --sample")

    if args.out:
        writer = write_parquet if args.format == "parquet" else write_csv
        n = writer(iter_records(args.input), args.out)
        print(f"[full]   {n:,} rows -> {args.out}", file=sys.stderr)

    if args.sample:
        rows = reservoir_sample(iter_records(args.input), args.sample, args.sample_seed)
        if args.sample_out.endswith(".csv"):
            write_csv(rows, args.sample_out)
        else:
            write_parquet(rows, args.sample_out)
        print(f"[sample] {len(rows):,} rows -> {args.sample_out} "
              f"(seed={args.sample_seed})", file=sys.stderr)


if __name__ == "__main__":
    main()

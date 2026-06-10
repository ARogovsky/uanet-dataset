#!/usr/bin/env python3
"""
load_example.py — minimal loaders for the UA Web Census 2026 dataset.

Examples
--------
Load the bundled 1k sample and print basic stats:

    python scripts/load_example.py

Point at the full release downloaded from Zenodo / Hugging Face:

    python scripts/load_example.py path/to/ua-web-census-2026.parquet
"""
from __future__ import annotations

import sys


def load_with_pyarrow(path: str):
    """Return a pyarrow.Table. No pandas required."""
    import pyarrow.parquet as pq

    return pq.read_table(path)


def load_with_pandas(path: str):
    """Return a pandas.DataFrame (requires pandas + pyarrow)."""
    import pandas as pd

    return pd.read_parquet(path)


def load_from_hub():
    """Stream the dataset from the Hugging Face Hub.

        from datasets import load_dataset
        ds = load_dataset("ARogovsky/uanet-dataset", split="train")
    """
    from datasets import load_dataset

    return load_dataset("ARogovsky/uanet-dataset", split="train")


def summarize(table):
    import pyarrow.compute as pc

    n = table.num_rows
    responded = pc.sum(pc.invert(pc.is_null(table.column("http_status")))).as_py()
    dmarc = pc.sum(pc.invert(pc.is_null(table.column("dmarc_record")))).as_py()
    print(f"rows:            {n:,}")
    print(f"columns:         {table.num_columns}")
    print(f"responded:       {responded:,} ({responded / n:.1%})")
    if responded:
        print(f"DMARC present:   {dmarc:,} ({dmarc / responded:.1%} of responders)")
    print("\nfirst 3 domains:",
          table.column("domain").slice(0, 3).to_pylist())


if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else "sample/ua_sample_1k.parquet"
    print(f"Loading {path} ...\n")
    summarize(load_with_pyarrow(path))

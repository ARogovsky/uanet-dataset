# UA Web Census 2026

An enrichment snapshot of the Ukrainian `.ua` (ccTLD) web.

[![DOI](https://img.shields.io/badge/DOI-pending-blue.svg)](https://zenodo.org/) <!-- replace with Zenodo DOI after release -->
[![Data: CC BY 4.0](https://img.shields.io/badge/Data-CC%20BY%204.0-lightgrey.svg)](LICENSE-DATA)
[![Code: MIT](https://img.shields.io/badge/Code-MIT-green.svg)](LICENSE)

---

## What this is

`UA Web Census 2026` is a structured, per-domain snapshot of the Ukrainian
`.ua` namespace, captured on **27–28 March 2026**. Starting from a seed list of
~500,000 registered `.ua` domains, each was probed and enriched with HTTP, TLS,
DNS and content-level signals.

The release contains **354,947 probed domains**. Of these, **175,182 (49.4%)
resolved and returned an HTTP response** and carry full enrichment; the
remaining ~50.6% did not respond (parked, dead, firewalled or geo-blocked) and
appear with null enrichment columns. Keeping both halves makes the dataset a
*census of probed domains* — the live/dead ratio is itself analyzable — rather
than a curated list of live sites.

Unlike global internet-scan corpora (Censys, Rapid7 Sonar, Common Crawl) or
bare zone-file listings, this dataset combines **single-ccTLD breadth** with
**rich per-domain enrichment** for one national web — a combination that, to
the author's knowledge, has not been published openly.

## Why it might be useful

- **National-scale email security posture** — SPF / DMARC adoption across the
  zone. (Headline finding: **~84.6% of live `.ua` hosts publish no DMARC**.)
- **TLS hygiene** — versions, cipher suites, certificate issuers, key
  algorithms, wildcard/self-signed/mismatch rates.
- **Web ecosystem snapshot** — HTTP status and version distribution, content
  metadata, mobile-friendliness.
- **Longitudinal baseline** — a 2026 reference point for the Ukrainian web.

See [`reports/aggregate_stats.md`](reports/aggregate_stats.md) for the full
zone-level summary.

## Contents

> **Note:** This repository holds the **methodology, schema, sanitization
> scripts and a small sample**. The full dataset is hosted on Zenodo / Hugging
> Face (links below). The repo does **not** carry the bulk data.

```
.
├── README.md
├── DATASET.md                 # data statement: composition, collection, sanitization
├── LICENSE                    # MIT (code)
├── LICENSE-DATA               # CC BY 4.0 (data)
├── schema/
│   └── columns.md             # per-column type and description (34 columns)
├── scripts/
│   ├── sanitize.py            # produces the public release from the raw dump
│   └── load_example.py        # minimal loader (pyarrow / pandas / HF datasets)
├── sample/
│   └── ua_sample_1k.parquet   # 1,000-row random sample for inspection
└── reports/
    └── aggregate_stats.md     # zone-level SPF/DMARC/TLS adoption summary
```

## Data access

- **Zenodo (canonical, DOI):** _link pending release_
- **Hugging Face Datasets:** _link pending release_

```python
# Hugging Face
from datasets import load_dataset
ds = load_dataset("ARogovsky/uanet-dataset", split="train")

# Or the bundled sample, locally:
import pyarrow.parquet as pq
tbl = pq.read_table("sample/ua_sample_1k.parquet")
```

## Methodology

1. **Seed.** A list of ~500,000 registered `.ua` second- and third-level
   domains was assembled as the input set.
2. **Probe.** Each domain was scanned with an **in-house Go-based scanner**
   that performs DNS resolution, an HTTP(S) request, a TLS handshake and
   certificate parse, SPF/DMARC lookups and lightweight HTML extraction in a
   single pass. The scanner is proprietary and is **not** released.
3. **Record.** Results were stored one row per domain. ~49.4% resolved and
   responded; non-responding domains are retained with null enrichment.
4. **Sanitize.** The raw output was passed through
   [`scripts/sanitize.py`](scripts/sanitize.py) to remove personal data and
   operational fields before release (see below).

_Capture window: 27–28 March 2026. Single snapshot, no longitudinal passes in
this release._

## What is intentionally **not** included

This release is deliberately reduced from the raw scan output:

- **The ~500k seed domain list is not published.** Only the probed/enriched
  table is released; the raw seed is withheld.
- **No personal data.** The release contains only externally observable
  properties of public endpoints. Any personal data present in the raw table
  is dropped entirely (not hashed), so it cannot be recovered. No individual
  is identifiable from this dataset.
- **No operational metadata.** Internal pipeline state, run and worker
  identifiers, and database bookkeeping timestamps are stripped.
- **Coarsened time.** The millisecond observation timestamp is reduced to a
  UTC day (`observed_day`).

SPF and DMARC records **are** included per-domain: they are public DNS records
any party can query, and certificate-anomaly flags (self-signed: 1,
mismatched: 3 across the whole snapshot) are effectively empty, so the release
does not function as an attack-target list.

## Limitations

- Single point-in-time snapshot; configurations change.
- Only the responding ~49.4% carries enrichment; non-responding hosts are
  present but sparse.
- Scanner-derived heuristics (mobile-friendliness, content extraction) carry
  the usual false-positive/negative characteristics of automated probing.
- `.ua` second-level registration requires a matching trademark, so the zone
  skews toward third-level (`com.ua`, `org.ua`, regional) names.

## Ethics & responsible use

All data was collected by probing publicly reachable hosts; no authentication
was bypassed and no private systems were accessed. The dataset is intended for
research into web infrastructure, security posture and the resilience of the
Ukrainian web. It must **not** be used to target, attack or harass any host or
operator.

## License

- **Data:** [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) — see [`LICENSE-DATA`](LICENSE-DATA).
- **Code:** MIT — see [`LICENSE`](LICENSE).

> GitHub reports this repository's license as **MIT** (it classifies the
> standard `LICENSE` file, which covers the code). The dataset itself is
> **CC BY 4.0** per `LICENSE-DATA`.

## Citation

```bibtex
@dataset{rogovsky_ua_web_census_2026,
  author    = {Rogovsky, Andrii},
  title     = {UA Web Census 2026: An Enrichment Snapshot of the .ua Web},
  year      = {2026},
  publisher = {Zenodo},
  doi       = {[DOI pending]},
  url        = {[URL pending]}
}
```

## Acknowledgements

Built and maintained by Andrii Rogovsky ([@ARogovsky](https://github.com/ARogovsky)).
Feedback and corrections welcome via Issues.

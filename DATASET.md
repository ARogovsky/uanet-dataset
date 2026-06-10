# Data Statement — UA Web Census 2026

A datasheet for the `ua-web-census-2026` dataset, following the structure of
*Datasheets for Datasets* (Gebru et al.). It documents what the data is, how
it was collected, what was removed before release, and how it should and
should not be used.

- **Name:** UA Web Census 2026
- **Version:** 1.0
- **Observation window:** 27–28 March 2026 (single snapshot)
- **Records:** 354,947 domains (one row each)
- **Format:** Apache Parquet (zstd), UTF-8
- **License:** data under CC BY 4.0; code under MIT
- **Canonical host:** Zenodo, DOI [10.5281/zenodo.20623589](https://doi.org/10.5281/zenodo.20623589)

---

## Motivation

Global internet-scan corpora (Censys, Rapid7 Sonar, Common Crawl) sample the
whole IPv4 space or a top-million list; bare zone-file products list `.ua`
names with little metadata. Neither provides **rich per-domain enrichment for
a single national namespace**. This dataset fills that gap for the Ukrainian
`.ua` ccTLD, enabling research into national email-security posture, TLS
hygiene, and the state of the Ukrainian web at a specific point in 2026.

## Composition

- **What each record represents.** One probed `.ua` domain. The seed was a
  list of ~500,000 registered second- and third-level `.ua` names; this
  release contains 354,947 of them.
- **Liveness.** ~49.4% (175,182) resolved and returned an HTTP response;
  ~50.6% (179,765) did not (parked, dead, firewalled or geo-blocked). Rows for
  non-responding domains are retained with **null** enrichment columns so the
  live/dead distribution is itself analyzable. This is why the dataset is
  described as a *census of probed domains*, **not** a list of live sites.
- **Fields.** 34 columns spanning HTTP, TLS/certificate, DNS (SPF/DMARC) and
  content-level signals. Full per-column documentation: [`schema/columns.md`](schema/columns.md).
- **Does it contain personal data?** No. The release contains only
  externally observable properties of public endpoints; no natural person is
  identifiable from it (see Preprocessing).
- **Sample vs. full.** This repository ships a 1,000-row random sample
  (`sample/ua_sample_1k.parquet`, seed 42). The full file is on Zenodo.

## Collection process

1. **Seed.** A list of ~500,000 registered `.ua` domains was assembled as the
   input set. The raw seed list is **not** published.
2. **Probe.** Each domain was probed with an **in-house Go-based scanner**
   that performs DNS resolution, an HTTP(S) request, a TLS handshake and
   certificate parse, SPF/DMARC TXT lookups and lightweight HTML content
   extraction in a single pass. The scanner is proprietary and is **not**
   included in this release.
3. **Record.** Results were written to a PostgreSQL table (`raw_domains`),
   one row per domain.
4. **Capture window.** All observations fall on 27–28 March 2026.

Only publicly reachable hosts were probed. No authentication was bypassed and
no private systems were accessed; all collected signals are externally
observable properties of public endpoints.

## Preprocessing / cleaning / sanitization

The public release is produced from the raw dump by
[`scripts/sanitize.py`](scripts/sanitize.py), which reads out **only** the 34
whitelisted columns (`schema/columns.md`) and discards everything else. In
particular it:

- **Excludes all personal data.** Any personal data present in the raw scan
  table is dropped entirely (not hashed), so it cannot be recovered by joining
  against domain + timestamp.
- **Excludes internal/operational fields:** pipeline run and worker
  identifiers and processing-status fields, which describe internal tooling
  rather than properties of the surveyed web.
- **Excludes database bookkeeping** timestamps and `cert_serial_number`.
- **Coarsens time:** the raw millisecond observation timestamp →
  `observed_day` (UTC date), reducing re-identification precision.
- **Keeps** `spf_record` and `dmarc_record` per-domain — these are public DNS
  records any party can query.

## Uses

- **Recommended:** measuring SPF/DMARC adoption across a ccTLD; TLS/cipher
  and certificate-issuer analysis; web-ecosystem and accessibility snapshots;
  a 2026 longitudinal baseline for the Ukrainian web; ML features for
  domain/infrastructure research.
- **Out of scope / prohibited:** targeting, attacking, scanning-for-exploit,
  or harassing any host or operator listed; re-identifying individuals; any
  use that treats the data as an attack-target list. Certificate-anomaly
  flags are released because self-signed/mismatched cases are effectively
  absent in this snapshot (1 and 3 respectively) and carry no meaningful
  targeting value.

## Distribution

- **Zenodo** (canonical, versioned, DOI):
  [10.5281/zenodo.20623589](https://doi.org/10.5281/zenodo.20623589).
- **Hugging Face Datasets** — mirror at
  <https://huggingface.co/datasets/ARogovsky/uanet-dataset>
  (`load_dataset("ARogovsky/uanet-dataset")`).
- This **GitHub repo** carries methodology, schema, sanitization code and the
  1k sample only — not the bulk data.

## Maintenance

Maintained by Andrii Rogovskyi ([@ARogovsky](https://github.com/ARogovsky)).
Corrections and questions via repository Issues. Versioning follows Zenodo
records; any future snapshot will be published as a new version with its own
observation window.

## Known limitations

- Single point-in-time snapshot; configurations change.
- Coverage is the probed seed, of which only the *responding* half carries
  enrichment; non-responding hosts are present but sparse.
- Scanner-derived heuristics (mobile-friendliness, content extraction) carry
  the usual false-positive/negative characteristics of automated probing.
- `.ua` second-level registration requires a matching trademark, so the
  namespace skews toward third-level zones (`com.ua`, regional, etc.).

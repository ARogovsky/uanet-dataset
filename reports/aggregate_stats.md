# UA Web Census 2026 — Zone-Level Aggregate Statistics

All figures are computed from the public release
(`ua-web-census-2026.parquet`, 354,947 rows) with `scripts/sanitize.py`
applied. Percentages labelled *"of responders"* use the **175,182** domains
that returned an HTTP response as the denominator; percentages labelled
*"of zone"* use the full **354,947** probed domains.

> Observation window: **27–28 March 2026** (single snapshot).

## 1. Liveness of the probed set

| Metric | Count | Share of zone |
|---|---:|---:|
| Domains probed (seed-derived) | 354,947 | 100.0% |
| Resolved + responded over HTTP(S) | 175,182 | 49.4% |
| No response (parked, dead, firewalled, geo-blocked) | 179,765 | 50.6% |

Roughly **half** of the probed `.ua` names did not return a usable HTTP
response. The non-responding half is retained in the dataset (enrichment
columns are null) so the live/dead ratio itself is analyzable.

## 2. Email authentication posture (the headline finding)

Among the 175,182 responders:

| Record | Present | Of responders |
|---|---:|---:|
| SPF (`v=spf1 ...`) | 102,852 | 58.7% |
| DMARC (`v=DMARC1 ...`) | 26,909 | 15.4% |

**~84.6% of live `.ua` web hosts publish no DMARC record.** SPF adoption is
moderate; DMARC adoption is low, leaving most domains without a published
policy against spoofing of their name.

### Government subzone (`*.gov.ua`)

| Metric | `gov.ua` | Whole zone |
|---|---:|---:|
| Responders | 2,016 (of 3,889) | 175,182 |
| SPF of responders | 84.9% | 58.7% |
| DMARC of responders | 57.4% | 15.4% |

Government domains are markedly better configured than the zone average —
DMARC adoption is ~3.7× higher — though ~43% of responding `gov.ua` hosts
still lack DMARC.

## 3. TLS hygiene

Among responders, **97.1%** (170,105) completed a TLS handshake.

| TLS version | Count |
|---|---:|
| TLS 1.3 | 153,065 |
| TLS 1.2 | 17,040 |
| < TLS 1.2 | 0 |

No host negotiated a protocol below TLS 1.2 — a healthy result.

| Key algorithm | Count |
|---|---:|
| RSA | 123,479 |
| ECDSA | 46,626 |

Top cipher suites: `TLS13_AES_256_GCM_SHA384` (147,435),
`TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384` (7,050),
`TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256` (5,117),
`TLS13_AES_128_GCM_SHA256` (5,055).

### Certificate anomalies

| Flag | Count | Of TLS hosts |
|---|---:|---:|
| Self-signed | 1 | ~0.0% |
| Hostname mismatch | 3 | ~0.0% |
| Wildcard certificate | 42,971 | 25.3% |

Self-signed and mismatched certificates are effectively absent — the live
`.ua` web is overwhelmingly served behind valid, CA-issued certificates.

### Certificate issuers (top)

| Issuer | Certificates |
|---|---:|
| Let's Encrypt (R12) | 51,042 |
| Let's Encrypt (R13) | 50,752 |
| Google Trust Services (WE1) | 31,469 |
| ZeroSSL (RSA Domain Secure Site CA) | 15,048 |
| Let's Encrypt (E7) | 7,440 |
| Let's Encrypt (E8) | 7,409 |
| Sectigo (Server Auth CA DV R36) | 2,691 |

Let's Encrypt issues the majority of live `.ua` certificates
(R12+R13+E7+E8 ≈ 116,600), followed by Google Trust Services and ZeroSSL.
Free, automated DV CAs dominate the zone.

## 4. HTTP layer

| HTTP version | Count |
|---|---:|
| HTTP/2 | 154,877 |
| HTTP/1.1 | 20,299 |
| HTTP/1.0 | 6 |

| Status (top) | Count |
|---|---:|
| 200 | 166,597 |
| 403 | 5,462 |
| 404 | 1,903 |
| 301 | 234 |
| 401 | 225 |
| 423 | 204 |
| 456 | 189 |
| 402 | 140 |
| 302 | 129 |

Response time among responders: median **0.397 s**, p90 **1.546 s**.

Mobile-friendly (heuristic): **150,627 / 175,182 = 86.0%** of responders.

## 5. Namespace composition (top second-level zones)

| Zone | Domains |
|---|---:|
| com.ua | 195,946 |
| kiev.ua | 20,170 |
| in.ua | 19,837 |
| org.ua | 14,981 |
| at.ua | 12,128 |
| pp.ua | 10,829 |
| inf.ua | 8,011 |
| net.ua | 7,108 |
| dp.ua | 5,239 |
| od.ua | 4,070 |
| gov.ua | 3,890 |
| ucoz.ua | 3,437 |
| lviv.ua | 2,998 |
| cc.ua | 2,413 |
| kh.ua | 2,297 |

`com.ua` accounts for the majority of the namespace, consistent with `.ua`
second-level registration requiring a matching trademark (which pushes most
registrants to third-level zones).

---

*Regenerate with:* `python scripts/sanitize.py <dump> --out build/ua-web-census-2026.parquet`
then re-run the aggregation over the resulting Parquet file.

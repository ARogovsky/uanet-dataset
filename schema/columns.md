# Schema — `ua-web-census-2026`

34 columns. One row per probed `.ua` domain (354,947 rows). Enrichment
columns are **null** for domains that did not resolve or respond
(~50.6% of rows).

| # | Column | Type | Nullable | Description |
|---|---|---|---|---|
| 1 | `domain` | string | no | The probed domain name (e.g. `example.com.ua`). Primary key; always present. |
| 2 | `initial_domain` | string | yes | Domain as first requested before any redirect. |
| 3 | `final_domain` | string | yes | Domain after following redirects. Differs from `domain` when the host redirects elsewhere. |
| 4 | `ip_address` | string | yes | Resolved IP address used for the connection. |
| 5 | `reverse_dns_name` | string | yes | PTR record for `ip_address`, when available. |
| 6 | `http_status` | int64 | yes | HTTP status code of the final response (e.g. 200, 403). Null = no HTTP response. |
| 7 | `http_status_text` | string | yes | Reason phrase for `http_status` (e.g. `OK`). |
| 8 | `response_time_seconds` | float64 | yes | Wall-clock time to complete the request, in seconds. |
| 9 | `title` | string | yes | Contents of the HTML `<title>` element. |
| 10 | `description` | string | yes | `<meta name="description">` content. |
| 11 | `keywords` | string | yes | `<meta name="keywords">` content. |
| 12 | `is_mobile_friendly` | bool | yes | Heuristic mobile-friendliness flag (e.g. responsive viewport). |
| 13 | `tls_version` | string | yes | Negotiated TLS version (e.g. `TLSv1.3`). Null = no TLS handshake. |
| 14 | `cipher_suite` | string | yes | Negotiated cipher suite. |
| 15 | `key_algorithm` | string | yes | Certificate public-key algorithm (`RSA`, `ECDSA`). |
| 16 | `ssl_cert_subject` | string | yes | Certificate Subject DN. |
| 17 | `ssl_cert_issuer` | string | yes | Certificate Issuer DN. |
| 18 | `ssl_cert_valid_from_ms` | int64 | yes | Certificate `notBefore`, Unix epoch milliseconds. |
| 19 | `ssl_cert_valid_to_ms` | int64 | yes | Certificate `notAfter`, Unix epoch milliseconds. |
| 20 | `spf_record` | string | yes | Published SPF TXT record (`v=spf1 ...`), if any. Public DNS data. |
| 21 | `dmarc_record` | string | yes | Published DMARC TXT record (`v=DMARC1 ...`), if any. Public DNS data. |
| 22 | `body_sha256` | string | yes | SHA-256 of the response body. Useful for deduplication / change detection. |
| 23 | `content_length` | int64 | yes | Response body length in bytes. |
| 24 | `http_version` | string | yes | Negotiated HTTP version (`HTTP/2`, `HTTP/1.1`). |
| 25 | `body_word_count` | int64 | yes | Word count of the rendered body text. |
| 26 | `body_line_count` | int64 | yes | Line count of the rendered body text. |
| 27 | `content_type` | string | yes | `Content-Type` response header. |
| 28 | `canonical_url` | string | yes | `<link rel="canonical">` URL, if present. |
| 29 | `cert_fingerprint_sha256` | string | yes | SHA-256 fingerprint of the leaf certificate. |
| 30 | `cert_is_self_signed` | bool | yes | Whether the certificate is self-signed. |
| 31 | `cert_is_wildcard` | bool | yes | Whether the certificate is a wildcard (`*.example.com.ua`). |
| 32 | `cert_is_mismatched` | bool | yes | Whether the certificate hostname does not match the domain. |
| 33 | `meta_refresh_url` | string | yes | Target of an HTML `<meta http-equiv="refresh">` redirect, if any. |
| 34 | `observed_day` | date32 | yes | UTC date of observation, **coarsened from a millisecond timestamp** to a day to limit re-identification precision. |

## Sanitization

The public release contains **only** the 34 columns above. The raw scan table
held additional fields that are **deliberately excluded** and never written to
the release (see `DATASET.md` §Preprocessing), namely:

- **Personal data of any kind** — removed entirely (not hashed), so it cannot
  be recovered.
- **Internal pipeline / operational state** — run identifiers, worker
  identifiers and processing-status fields.
- **Database bookkeeping timestamps** and the raw millisecond observation
  timestamp (replaced by the day-coarsened `observed_day`).
- **`cert_serial_number`** — unnecessary precision, not needed for analysis.

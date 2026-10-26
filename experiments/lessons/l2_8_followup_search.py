"""L2.8 follow-up: gọi API tìm paper và lưu nguyên raw response ngay sau mỗi call.

Người phụ trách: Doan Van Tai. AI (Claude) viết theo yêu cầu tác giả 26/10/2026.
Mục đích: khắc phục giới hạn của L2.8 Part2 (raw từng rank không được giữ) cho
các lượt tìm MỚI. Script không tái dựng hay ghi đè 169 screening events cũ.

Mỗi lần gọi `call`:
  1. ghi body HTTP đúng như nhận được vào raw/<call_id>__a<n>.<ext>;
  2. append một dòng JSON vào calls.jsonl (URL, giờ UTC, HTTP status, bytes,
     sha256, số record parse được, tổng provider báo nếu có);
  3. 429/5xx/timeout được thử lại có giới hạn, mỗi attempt là một dòng riêng.
`show` in record đã chuẩn hóa từ raw để sàng; quyết định sàng ghi riêng ở
screen/<call_id>.csv. Không gửi email/API key của tác giả tới dịch vụ nào.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import socket
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "results" / "lessons" / "l2_8" / "followup"
RAW = OUT / "raw"
LEDGER = OUT / "calls.jsonl"
UA = "state-model-regret-l2.8-followup/1.0 (research literature audit script)"
OPENALEX_SELECT = (
    "id,doi,title,publication_year,type,primary_location,"
    "abstract_inverted_index,cited_by_count,ids"
)
S2_FIELDS = "title,year,venue,externalIds,abstract,publicationTypes,citationCount"
ATOM = "{http://www.w3.org/2005/Atom}"
ARXIV_NS = "{http://arxiv.org/schemas/atom}"


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def build_url(provider: str, seed: str, limit: int, sort: str | None) -> tuple[str, str]:
    q = urllib.parse.urlencode
    if provider == "openalex_search":
        params = {"search": seed, "per-page": limit, "select": OPENALEX_SELECT}
        if sort:
            params["sort"] = sort
        return "https://api.openalex.org/works?" + q(params), "json"
    if provider == "openalex_cites":
        params = {"filter": f"cites:{seed}", "per-page": limit, "select": OPENALEX_SELECT}
        if sort:
            params["sort"] = sort
        return "https://api.openalex.org/works?" + q(params), "json"
    if provider == "openalex_ta":
        params = {"filter": f"title_and_abstract.search:{seed}", "per-page": limit,
                  "select": OPENALEX_SELECT, "sort": sort or "relevance_score:desc"}
        return "https://api.openalex.org/works?" + q(params), "json"
    if provider == "openalex_title":
        params = {"filter": f"title.search:{seed}", "per-page": limit, "select": OPENALEX_SELECT}
        return "https://api.openalex.org/works?" + q(params), "json"
    if provider == "s2_citations":
        pid = urllib.parse.quote(seed, safe=":")
        return (
            f"https://api.semanticscholar.org/graph/v1/paper/{pid}/citations?"
            + q({"fields": S2_FIELDS, "limit": limit}),
            "json",
        )
    if provider == "s2_search":
        return (
            "https://api.semanticscholar.org/graph/v1/paper/search?"
            + q({"query": seed, "limit": limit, "fields": S2_FIELDS}),
            "json",
        )
    if provider == "arxiv":
        return "https://export.arxiv.org/api/query?" + q({"id_list": seed, "max_results": limit}), "xml"
    if provider == "crossref_doi":
        return "https://api.crossref.org/works/" + urllib.parse.quote(seed, safe="/.()-_"), "json"
    if provider == "crossref_query":
        return (
            "https://api.crossref.org/works?"
            + q({"query.bibliographic": seed, "rows": limit,
                 "select": "DOI,title,author,container-title,issued,type,relation"}),
            "json",
        )
    raise SystemExit(f"unknown provider {provider}")


def openalex_abstract(inv: dict | None) -> str:
    if not inv:
        return ""
    pos: dict[int, str] = {}
    for word, idxs in inv.items():
        for i in idxs:
            pos[i] = word
    return " ".join(pos[i] for i in sorted(pos))


def parse_records(provider: str, body: bytes) -> tuple[list[dict], object]:
    """Trả về (records chuẩn hóa theo thứ tự rank, tổng provider báo hoặc None)."""
    if provider.startswith("openalex"):
        d = json.loads(body)
        recs = []
        for w in d.get("results", []):
            loc = (w.get("primary_location") or {}).get("source") or {}
            ids = w.get("ids") or {}
            recs.append({
                "id": w.get("id"), "doi": w.get("doi"), "title": w.get("title"),
                "year": w.get("publication_year"), "type": w.get("type"),
                "venue": loc.get("display_name"), "cited_by": w.get("cited_by_count"),
                "arxiv": next((v for k, v in ids.items() if "arxiv" in str(v).lower()), None),
                "abstract": openalex_abstract(w.get("abstract_inverted_index")),
            })
        return recs, d.get("meta", {}).get("count")
    if provider.startswith("s2_"):
        d = json.loads(body)
        rows = d.get("data", [])
        recs = []
        for r in rows:
            p = r.get("citingPaper", r)
            ext = p.get("externalIds") or {}
            recs.append({
                "id": p.get("paperId"), "doi": ext.get("DOI"), "arxiv": ext.get("ArXiv"),
                "title": p.get("title"), "year": p.get("year"), "venue": p.get("venue"),
                "type": ",".join(p.get("publicationTypes") or []),
                "cited_by": p.get("citationCount"), "abstract": p.get("abstract") or "",
            })
        return recs, d.get("total", d.get("next"))
    if provider == "arxiv":
        root = ET.fromstring(body)
        recs = []
        for e in root.findall(f"{ATOM}entry"):
            def t(tag: str, ns: str = ATOM) -> str:
                el = e.find(f"{ns}{tag}")
                return " ".join(el.text.split()) if el is not None and el.text else ""
            recs.append({
                "id": t("id"), "title": t("title"), "year": t("published")[:4],
                "published": t("published"), "updated": t("updated"),
                "authors": [" ".join((a.findtext(f"{ATOM}name") or "").split())
                            for a in e.findall(f"{ATOM}author")],
                "journal_ref": t("journal_ref", ARXIV_NS), "doi": t("doi", ARXIV_NS),
                "comment": t("comment", ARXIV_NS), "abstract": t("summary"),
                "venue": "arXiv", "type": "preprint",
            })
        return recs, len(recs)
    if provider.startswith("crossref"):
        d = json.loads(body)
        msg = d.get("message", {})
        items = msg.get("items", [msg] if "DOI" in msg else [])
        recs = []
        for it in items:
            issued = (it.get("issued") or {}).get("date-parts") or [[None]]
            recs.append({
                "id": it.get("DOI"), "doi": it.get("DOI"),
                "title": (it.get("title") or [""])[0],
                "venue": (it.get("container-title") or [""])[0],
                "year": issued[0][0], "type": it.get("type"),
                "authors": [" ".join(filter(None, [a.get("given"), a.get("family")]))
                            for a in it.get("author", [])],
                "published_online": (it.get("published-online") or {}).get("date-parts"),
                "abstract": it.get("abstract", ""),
            })
        return recs, msg.get("total-results", len(recs))
    raise SystemExit(provider)


def fetch(url: str, timeout: float) -> tuple[int | None, bytes, str]:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, r.read(), ""
    except urllib.error.HTTPError as e:
        return e.code, e.read(), f"HTTPError {e.code}"
    except (urllib.error.URLError, socket.timeout, TimeoutError) as e:
        return None, b"", f"{type(e).__name__}: {e}"


def cmd_call(a: argparse.Namespace) -> int:
    RAW.mkdir(parents=True, exist_ok=True)
    if any(p.name.startswith(a.call_id + "__") for p in RAW.iterdir()):
        raise SystemExit(f"{a.call_id} đã có raw; dùng call_id mới, không ghi đè lịch sử")
    url, ext = build_url(a.provider, a.seed, a.limit, a.sort)
    waits = [0] + [int(x) for x in a.backoff.split(",") if x]
    status = None
    for n, wait in enumerate(waits[: a.max_attempts], start=1):
        if wait:
            time.sleep(wait)
        start = utc_now()
        status, body, err = fetch(url, a.timeout)
        end = utc_now()
        raw_path = RAW / f"{a.call_id}__a{n}.{ext if status == 200 else 'txt'}"
        raw_path.write_bytes(body)
        rec: dict = {
            "call_id": a.call_id, "attempt": n, "region": a.region, "kind": a.kind,
            "pc": a.pc, "provider": a.provider, "seed": a.seed, "limit": a.limit,
            "sort": a.sort, "url": url, "utc_start": start, "utc_end": end,
            "http_status": status, "error": err, "bytes": len(body),
            "sha256": hashlib.sha256(body).hexdigest(),
            "raw_path": str(raw_path.relative_to(ROOT)), "note": a.note,
        }
        if status == 200:
            recs, total = parse_records(a.provider, body)
            rec.update({"n_records": len(recs), "provider_total": total})
        with LEDGER.open("a", encoding="utf-8") as f:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
        print(json.dumps({k: rec.get(k) for k in
                          ("call_id", "attempt", "http_status", "error", "n_records",
                           "provider_total", "bytes", "raw_path")}, ensure_ascii=False))
        if status == 200 or (status is not None and status not in (429, 500, 502, 503, 504)):
            break
    return 0 if status == 200 else 2


def cmd_show(a: argparse.Namespace) -> int:
    rows = [json.loads(x) for x in LEDGER.read_text(encoding="utf-8").splitlines()]
    ok = [r for r in rows if r["call_id"] == a.call_id and r["http_status"] == 200]
    if not ok:
        raise SystemExit("no successful attempt")
    r = ok[-1]
    body = (ROOT / r["raw_path"]).read_bytes()
    recs, total = parse_records(r["provider"], body)
    print(f"# {a.call_id} provider={r['provider']} total={total} n={len(recs)} sha256={r['sha256'][:12]}")
    for i, x in enumerate(recs, start=1):
        ab = (x.get("abstract") or "").replace("\n", " ")
        print(f"[{i}] {x.get('title')} | {x.get('year')} | {x.get('venue')} | {x.get('type')}")
        print(f"     id={x.get('id')} doi={x.get('doi')} arxiv={x.get('arxiv')} cited={x.get('cited_by')}")
        for k in ("journal_ref", "comment", "published", "updated", "published_online"):
            if x.get(k):
                print(f"     {k}={x.get(k)}")
        if x.get("authors"):
            print(f"     authors={'; '.join(x['authors'][:8])}")
        print(f"     abstract[{len(ab)}]={ab[: a.chars]}")
    return 0


def latest_ok(call_id: str) -> dict:
    rows = [json.loads(x) for x in LEDGER.read_text(encoding="utf-8").splitlines()]
    ok = [r for r in rows if r["call_id"] == call_id and r["http_status"] == 200]
    if not ok:
        raise SystemExit("no successful attempt")
    return ok[-1]


def cmd_screen(a: argparse.Namespace) -> int:
    """Ghép quyết định sàng (JSON theo rank) với ID lấy thẳng từ raw → CSV."""
    import csv

    r = latest_ok(a.call_id)
    recs, _ = parse_records(r["provider"], (ROOT / r["raw_path"]).read_bytes())
    dec = json.loads(Path(a.decisions).read_text(encoding="utf-8"))
    if sorted(int(k) for k in dec) != list(range(1, len(recs) + 1)):
        raise SystemExit(f"cần đúng {len(recs)} quyết định theo rank 1..{len(recs)}")
    out = OUT / "screen" / f"{a.call_id}.csv"
    if out.exists() and not a.replace:
        raise SystemExit(f"{out} đã có")
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(["call_id", "rank", "record_id", "doi", "arxiv", "year", "title",
                    "abstract_available", "decision", "tier", "reason", "raw_sha256"])
        for i, x in enumerate(recs, start=1):
            d = dec[str(i)]
            rid = str(x.get("id") or "").rsplit("/", 1)[-1] if r["provider"].startswith("openalex") else x.get("id")
            w.writerow([a.call_id, i, rid, (x.get("doi") or "").replace("https://doi.org/", ""),
                        (x.get("arxiv") or "").replace("https://doi.org/", ""), x.get("year"),
                        x.get("title"), "yes" if x.get("abstract") else "no",
                        d[0], d[1], d[2], r["sha256"]])
    print(f"wrote {out.relative_to(ROOT)} rows={len(recs)}")
    return 0


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("call")
    c.add_argument("--call-id", required=True)
    c.add_argument("--region", required=True)
    c.add_argument("--kind", required=True, choices=["keyword", "forward", "lookup"])
    c.add_argument("--pc", required=True)
    c.add_argument("--provider", required=True)
    c.add_argument("--seed", required=True)
    c.add_argument("--limit", type=int, default=20)
    c.add_argument("--sort", default=None)
    c.add_argument("--timeout", type=float, default=45)
    c.add_argument("--max-attempts", type=int, default=3)
    c.add_argument("--backoff", default="20,60")
    c.add_argument("--note", default="")
    s = sub.add_parser("show")
    s.add_argument("--call-id", required=True)
    s.add_argument("--chars", type=int, default=700)
    d = sub.add_parser("screen")
    d.add_argument("--call-id", required=True)
    d.add_argument("--decisions", required=True, help="JSON {rank: [decision, tier, reason]}")
    d.add_argument("--replace", action="store_true", help="chỉ dùng để sửa lỗi chép trước commit")
    a = p.parse_args(argv)
    return {"call": cmd_call, "show": cmd_show, "screen": cmd_screen}[a.cmd](a)


if __name__ == "__main__":
    sys.exit(main())

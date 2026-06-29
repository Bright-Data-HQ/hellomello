#!/usr/bin/env python3
"""
Competitor data audit — checks whether a competitor folder has enough and correct
data to build the deck described in INSTRUCTIONS.md.

Usage:
    cd competitors/<competitor-slug>
    python3 ../_template/code/audit.py

    # or explicitly:
    python3 competitors/_template/code/audit.py competitors/<competitor-slug>

Exit code is non-zero if any 🔴 BLOCKER fails.
"""
from __future__ import annotations
import csv, json, os, re, sys, glob
from datetime import datetime, timedelta

# ---------- terminal colours ----------
def _supports_colour() -> bool:
    return sys.stdout.isatty() and os.environ.get("NO_COLOR") is None

if _supports_colour():
    GREEN, YELLOW, RED, DIM, RESET, BOLD = "\033[32m", "\033[33m", "\033[31m", "\033[2m", "\033[0m", "\033[1m"
else:
    GREEN = YELLOW = RED = DIM = RESET = BOLD = ""

OK   = f"{GREEN}✓{RESET}"
WARN = f"{YELLOW}⚠{RESET}"
FAIL = f"{RED}✗{RESET}"

# ---------- thresholds (mirror DATA_AUDIT.md) ----------
MAX_EXPORT_AGE_DAYS = 45
MIN_KEYWORDS_SNAPSHOT = 200
MIN_KEYWORDS_FULL_DECK = 1000
MIN_PAGES = 25
MIN_BACKLINK_PAGES = 50
MAX_BRAND_SHARE = 0.85
WARN_BRAND_SHARE = 0.60
MAX_DATE_SPREAD_DAYS = 7

REQUIRED_COLS = {
    "positions": {"Keyword", "Position", "Search Volume", "Traffic", "URL"},
    "pages":     {"URL", "Traffic"},
    # backlinks_pages export carries the source side only; target is implicit (competitor domain)
    "backlinks": {"Source url"},
}
# tolerate common SEMrush column aliases
COL_ALIASES = {
    "URL": {"Url", "url"},
    "Traffic": {"Estimated Traffic", "Traffic (%)", "Organic Traffic"},
    "Search Volume": {"Volume"},
    "Source url": {"Source Url", "Source URL"},
    "Target url": {"Target Url", "Target URL"},
}

DATE_RE = re.compile(r"(\d{8})")

# ---------- audit state ----------
class Audit:
    def __init__(self, root: str):
        self.root = root
        self.slug = os.path.basename(root.rstrip("/"))
        self.data_dir = os.path.join(root, "data", "raw")
        self.blockers: list[tuple[str, bool, str]] = []
        self.volume:   list[tuple[str, str, str]]  = []  # symbol, msg, detail
        self.optional: list[tuple[str, str]]       = []
        self.qual:     list[tuple[str, str]]       = []
        self.notes:    list[str]                   = []

    def block(self, msg: str, ok: bool, detail: str = ""):
        self.blockers.append((msg, ok, detail))

    def vol(self, symbol: str, msg: str, detail: str = ""):
        self.volume.append((symbol, msg, detail))

    def opt(self, symbol: str, msg: str):
        self.optional.append((symbol, msg))

    def q(self, symbol: str, msg: str):
        self.qual.append((symbol, msg))

    def has_blocker_failure(self) -> bool:
        return any(not ok for _, ok, _ in self.blockers)


# ---------- helpers ----------
def find(data_dir: str, suffix_glob: str) -> list[str]:
    return sorted(glob.glob(os.path.join(data_dir, suffix_glob)))


def parse_date_from_name(path: str) -> datetime | None:
    m = DATE_RE.search(os.path.basename(path))
    if not m:
        return None
    try:
        return datetime.strptime(m.group(1), "%Y%m%d")
    except ValueError:
        return None


def normalise_cols(header: list[str]) -> set[str]:
    out: set[str] = set()
    for col in header:
        col = col.strip()
        out.add(col)
        for canonical, aliases in COL_ALIASES.items():
            if col in aliases:
                out.add(canonical)
    return out


def sniff_csv(path: str, max_rows: int = 50000) -> tuple[list[str], list[dict]]:
    """Returns (header, rows)."""
    with open(path, newline="", encoding="utf-8", errors="replace") as f:
        reader = csv.DictReader(f)
        header = reader.fieldnames or []
        rows: list[dict] = []
        for i, row in enumerate(reader):
            if i >= max_rows:
                break
            rows.append(row)
        return header, rows


def col_value(row: dict, *candidates: str) -> str:
    for c in candidates:
        if c in row and row[c] not in (None, ""):
            return row[c]
    return ""


# ---------- checks ----------
def check_identity_and_freshness(a: Audit):
    pos = find(a.data_dir, "*organic.Positions*.csv")
    pages = find(a.data_dir, "*organic.Pages*.csv")
    bl = find(a.data_dir, "*backlinks_pages*.csv")

    a.block("Positions CSV present", bool(pos),
            "expected *organic.Positions*.csv in data/raw/")
    a.block("Pages CSV present", bool(pages),
            "expected *organic.PagesV3*.csv in data/raw/")
    a.block("Backlinks CSV present", bool(bl),
            "expected *backlinks_pages*.csv in data/raw/")

    if not (pos and pages and bl):
        return None

    # database = au (filename contains -au- or column "Database"=au)
    au_in_name = all("-au-" in os.path.basename(p).lower() for p in (pos[0], pages[0]))
    a.block("Database is AU", au_in_name,
            "filename should contain -au- (e.g. ...-au-20260528-...)")

    # freshness
    dates = [d for d in (parse_date_from_name(pos[0]),
                         parse_date_from_name(pages[0]),
                         parse_date_from_name(bl[0])) if d]
    if dates:
        newest = max(dates)
        age = (datetime.now() - newest).days
        a.block(f"Export age ≤ {MAX_EXPORT_AGE_DAYS} days",
                age <= MAX_EXPORT_AGE_DAYS,
                f"newest export is {age} days old ({newest.date()})")
        spread = (max(dates) - min(dates)).days
        a.block(f"All exports within {MAX_DATE_SPREAD_DAYS} days of each other",
                spread <= MAX_DATE_SPREAD_DAYS,
                f"spread = {spread} days")
    else:
        a.notes.append("Could not parse export date from filenames — skipping freshness check.")

    # size sanity
    for p in (pos[0], pages[0], bl[0]):
        size = os.path.getsize(p)
        a.block(f"Not truncated: {os.path.basename(p)}", size > 5_000,
                f"size = {size} bytes")

    return {"positions": pos[0], "pages": pages[0], "backlinks": bl[0]}


def check_schema(a: Audit, files: dict):
    for kind, path in files.items():
        header, _ = sniff_csv(path, max_rows=1)
        cols = normalise_cols(header)
        required = REQUIRED_COLS[kind]
        missing = required - cols
        a.block(f"Schema OK: {kind}", not missing,
                f"missing columns: {sorted(missing)}" if missing else "")


def check_volume(a: Audit, files: dict, expected_brand_re: str | None):
    _, pos_rows = sniff_csv(files["positions"])
    _, page_rows = sniff_csv(files["pages"])
    _, bl_rows = sniff_csv(files["backlinks"])

    kw_count = len(pos_rows)
    page_count = len(page_rows)
    bl_count = len(bl_rows)

    # keyword volume
    if kw_count >= MIN_KEYWORDS_FULL_DECK:
        a.vol(OK, f"{kw_count:,} ranking keywords", "healthy")
    elif kw_count >= MIN_KEYWORDS_SNAPSHOT:
        a.vol(WARN, f"{kw_count:,} ranking keywords",
              "thin — flag on slide 02; consider snapshot only")
    else:
        a.vol(FAIL, f"{kw_count:,} ranking keywords",
              f"< {MIN_KEYWORDS_SNAPSHOT} — produce one-page snapshot, not full deck")

    # pages
    if page_count >= MIN_PAGES:
        a.vol(OK, f"{page_count:,} pages with traffic")
    else:
        a.vol(FAIL, f"{page_count:,} pages with traffic",
              f"< {MIN_PAGES}")

    # backlinks
    if bl_count >= MIN_BACKLINK_PAGES:
        a.vol(OK, f"{bl_count:,} indexed backlink pages")
    else:
        a.vol(WARN, f"{bl_count:,} indexed backlink pages",
              f"< {MIN_BACKLINK_PAGES} — slide 15 will be thin")

    # subdomains
    hosts = set()
    for r in page_rows:
        url = col_value(r, "URL", "Url", "url")
        m = re.match(r"https?://([^/]+)/", url + "/")
        if m:
            hosts.add(m.group(1))
    a.vol(OK if len(hosts) >= 1 else FAIL,
          f"{len(hosts)} distinct host(s) in pages")

    # brand share
    if expected_brand_re:
        brand_re = re.compile(expected_brand_re, re.I)
        brand_kw = sum(1 for r in pos_rows
                       if brand_re.search(col_value(r, "Keyword")))
        share = brand_kw / max(kw_count, 1)
        share_pct = f"{share*100:.0f}%"
        if share > MAX_BRAND_SHARE:
            a.vol(FAIL, f"Brand share {share_pct}",
                  "> 85% — non-brand insights will be noise")
        elif share > WARN_BRAND_SHARE:
            a.vol(WARN, f"Brand share {share_pct}",
                  "> 60% — flag on slide 02")
        else:
            a.vol(OK, f"Brand share {share_pct}")
    else:
        a.vol(WARN, "Brand regex not supplied",
              "pass --brand 'regex' to check brand share")

    # sanity: any #1 rankings?
    any_p1 = any(col_value(r, "Position").strip() in ("1", "1.0")
                 for r in pos_rows[:5000])
    a.vol(OK if any_p1 else FAIL,
          "At least one #1 ranking" if any_p1 else "No #1 rankings found",
          "" if any_p1 else "likely broken export")

    # sanity: traffic > 0
    total_traffic = 0.0
    for r in pos_rows:
        try:
            total_traffic += float(col_value(r, "Traffic", "Estimated Traffic") or 0)
        except ValueError:
            pass
    a.vol(OK if total_traffic > 0 else FAIL,
          f"Total estimated traffic {total_traffic:,.0f}")


def check_optional(a: Audit):
    optional = [
        ("trends",        "*trends*.csv",               "slide 05 Trajectory"),
        ("serp-features", "*serp-features*.csv",        "slide 06 SERP features"),
        ("sov",           "*sov*.csv",                  "slide 08 Share of voice"),
        ("new-lost",      "*backlinks*new*lost*.csv",   "slide 16 Backlink velocity"),
        ("lighthouse",    "*lighthouse*.json",          "slide 17 E-E-A-T"),
    ]
    for name, pattern, unlocks in optional:
        present = bool(find(a.data_dir, pattern))
        if present:
            a.opt(OK, f"{name}.csv present → {unlocks}")
        else:
            a.opt(FAIL, f"{name} missing → {unlocks} will auto-hide")


def check_qualitative(a: Audit):
    notes_path = os.path.join(a.root, "data", "notes.json")
    if not os.path.exists(notes_path):
        a.q(WARN, "notes.json missing — slides 3/17/18/19/20 will be sparse")
        return
    try:
        with open(notes_path, encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        a.q(FAIL, f"notes.json invalid JSON: {e}")
        return

    required = [
        ("brand.visual_system",     ["brand", "visual_system"]),
        ("brand.site_architecture", ["brand", "site_architecture"]),
        ("brand.tone_compliance",   ["brand", "tone_compliance"]),
        ("position",                ["position"]),
    ]
    for label, path in required:
        cur = data
        ok = True
        for k in path:
            if not isinstance(cur, dict) or k not in cur or cur[k] in (None, "", []):
                ok = False
                break
            cur = cur[k]
        a.q(OK if ok else WARN, f"notes.{label}")

    pos = data.get("position")
    if pos and pos not in ("model", "careful", "watch"):
        a.q(WARN, f"notes.position = {pos!r} (expected model|careful|watch)")


# ---------- report ----------
def print_report(a: Audit):
    print(f"\n{BOLD}COMPETITOR AUDIT — {a.slug}{RESET}")
    print("─" * 60)

    print(f"\n{BOLD}[BLOCKERS]{RESET}")
    for msg, ok, detail in a.blockers:
        sym = OK if ok else FAIL
        line = f"  {sym} {msg}"
        if detail and not ok:
            line += f"  {DIM}({detail}){RESET}"
        print(line)

    if a.volume:
        print(f"\n{BOLD}[VOLUME]{RESET}")
        for sym, msg, detail in a.volume:
            line = f"  {sym} {msg}"
            if detail:
                line += f"  {DIM}({detail}){RESET}"
            print(line)

    if a.optional:
        print(f"\n{BOLD}[OPTIONAL]{RESET}")
        for sym, msg in a.optional:
            print(f"  {sym} {msg}")

    if a.qual:
        print(f"\n{BOLD}[QUALITATIVE]{RESET}")
        for sym, msg in a.qual:
            print(f"  {sym} {msg}")

    if a.notes:
        print(f"\n{BOLD}[NOTES]{RESET}")
        for n in a.notes:
            print(f"  · {n}")

    # verdict
    print()
    if a.has_blocker_failure():
        verdict = f"{RED}{BOLD}VERDICT: DO NOT BUILD{RESET} — fix blockers above and re-run."
    else:
        warn_count = sum(1 for sym, _, _ in a.volume if sym == WARN) + \
                     sum(1 for sym, _ in a.qual if sym == WARN)
        if warn_count:
            verdict = f"{YELLOW}{BOLD}VERDICT: BUILD with {warn_count} caveat(s){RESET}"
        else:
            verdict = f"{GREEN}{BOLD}VERDICT: BUILD{RESET} — all checks green."
    print(verdict)
    print()


def main(argv: list[str]) -> int:
    root = os.getcwd()
    brand = None
    args = argv[1:]
    while args:
        a = args.pop(0)
        if a == "--brand":
            brand = args.pop(0)
        elif a.startswith("--brand="):
            brand = a.split("=", 1)[1]
        elif a.startswith("-"):
            print(f"Unknown option: {a}", file=sys.stderr)
            return 2
        else:
            root = os.path.abspath(a)

    if not os.path.isdir(os.path.join(root, "data", "raw")):
        print(f"{FAIL} No data/raw/ folder at {root}", file=sys.stderr)
        return 2

    # infer brand regex from folder slug if not given
    if not brand:
        slug = os.path.basename(root.rstrip("/")).lower()
        brand = re.escape(slug)

    audit = Audit(root)
    files = check_identity_and_freshness(audit)
    if files:
        # only run schema/volume if all 3 required files exist
        if all(not (msg.startswith("Positions") or msg.startswith("Pages") or msg.startswith("Backlinks"))
               or ok for msg, ok, _ in audit.blockers):
            check_schema(audit, files)
            try:
                check_volume(audit, files, brand)
            except Exception as e:
                audit.vol(FAIL, f"Volume check crashed: {e}")
    check_optional(audit)
    check_qualitative(audit)

    print_report(audit)
    return 1 if audit.has_blocker_failure() else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))

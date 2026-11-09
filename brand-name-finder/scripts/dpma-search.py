#!/usr/bin/env python3
"""dpma-search.py: trademark lookup in DPMAregister (German, EU and international marks).

Usage:
  dpma-search.py telvik ovanda        exact word
  dpma-search.py -n telvik            near misses: every letter replaced by '?'.
                                      Only hits
                                      whose mark text is within Levenshtein 1 of
                                      the name (after sound normalisation v/w,
                                      c/k, ph/f, y/i) are printed.
  dpma-search.py -n --all telvik      near-miss search without the filter
  dpma-search.py -n --classes telvik  add Nice classes for live hits (DE/EM/IR)

Output (TSV): name  query  register  number  status  mark-text  [classes]
  plus a summary line per name:  name  HITS  n  (n live)
Dead = gelöscht, vernichtet, zurückgewiesen, zurückgenommen, erloschen,
abgelaufen, "Kein Schutz", "Marke nicht eingetragen(/Schutz nicht möglich)". A live hit in classes 9/35/38/42 kills a name.
"classes?" = classes could not be read: look them up before trusting the name.

Uses the public SmartSearch JSON endpoint (no login, no captcha); the Basis
form needs JavaScript and can't be scripted. The search covers mark text,
file number and owner. Calibrated 2026-11: zendesk -> 14, swarovski -> 367,
xqzvupt -> 0. Fresh filings appear only after a few weeks: re-check before
buying. Wildcards: '?' (one letter) is reliable (swarovsk? -> 371). '*' is
NOT: it works only with very short stems and silently undercounts
(swarov* -> 0, *rovski -> 0, zende* -> 0, though the marks exist; long
stems give "Ungültige Platzhalterverwendung"). So -n uses '?' only.
Rough ending-density probe: dpma-search.py --all '*alde' (4-letter
endings return hits, e.g. *desk -> 352); treat it as a lower bound.
Detail pages work only inside a search session (EM via the relative link
registerHABM?AKZ= from the result list, DE via marke/register/<nr>/DE);
opened directly they redirect. --classes avoids that.
Retries timeouts/HTTP errors with backoff (5/15/45 s); ERROR only after the
last try. A name with an ERROR line is unresolved, not safe; its summary
line then says "(UNRESOLVED: k variant errors)" instead of "(n live)". Batches of <= 20
names per call.
"""
import sys, re, html, time, json, urllib.request, urllib.parse, http.cookiejar, functools

print = functools.partial(print, flush=True)  # unbuffered output for background runs

ROOT = "https://register.dpma.de"
UA = {"User-Agent": "Mozilla/5.0 (brand-name-finder)"}
DEAD = re.compile(r"gelöscht|vernichtet|zurückgewiesen|zurückgenommen|erloschen|abgelaufen|kein schutz|nicht eingetragen|schutz nicht möglich", re.I)


def opener():
    op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))
    return lambda u, h=UA: op.open(urllib.request.Request(u, headers=h), timeout=60).read().decode("utf-8", "ignore")


def search(q):
    """With retries: DPMA times out after ~25 names in a row."""
    for wait in (5, 15, 45, None):
        try:
            return _search(q)
        except Exception:
            if wait is None:
                raise
            time.sleep(wait)


def _search(q):
    get = opener()
    meta = json.loads(get(f"{ROOT}/DPMAregister/smartsearch?queryString={urllib.parse.quote(q)}"))
    if meta.get("marErrors"):
        raise RuntimeError(meta["marErrors"])
    if int(meta.get("marHits") or 0) == 0:
        return []
    page = get(ROOT + meta["marLink"])
    rows = []
    for tr in re.findall(r"<tr><td[^>]*data-th=\"Nr\.\".*?</tr>", page, re.S):
        cell = lambda k: html.unescape(re.sub(r"<[^>]+>|\s+", " ", (re.search(
            rf'data-th="{k}"[^>]*>(.*?)</td>', tr, re.S) or [None, ""])[1])).strip()
        alt = re.search(r'alt="Darstellung der Marke \S+ \((.*?)\)"', tr)
        rows.append((cell("Datenbestand"), cell("Aktenzeichen/Registernummer"),
                     cell("Aktenzustand"), html.unescape(alt.group(1)) if alt else ""))
    return rows


def classes(nr):
    """Nice classes via the result-list filter facet (works for DE, EM and IR;
    the EM/IR detail pages redirect to 'Session abgelaufen')."""
    try:
        get = opener()
        meta = json.loads(get(f"{ROOT}/DPMAregister/smartsearch?queryString={urllib.parse.quote(nr)}"))
        get(ROOT + meta["marLink"])
        s = get(ROOT + "/DPMAregister/marke/trefferliste.trefferlistefilterkonfig."
                "trefferlistenfilterauswahl_2.refreshfilterauswahl",
                {**UA, "X-Requested-With": "XMLHttpRequest"})
        k = sorted(set(re.findall(r"Klasse (\d\d)", s)))
        return ",".join(k) if k else "classes?"
    except Exception:
        return "classes?"


def norm(s):
    s = s.lower().replace("ph", "f")
    return s.translate(str.maketrans("wcyäöüß", "vkiaous"))


def lev(a, b):
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        cur = [i]
        for j, cb in enumerate(b, 1):
            cur.append(min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (ca != cb)))
        prev = cur
    return prev[-1]


def near_hit(name, text):
    n = norm(name)
    words = [norm(w) for w in re.findall(r"[^\W\d_]+", text)]
    cands = words + ["".join(words)]
    return any(lev(n, w) <= 1 for w in cands if w)


def variants(n):
    return [n] + [n[:i] + "?" + n[i + 1:] for i in range(len(n))]


if __name__ == "__main__":
    args = sys.argv[1:]
    near, show_all, want_cls = "-n" in args, "--all" in args, "--classes" in args
    for name in [a for a in args if not a.startswith("-")]:
        seen, live, errors = {}, 0, 0
        for q in (variants(name.lower()) if near else [name]):
            try:
                for r in search(q):
                    seen.setdefault(r[1], (q,) + r)
            except Exception as e:
                print(f"{name}\tERROR\t{q}\t{e}")
                errors += 1
            time.sleep(0.5)
        hits = [h for h in seen.values()
                if not near or show_all or near_hit(name, h[4])]
        for q, reg, nr, st, txt in hits:
            alive = not DEAD.search(st)
            extra = [classes(nr)] if want_cls and alive else ([""] if want_cls else [])
            print(name, q, reg, nr, st, txt, *extra, sep="\t")
            live += alive
        status = f"UNRESOLVED: {errors} variant errors" if errors else f"{live} live"
        print(f"{name}\tHITS\t{len(hits)}\t({status})")

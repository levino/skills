#!/usr/bin/env python3
"""dpma-search.py: trademark lookup in DPMAregister (German, EU and international marks).

Usage:
  dpma-search.py telvik ovanda           exact word
  dpma-search.py -n telvik               also near misses: every letter replaced
                                          by '?' (telv?k, tel?ik ...) and name*
Output (TSV): query  register  number  status  mark-text
  plus a summary line per query:  query  HITS  n  (n live)
Live = not "gelöscht", "vernichtet", "zurückgewiesen" or "zurückgenommen".

Uses the public DPMAregister SmartSearch (no login, no captcha). The search
covers mark text, file number and owner. Calibrated 2026-11: zendesk -> 14,
swarovski -> 367, xqzvupt -> 0. Brand-new filings show up only after the DPMA
has processed them (a few weeks), so re-check before buying.
For class details open https://register.dpma.de/DPMAregister/marke/register/<nr>/<DE|EM|IR>.
"""
import sys, re, html, time, json, urllib.request, urllib.parse, http.cookiejar

ROOT = "https://register.dpma.de"
UA = {"User-Agent": "Mozilla/5.0 (brand-name-finder)"}
DEAD = re.compile(r"gelöscht|vernichtet|zurückgewiesen|zurückgenommen|erloschen|abgelaufen", re.I)


def search(q):
    op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))
    get = lambda u: op.open(urllib.request.Request(u, headers=UA), timeout=60).read().decode("utf-8", "ignore")
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


def variants(n):
    return [n] + [n[:i] + "?" + n[i + 1:] for i in range(len(n))] + [n + "*"]


if __name__ == "__main__":
    args = sys.argv[1:]
    near = "-n" in args
    for name in [a for a in args if a != "-n"]:
        seen, live = {}, 0
        for q in (variants(name.lower()) if near else [name]):
            try:
                for r in search(q):
                    seen.setdefault(r[1], (q,) + r)
            except Exception as e:
                print(f"{name}\tERROR\t{q}\t{e}")
            time.sleep(0.5)
        for q, reg, nr, st, txt in seen.values():
            print(name, q, reg, nr, st, txt, sep="\t")
            live += not DEAD.search(st)
        print(f"{name}\tHITS\t{len(seen)}\t({live} live)")

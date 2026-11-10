#!/usr/bin/env python3
"""dns-bulk.py: fast bulk prefilter of one TLD via DNS over HTTPS.

Usage: generate.py ... | dns-bulk.py de > de.tsv      (names on stdin, one per line)
Output (TSV): name  free|taken|unknown
  free    = NXDOMAIN (Status 3): no NS records. Means "likely free" (a domain can be
            registered without nameservers): confirm finalists with check-domains.sh (RDAP).
  taken   = the name resolves (Status 0).
  unknown = lookup failed 3 times or another DNS status: never treat as free.
24 threads against Cloudflare DoH: tens of thousands of names in minutes, no RDAP
rate limits. Run it per TLD (de, com, ai) and intersect the free lists.
Calibrate first: printf 'google\\nxqzvkwplm\\n' | dns-bulk.py ai  -> taken / free.
"""
import sys, json, urllib.request, concurrent.futures as cf

THREADS = 24


def lookup(domain):
    for _ in range(3):
        try:
            req = urllib.request.Request(
                f"https://cloudflare-dns.com/dns-query?name={domain}&type=NS",
                headers={"accept": "application/dns-json"})
            status = json.load(urllib.request.urlopen(req, timeout=10)).get("Status")
            return domain, {3: "free", 0: "taken"}.get(status, "unknown")
        except Exception:
            pass
    return domain, "unknown"


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit("usage: dns-bulk.py <tld>  < names.txt")
    tld = sys.argv[1].lstrip(".")
    names = [l.strip().lower() for l in sys.stdin if l.strip()]
    with cf.ThreadPoolExecutor(THREADS) as ex:
        for domain, status in ex.map(lookup, [f"{n}.{tld}" for n in names]):
            print(domain.rsplit(".", 1)[0], status, sep="\t", flush=True)

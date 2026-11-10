#!/usr/bin/env python3
"""desirability.py: rank FREE names of a full pattern space by how coveted the sound is.

Usage: desirability.py space.tsv [--brands references/brands.txt] [--top 200] [--min-coverage 0.8]
Input: TSV `name<TAB>free|taken[|unknown]` for a COMPLETE pattern space (dns-bulk.py output
       of generate.py --no-caps, same TLD, all names of one length/pattern).
Score = z(neighbour density) + z(brand-likeness):
  density = share of one-letter neighbours (same position class: vowel<->vowel,
            consonant<->consonant, using the letters seen at that position) whose
            domain is taken. High = the surrounding sound region is coveted.
  brand-likeness = mean letter-bigram log-likelihood under a model trained on
            the famous coined brands in brands.txt.
Output: score, density, bigram, name (best first). Free here is DNS-free: confirm with RDAP.
"""
import sys, math, argparse, collections, statistics, os

V = set("aeiou")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("tsv")
    ap.add_argument("--brands", default=os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "references", "brands.txt"))
    ap.add_argument("--top", type=int, default=200)
    ap.add_argument("--min-coverage", type=float, default=0.8, help="min share of neighbours with known status")
    a = ap.parse_args()

    st = {}
    for l in open(a.tsv):
        p = l.split()
        if len(p) >= 2:
            st[p[0].lower().split(".")[0]] = p[1]
    seen = collections.defaultdict(set)  # (length, pos) -> letters
    for n in st:
        for i, ch in enumerate(n):
            seen[len(n), i].add(ch)

    big, uni = collections.Counter(), collections.Counter()
    for l in open(a.brands):
        n = "".join(c for c in l.strip().lower() if c.isalpha())
        if not n:
            continue
        s = "^" + n + "$"
        for x, y in zip(s, s[1:]):
            big[x, y] += 1
            uni[x] += 1

    def lm(n):
        s = "^" + n + "$"
        return sum(math.log((big[x, y] + .5) / (uni[x] + .5 * 28)) for x, y in zip(s, s[1:])) / (len(s) - 1)

    rows = []
    for n, s in st.items():
        if s != "free":
            continue
        nb = [n[:i] + c + n[i + 1:] for i, ch in enumerate(n)
              for c in seen[len(n), i] if c != ch and (c in V) == (ch in V)]
        k = [st[x] for x in nb if st.get(x) in ("free", "taken")]
        if not nb or len(k) < len(nb) * a.min_coverage:
            continue
        rows.append((n, k.count("taken") / len(k), lm(n)))
    if len(rows) < 2:
        sys.exit("too few scorable free names (need a complete space with taken+free)")
    z = lambda i: (statistics.mean(r[i] for r in rows), statistics.pstdev(r[i] for r in rows) or 1)
    (md, sd), (mb, sb) = z(1), z(2)
    out = sorted(((((d - md) / sd) + ((b - mb) / sb), d, b, n) for n, d, b in rows), reverse=True)
    for sc, d, b, n in out[:a.top]:
        print(f"{sc:.2f}\t{d:.2f}\t{b:.2f}\t{n}")


if __name__ == "__main__":
    main()

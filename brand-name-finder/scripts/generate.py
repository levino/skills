#!/usr/bin/env python3
"""generate.py: enumerate a name pattern exhaustively, with variety caps.

Use it once the user's liked pattern is known (step 3), instead of letting agents
invent names by hand. Name = onset + vowel + middle + ending.

Example (two syllables, 5–7 letters):
  generate.py --onsets "bl br dr fl kl pl pr sl tr zw" --vowels "a e i o u ei au" \\
              --middles "lk lp rd lf nv lv mv" --endings "a e i o" \\
              --seen tried.txt --exclude 'ov[aeiou]$|[ai]no$' > cands.txt
Then: cands.txt | dns-bulk.py de / com / ai, keep names free on all three.

Variety caps (applied in a shuffled order so no onset is favoured):
  --max-onset N        names per onset              (default 40)
  --max-middle N       names per middle cluster     (default 60)
  --max-onset-middle N names per onset+middle       (default 4)
  --max-ove N          names per onset+vowel+ending (default 3)
Use 0 to disable a cap. Run the caps AFTER the DNS prefilter for the best
yield: generate.py --no-caps … | dns-bulk.py … ; then generate.py --cap-only < free.txt
"""
import argparse, random, re, sys
from collections import Counter


def split(name, onsets, vowels, middles, endings):
    """Recover (onset, vowel, middle, ending) for cap counting."""
    for o in sorted(onsets, key=len, reverse=True):
        if not name.startswith(o):
            continue
        rest = name[len(o):]
        for v in sorted(vowels, key=len, reverse=True):
            if not rest.startswith(v):
                continue
            r2 = rest[len(v):]
            for e in sorted(endings, key=len, reverse=True):
                if r2.endswith(e) and r2[:len(r2) - len(e)] in middles:
                    return o, v, r2[:len(r2) - len(e)], e
    return None


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--onsets", required=True)
    ap.add_argument("--vowels", default="a e i o u")
    ap.add_argument("--middles", required=True)
    ap.add_argument("--endings", default="a e i o")
    ap.add_argument("--min-len", type=int, default=5)
    ap.add_argument("--max-len", type=int, default=7)
    ap.add_argument("--seen", action="append", default=[], help="file with names to skip (repeatable)")
    ap.add_argument("--exclude", help="regex: drop matching names (e.g. Slavic/Italian endings)")
    ap.add_argument("--max-onset", type=int, default=40)
    ap.add_argument("--max-middle", type=int, default=60)
    ap.add_argument("--max-onset-middle", type=int, default=4)
    ap.add_argument("--max-ove", type=int, default=3)
    ap.add_argument("--no-caps", action="store_true", help="enumerate only")
    ap.add_argument("--cap-only", action="store_true", help="read names on stdin, apply caps only")
    ap.add_argument("--seed", type=int, default=1)
    a = ap.parse_args()

    on, vo, mi, en = (x.split() for x in (a.onsets, a.vowels, a.middles, a.endings))
    seen = set()
    for f in a.seen:
        seen |= {l.strip().lower() for l in open(f) if l.strip()}
    bad = re.compile(a.exclude) if a.exclude else None

    if a.cap_only:
        names = [l.strip().lower() for l in sys.stdin if l.strip()]
    else:
        names = [o + v + m + e for o in on for v in vo for m in mi for e in en]
    names = [n for n in dict.fromkeys(names)
             if a.min_len <= len(n) <= a.max_len and n not in seen and not (bad and bad.search(n))]
    if a.no_caps:
        print("\n".join(names)); return

    random.Random(a.seed).shuffle(names)
    caps = [(lambda p: p[0], a.max_onset), (lambda p: p[2], a.max_middle),
            (lambda p: (p[0], p[2]), a.max_onset_middle), (lambda p: (p[0], p[1], p[3]), a.max_ove)]
    counts = [Counter() for _ in caps]
    out = []
    for n in names:
        p = split(n, on, vo, mi, en)
        if p is None:
            continue
        keys = [k(p) for k, _ in caps]
        if any(lim and c[k] >= lim for (_, lim), c, k in zip(caps, counts, keys)):
            continue
        for c, k in zip(counts, keys):
            c[k] += 1
        out.append(n)
    print("\n".join(sorted(out)))
    print(f"# {len(out)} of {len(names)} names after caps", file=sys.stderr)


if __name__ == "__main__":
    main()

---
name: brand-name-finder
description: Find a brand or company name that is genuinely unused - pattern-driven ideation with the user, then hard checks of domains across all relevant TLDs, the content of registered domains, web usage and trademark registers. Use when someone wants a name for a product, company or SaaS.
---

# Brand name finder

Goal: 3–10 names the user likes that are **verifiably not in use** (domains,
web, trademarks). This skill exists because a name once recommended as
"free" turned out to be used by an AI startup on its .ai domain after the
name had been registered and filed as a trademark. Details: `references/lessons.md`.

## Hard rules

1. **Never call a name free before all checks in step 5 passed.** A check
   that could not run is "nicht geprüft". Unknown is never free.
2. **Always check .com, .ai, .io, .app**, whatever TLD the user wants.
   Competitors live there; many names with a free .de died on an active
   .ai/.app SaaS.
3. **A taken domain is not a dead name.** Dead only if (a) an active
   business in the same or a neighbouring field, (b) a big business of any
   field (or a near-identical sound: Kovanta ≈ Covanta), or (c) a live
   trademark in classes 9/35/38/42. Parked or for-sale is fine.
4. **Look at what is on every taken domain** (`site-info.sh`).
5. **One name per web search.** `"name"`, then `"name" software`,
   `"name" app`. Mixed OR queries return noise.
6. **Calibrate every lookup method**: a known-taken name must come back taken,
   gibberish must come back free. If a register's UI can't be scripted, look
   for the JSON endpoint its own JavaScript calls before reaching for a
   headless browser.
7. **Show only survivors**, and say which checks were not done.

## Process

### 1. Understand what is being named
Read the product. Single product or umbrella brand? Market, audience,
required TLDs, hyphen OK? Is the domain also the **email domain**? Then
short, dictatable, no hyphen.

### 2. Agree on exclusions
Read `references/naming-principles.md`; decide with the user which
categories to exclude.

### 3. Calibrate taste before generating at scale
- Invent 20–30 names by hand across clearly different styles
  (short/punchy, soft/vowel-ending, English-ish, abstract-tech, root +
  suffix, compound). Number them. No checks yet.
- Ask: "Welche gefallen dir, welche gar nicht?" Reflect the pattern back in
  one or two lines and get a nod. If "alles Mist": change the style axis,
  not just letters.
- Offer a **semantic track** too: a small story from the product's world,
  not overdone, no group/team/mail puns.
- Known dislikes and likes: `references/lessons.md`.

### 4. Generate within the agreed pattern
Short names are nearly all registered (5 letters: every .com, ~90 % .de).
Plan for 6–7 letters or accept a parked .com. Vary endings. Read every name
aloud in German and English; drop what you wouldn't put on a business card.

### 5. Check — in this order, stop at the first hard fail
Run independent checks (domains, sites, web, trademarks per batch) in
parallel with background agents; only the survivors reach the next step.

1. **Domains:** `scripts/check-domains.sh -t "de com ai io app" names…`,
   full list (`-t all`) for survivors.
2. **Taken domains:** `… | awk '$3=="taken"{print $1"."$2}' | scripts/site-info.sh`
   - `for-sale` → note price; `parked` → keep, note.
   - `active` → open it. Software / SaaS / AI / business tools → **dead**.
   - `blocked` → content unknown, check via web search.
3. **Web search** (rule 5), plus near-misses one letter off in the same field.
4. **Trademarks:** `scripts/dpma-search.py -n names…` (DE + EU + IR marks;
   `-n` adds one-letter-off and prefix variants). Any live hit → open
   `https://register.dpma.de/DPMAregister/marke/register/<nr>/<DE|EM|IR>`
   and check classes 9/35/38/42. Fresh filings appear only after weeks
   (a filing only days old returned 0 hits).
   Optional, in the user's browser: TMview (https://www.tmdn.org/tmview)
   for non-EU offices (USPTO, UK, CH). Don't script TMview.
5. **Meaning / mockery** in DE, EN, FR, ES, IT, PL, TR, RU/Serbian: drug
   names, slurs, rude near-words, how people would mock it
   (examples in `references/lessons.md`).
6. **"Have I heard this?"**: "Ich habe mal eine Marke gehört, die ungefähr
   wie XYZ klang — welche?" Catches Swaroni → Swarovski, Zendon → Zendesk.

### 6. Present
Table of survivors only: name, idea, domains (free / for sale), closest
near-miss, trademark result, meaning check, verdict. List checks not done.

### 7. Before buying
Re-run step 5 on the day of purchase. Register main TLDs, file the word
mark (DPMA, then EU within 6 months claiming priority), and talk to a
trademark lawyer if anything near-identical exists in the EU.

## Scripts

- `check-domains.sh`: RDAP (IANA bootstrap + overrides) → WHOIS → DNS over
  HTTPS (`likely-free` = no NS records, say "wahrscheinlich frei"). WHOIS
  is blocked in sandboxes; RDAP works. Fast: split the list, `xargs -P8`,
  `DELAY=0.1`.
- `site-info.sh`: `for-sale | parked | active | blocked | no-site` per domain.
- `dpma-search.py`: DPMAregister SmartSearch
  (`/DPMAregister/smartsearch?queryString=…`, public JSON, no login, `*` and
  `?` wildcards). The Basisrecherche form can't be scripted (Tapestry/JS).
  Calibrated: zendesk → 14 hits, xqzvupt → 0. Output: hits with status;
  summary line `name HITS n (k live)`.

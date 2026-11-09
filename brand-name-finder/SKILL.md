---
name: brand-name-finder
description: Find a brand or company name that is genuinely unused - pattern-driven ideation with the user, then hard checks of domains across all relevant TLDs, the content of registered domains, web usage and trademark registers. Use when someone wants a name for a product, company or SaaS.
---

# Brand name finder

Goal: 3–7 names the user likes that are **verifiably not in use** (domains, web,
trademarks) — not 500 names that are merely "free on .de".

This skill was written after a session that went badly: hundreds of random,
unpronounceable names, wrong "free" claims, and finally a recommendation
(Swavo) that the user registered and filed a trademark for — only to find an
Italian startup selling an "AI Business OS" on swavo.ai. Every rule below
exists because it was broken there.

## Hard rules

1. **Never call a name "free" or "unused" before ALL checks in step 5 passed.**
   If a check could not run, say "nicht geprüft" for that check. Never fill a
   gap with a guess. "Unknown" is never "free".
2. **Check .com, .ai and .io always**, whatever TLD the user wants. For a
   software / AI product these are where competitors live. A taken .ai with an
   active site in a related field kills the name.
3. **A taken domain is not a dead name.** Someone bought it — so what. The
   name is dead only if (a) an active business in the same or a neighbouring
   field runs there, (b) a big business of any field uses it (or a
   near-identical sound: Kovanta ≈ Covanta), or (c) a live trademark exists in
   classes 9/35/38/42. Parked / for sale on .com is fine if .de/.ai are free.
4. **Look at what is on every taken domain** (`scripts/site-info.sh`). "Taken"
   can mean parked, for sale (often buyable) or an active competitor —
   completely different verdicts.
5. **Search the bare name first** (`"swavo"`), then `swavo.ai`, `swavo app`,
   `swavo software`. Do not search `"X" OR "Y" OR "Z" company` — mixed queries
   return noise and hide the real hit.
6. **Show the user only names that passed.** Do not list what is taken unless
   asked. Do not present unchecked names as candidates.
7. **Calibrate every lookup method** before trusting it: a known-taken domain
   must come back taken and gibberish must come back free. The `.eu` check
   via rdap.org returned 404 for *everything* (there is no .eu RDAP) and was
   reported as "free" — that is the failure mode to prevent.

## Process

### 1. Understand what is being named
- Read the product (repo, site, pitch). Ask: single product or umbrella brand
  ("wie Google" — must not be tied to one product like Mail or KI)?
- Market and audience (here: German B2B). Required TLDs. Is a hyphen OK?
- Will the domain also be an **email domain**? Then short, easy to dictate,
  no hyphen (`name@xyz.de`, "wie gmail.com / mailbox.org").

### 2. Read the naming theory
Read `references/naming-principles.md` (summary of a brand-name psychology
paper plus the user's own process). Decide with the user which **categories
to exclude** up front.

### 3. Calibrate taste BEFORE generating at scale  ← the step that was skipped
Do NOT start with a script producing thousands of random syllables.
- Invent 20–30 names **by hand**, deliberately spread over clearly different
  styles (short/punchy, soft/vowel-ending, English-ish, abstract-tech,
  meaningful root + suffix, compound). Number them. Use invented words only —
  not existing brands as examples.
- No checks yet. Ask: "Welche gefallen dir, welche gar nicht?"
- State the pattern you see back in one or two lines (syllables, ending,
  consonants, vibe) and get a nod.
- Repeat once if the answer is "alles Mist". Each round, change the style
  axis, not just the letters.

What went wrong in practice (avoid):
- random consonant clusters → "Pruzim, Kugirk" (unpronounceable)
- -o/-i/-zo endings everywhere → "klingt italienisch, niemand kauft bei Italienern"
- -ir/-ul/-um → "klingt arabisch"
- Latin -ion/-ora/-is/-ix/-ant → "klingt nach Pharmakonzern"
- 6-letter -el/-en/-ar names → "das sind Vornamen, keine Firmennamen"
- Lieferando-style (German word + -ando) → "für B2B unmöglich"
- all names following one template → "alles total ähnlich"
- names that are just the description ("aireadygroupware", "agentbuero")
- far-fetched metaphors only fans get (The-Expanse references)

What the user liked: 2 syllables, ends on a vowel (mostly -o), clear
consonant start (often a cluster like sw-, gr-, fl-), v or n in the middle,
friendly-technical but not childish: Lumo, Kado, Nuvo, Tava, Zubio, Gravo,
Swivo, Flinto, Swavo, Svento. (All of these turned out to be in use.)

Also offer a **semantic** track: names with a small, not overdone story
from the product's world (for groupware: messenger, letters, office,
archive, commons — lat. *nuntius* Bote, *tablinum* Aktenraum, Munin = Odins
Rabe der Erinnerung). No "group/team/mail" puns.

### 4. Generate within the agreed pattern
Facts from the Swavo rename (Nov 2026): of 104 five-letter CCVCV/-o names,
every .com and 90 % of .de were registered. Plan for 6–7 letters, or accept
a registered-but-parked .com. Many -ano/-avo/-ino names in a row sound
Italian — vary endings.
Now produce many candidates (by hand + optionally a generator constrained to
the agreed pattern). Pre-filter by ear: read each one aloud in German and
English. Drop anything you would not put on a business card.

### 5. Check — in this order, stop at the first hard fail
For each shortlisted name (aim for 10–20):

1. **Domains, all TLDs:**
   `scripts/check-domains.sh -t "de com app ai io eu net org co dev" name1 name2 …`
   (`-t all` for the long list). Needs `curl` + `jq`; `whois` for .eu/.co/.at
   (port 43 — works on a normal computer, usually not in sandboxes).
   Note required-TLD failures, but don't stop: a name free on .de with an
   active competitor on .ai is NOT free.
2. **Content of every taken domain:**
   `… | awk '$3=="taken"{print $1"."$2}' | scripts/site-info.sh`
   - `for-sale` → note the price (domainmarkt, sedo, dan.com …), may be OK.
   - `parked`  → weak signal, keep but note.
   - `active`  → open it. Same or neighbouring field (software, SaaS, AI,
     business tools) → **name is dead.** Unrelated field (a bakery) → note.
3. **Web search**, one search per name, bare name in quotes, plus
   `"name" software` and `"name" app`. Also look for near-misses one letter
   off in the same field (Swovo vs Swavo, Zendon vs Zendo, Mevon vs Mevo).
4. **Trademarks:** Scripted TMview access (headless browser) was blocked as
   bot-check circumvention — don't. Use the official EUIPO trademark search
   API (free registration, API key) or let the user search TMview (https://www.tmdn.org/tmview — covers DPMA, EUIPO,
   USPTO, national offices; use fuzzy search) for the name and its near
   misses, classes 9, 35, 38, 42. DPMAregister for Germany. Needs a browser.
5. **Meaning / mockery check:** What does it mean or sound like in German,
   English, French, Spanish, Italian, Polish, Turkish, Russian/Serbian? Drug
   or medicine names? Slurs? How would someone make fun of it? Examples that
   killed names: Pibo ≈ pivo (Bier), Bimba ≈ bimbo, Gluvo = taub (serb.),
   Glevo = Antibiotikum, Frento = Tiermedikament, Nasola = Nasenspray,
   Jahoba ≈ Jehova, Brindel ≈ Windel, Kenodor ⊃ "odor", Premine = Krypto-Begriff,
   Ordel ≈ Bordell.
6. **"Have I heard this?"** prompt: "Ich habe mal eine Marke gehört, die
   ungefähr wie XYZ klang — welche könnte das sein?" — catches famous
   near-names (Swavo → Swarovski; Zendon → Zendesk).

### 6. Present
A table of only the survivors: name, domains (free / for sale + price),
closest near-miss, meaning check, own verdict. 3–7 names. Say clearly which
checks were NOT done (e.g. trademark search needs the user's browser).

### 7. Before the user buys anything
Re-run step 5 on the final name on the day of purchase (new startups appear
weekly). Recommend: register main TLDs, file the word mark (DPMA, then EU
within 6 months claiming priority), and a short call with a trademark lawyer
when anything near-identical exists in the EU.

## Scripts

- `scripts/check-domains.sh` — RDAP (IANA bootstrap + overrides for .de, .io,
  .ch, .li) with WHOIS fallback and per-TLD calibration. TSV output:
  `name tld free|taken|unknown method`.
  Without WHOIS (port 43 blocked in sandboxes) it falls back to DNS over
  HTTPS: `likely-free` = no NS records — report as "wahrscheinlich frei".
  Fast pre-filter: run several chunks in parallel (`split` + `xargs -P8`,
  `DELAY=0.1`), `-t "de com ai io app"` first, full list only for survivors.
- `scripts/site-info.sh` — classifies registered domains as
  `for-sale | parked | active | blocked | no-site` with final URL and title.
  `blocked` = bot challenge / error page: content unknown, look via search.

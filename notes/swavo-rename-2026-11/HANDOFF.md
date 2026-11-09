# Swavo rename — handoff (2026-11-09)

Goal: find a new name for Swavo (swavo.ai is used by an Italian "AI Business OS"
startup — must not happen again) and keep improving the `brand-name-finder`
skill while doing it, so it works well in the end (also: keep SKILL.md lean).

## Product being named
Swavo (repo `swavo-de/app`): AI-first groupware for the German market —
mail server + webmail, calendar/contacts (CalDAV/CardDAV), document archive
with OCR, MCP access for AI assistants, approvals. Hosted in Germany.
Umbrella brand ("wie Google"), domain is also the email domain → short,
dictatable, no hyphen.

## User's rules (stated in this session)
- A registered .com is **not** a knockout. Knockout only if there is
  (a) an active business in the same/neighbouring field, (b) a big business
  of any field (incl. near-identical sound), or (c) a live trademark.
- Semantic track wanted: a small story fitting groupware (messenger, letters,
  office, archive, commons …) — but not overdone, **no "group"/"team" puns**.
- Paid services or an own server are OK if the sandbox is too limited.
- Earlier taste profile (see SKILL.md step 3): 2 syllables, vowel ending
  (often -o), clear consonant start, v/n in the middle, friendly-technical.
  Too many -ano/-avo/-ino in a row sounds Italian.

## What was learned (already partly in SKILL.md / scripts)
- RDAP works from the cloud sandbox for .de .com .ai .io .app .net .org .dev.
  WHOIS (port 43) is blocked → `check-domains.sh` now falls back to DNS over
  HTTPS for .eu/.co (`likely-free`).
- 104 five-letter Swavo-pattern names: **all .com taken, ~90 % .de taken.**
- `site-info.sh` misread Cloudflare challenge pages as `active` → fixed
  (`blocked` verdict, marketplace redirects = for-sale).
- TMview via headless Playwright works technically, but the auto-mode
  classifier blocked it as bot-check circumvention. Use the official EUIPO
  trademark API (needs API key) or the user's own browser instead.
  → Open task: add an EUIPO-API script to the skill (or run locally).
- WebSearch tool returns summaries; good enough to catch near-misses.

## Candidates (state when the session stopped)
Trademark check: **not done for any of them.**

| Name | free | .com | web search |
|---|---|---|---|
| Munvo (Munin = Odin's raven of memory) | .de .ai .io .app | taken, content not checked | not done |
| Telvik | .de .ai .io .app | parked | clean |
| Fenvik | .de .ai .io .app | parked | clean (≈ Fevik, Norwegian village) |
| Ovanda | .de .ai .io .app | parked | clean |
| Tarova | .de .ai .io .app | parked | village in Russia only |
| Kelvea | .de .ai .io .app | parked | clean |
| Dovea | .de .ai .io .app | for sale (namestar) | only "dove" hits |

Also .de-free from the semantic round (round4), content not yet checked:
tablin, tablina (tablinum = Roman records room), rafno (hrafn = raven),
merkuro, bodvo/bodvi (boð = message), atrino, nuntivo; nunto (nuntius =
messenger) has .ai/.io/.app taken, .com for sale.

Dropped: Kavly (≈ Kavli Foundation), Brivea (≈ drug Briviact), Kovanta
(≈ Covanta), Kavedo / Kalvano (active digital/ad businesses on .com),
Snavo/Twavo/Kwavo (too close to Swavo).

## Next steps
1. site-info on round4 survivors' taken domains; web search Munvo + round4.
2. Show the user a short mixed list (pattern + semantic) for taste feedback.
3. Trademark check (EUIPO API / TMview in browser) for the survivors.
4. Meaning/mockery check in DE/EN/FR/ES/IT/PL/TR/RU.
5. Slim down SKILL.md and fold the learnings above into it.

## Data
`data/roundN.txt` = names tried, `data/rN.tsv` = domain results
(`name tld status method`), `data/sites.tsv` = content of taken domains.

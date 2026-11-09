# Lessons from real naming sessions

## Taste: what the user rejected (and why)
- random consonant clusters: "Pruzim, Kugirk" (unpronounceable)
- -o/-i/-zo endings everywhere, many -ano/-avo/-ino in a row → "klingt italienisch"
- -ir/-ul/-um → "klingt arabisch"
- Latin -ion/-ora/-is/-ix/-ant → "klingt nach Pharmakonzern"
- 6-letter -el/-en/-ar names → "das sind Vornamen, keine Firmennamen"
- German word + -ando (Lieferando style) → "für B2B unmöglich"
- all names from one template → "alles total ähnlich"
- descriptive names ("aireadyoffice", "agentkontor")
- far-fetched metaphors only fans get (The-Expanse references)
- puns on group/team/mail

## Taste: example profile from one session
2 syllables, vowel ending (mostly -o), clear consonant start (often sw-, gr-,
fl-), v or n in the middle, friendly-technical, not childish:
Lumo, Kado, Nuvo, Tava, Zubio, Gravo, Flinto, Svento.
(All of them turned out to be in use.)
Semantic track for groupware (small story, not overdone): lat. *nuntius*
(Bote), *tablinum* (Aktenraum), Munin (Odins Rabe der Erinnerung), hrafn, boð.

## Market facts (Nov 2026)
- 104 five-letter CCVCV/-o names: every .com and ~90 % of .de registered.
  Plan for 6–7 letters, or accept a parked/for-sale .com.
- With .de free, names still died on: an active .app/.ai SaaS (Tablin,
  Atrino, Teselo), a same-named MarTech consultancy (Munvo), messaging
  software on .com (Nuntivo), a big marketplace (Merkuro), near-sounding big
  brands (Kovanta ≈ Covanta, Kavly ≈ Kavli Foundation, Brivea ≈ Briviact).
- A name once called "free" died on its .ai domain (an "AI Business OS"
  startup) after it had been registered and filed as a trademark.

## Meaning / mockery kills
Pibo ≈ pivo (Bier), Bimba ≈ bimbo, Gluvo = taub (serb.), Glevo = Antibiotikum,
Frento = Tiermedikament, Nasola = Nasenspray, Jahoba ≈ Jehova,
Brindel ≈ Windel, Kenodor ⊃ "odor", Premine = Krypto-Begriff, Ordel ≈ Bordell.
Famous near-names: Swaroni → Swarovski, Zendon → Zendesk.

## Tooling
- RDAP works from cloud sandboxes (.de .com .ai .io .app .net .org .dev);
  WHOIS port 43 does not → check-domains.sh falls back to DNS over HTTPS.
- rdap.org returned 404 for every .eu (no .eu RDAP) — was reported "free".
  Calibrate every method.
- site-info.sh used to read Cloudflare challenge pages as "active" → now
  `blocked`.
- Scripted TMview (headless browser) was blocked as bot-check circumvention;
  the TMview JSON API rejects curl ("Request Rejected"). DPMAregister's
  Basisrecherche form can't be scripted (Tapestry/JS: the POST redirects back
  to an empty form), but the SmartSearch JSON endpoint its own JS calls
  (`/DPMAregister/smartsearch?queryString=…`, supports `*` and `?`) works and
  covers DE + EU + IR marks → dpma-search.py. General rule: find the JSON
  endpoint the page's JS calls before using a headless browser.
- New filings show up with a delay: a filing only days old returned 0 hits
  in DPMAregister.
- Web search: mixed `"X" OR "Y" OR "Z"` queries return noise and hide hits.

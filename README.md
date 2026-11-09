# skills

Agent skills (SKILL.md + scripts) for Claude and other agents.

| Skill | What it does |
|---|---|
| [brand-name-finder](brand-name-finder/SKILL.md) | Find a brand name that is genuinely unused: taste calibration with the user, then domain checks across all TLDs (RDAP/WHOIS), content check of registered domains, web, trademark and meaning checks. |

## Install

Copy a skill folder into your skills directory, e.g. `~/.claude/skills/brand-name-finder/`.
Scripts need `bash`, `curl`, `jq` (and `whois` for TLDs without RDAP such as .eu).

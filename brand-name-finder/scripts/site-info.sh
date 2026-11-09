#!/usr/bin/env bash
# site-info.sh — what is actually ON a registered domain?
#
# Usage: site-info.sh swavo.com swavo.ai ...
#        check-domains.sh name | awk '$3=="taken"{print $1"."$2}' | site-info.sh
#
# Output (TSV): domain  verdict  final_url  title
#   verdict: for-sale | parked | active | no-site
#   "active" means a real site — open it and find out WHO it is and WHAT they sell.
#   A registered domain with an active business in a related field kills the name.

set -uo pipefail
DOMS=("$@")
if [ ${#DOMS[@]} -eq 0 ]; then while read -r d; do [ -n "$d" ] && DOMS+=("$d"); done; fi

SALE_RE='domainmarkt|sedo\.|dan\.com|afternic|hugedomains|greatestdomains|godaddy\.com/domainsearch|spaceship\.com|namecheap\.com/market|undeveloped|atom\.com|squadhelp|brandbucket|for sale|zu verkaufen|kaufen sie diese domain|buy this domain|make an offer|domain.*(is|ist).*(for sale|verkauf)'
PARK_RE='parked|parking|bodis|parkingcrew|above\.com|domain (is )?registered|coming soon|under construction|this domain|default web page|index of /|welcome to nginx|it works!'

for d in "${DOMS[@]}"; do
  out=$(curl -sL --max-time 15 -A 'Mozilla/5.0 (brand-name-finder)' -w '\n__FINAL__%{url_effective}' "https://$d" 2>/dev/null \
     || curl -sL --max-time 15 -A 'Mozilla/5.0 (brand-name-finder)' -w '\n__FINAL__%{url_effective}' "http://$d" 2>/dev/null)
  final=$(printf '%s' "$out" | sed -n 's/^__FINAL__//p' | tail -1)
  body=$(printf '%s' "$out" | sed '/^__FINAL__/d' | tr '\n' ' ' | head -c 300000)
  title=$(printf '%s' "$body" | grep -oiE '<title[^>]*>[^<]*' | head -1 | sed -E 's/<title[^>]*>//I' | cut -c1-100)
  if [ -z "$body" ]; then v=no-site
  elif printf '%s %s' "$final" "$body" | grep -Eqi "$SALE_RE"; then v=for-sale
  elif printf '%s' "$body" | grep -Eqi "$PARK_RE" || [ ${#body} -lt 1500 ]; then v=parked
  else v=active; fi
  printf '%s\t%s\t%s\t%s\n' "$d" "$v" "${final:-}" "${title:-}"
done

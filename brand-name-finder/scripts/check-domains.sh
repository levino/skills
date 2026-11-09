#!/usr/bin/env bash
# check-domains.sh — check whether names are registered under many TLDs.
#
# Usage:
#   check-domains.sh [-t "de app com eu"] name1 [name2 ...]
#   check-domains.sh -t all < names.txt          # one name per line on stdin
#
# Output (TSV on stdout): name  tld  status  method
#   status: free | taken | likely-free | unknown
#   unknown means: this TLD could not be checked reliably from this machine.
#   likely-free means: only DNS could be asked (no NS records). Registered
#   domains without nameservers exist, so say "wahrscheinlich frei (nur DNS)".
#   NEVER report "unknown" or "likely-free" as free.
#
# How it works:
#   1. RDAP via the IANA bootstrap file (data.iana.org/rdap/dns.json),
#      plus manual overrides for registries missing from it (.de, .io, .ch, .li).
#      HTTP 200 = taken, 404 = free.
#   2. For TLDs without RDAP (.eu, .co, .at, ...), fall back to WHOIS on port 43
#      (needs the `whois` command and outbound port 43 — works on a normal
#      computer, usually NOT in sandboxes/proxies).
#   3. If WHOIS is not possible, DNS over HTTPS (cloudflare-dns.com): NS records
#      = taken, NXDOMAIN = likely-free.
#      Also used when RDAP keeps failing (429 rate limit when several agents
#      check in parallel; .ai/.io are the strictest): method "dns-fallback".
#   4. Calibration: before trusting a TLD, query nic.<tld> or a known-taken
#      domain AND a random gibberish domain. If they don't give different
#      answers, every result for that TLD is reported as "unknown".
#
# Requires: bash, curl, jq. Optional: whois.

set -uo pipefail

DEFAULT_TLDS="de com app eu io ai net org co dev ch at"
ALL_TLDS="de com app eu io ai net org co dev ch at li info biz xyz tech cloud online site store me tv so gg"
TLDS="$DEFAULT_TLDS"
DELAY="${DELAY:-0.3}"        # seconds between requests (be polite, avoid 429)

while getopts "t:" opt; do
  case $opt in
    t) if [ "$OPTARG" = all ]; then TLDS="$ALL_TLDS"; else TLDS="$OPTARG"; fi ;;
    *) echo "usage: $0 [-t 'de com app' | -t all] name..." >&2; exit 2 ;;
  esac
done
shift $((OPTIND - 1))

NAMES=("$@")
if [ ${#NAMES[@]} -eq 0 ]; then
  while IFS= read -r line; do
    line="$(echo "$line" | tr '[:upper:]' '[:lower:]' | tr -d '[:space:]')"
    [ -n "$line" ] && NAMES+=("$line")
  done
fi
[ ${#NAMES[@]} -eq 0 ] && { echo "no names given" >&2; exit 2; }

command -v jq >/dev/null || { echo "jq is required" >&2; exit 2; }
HAVE_WHOIS=0; command -v whois >/dev/null && HAVE_WHOIS=1

# --- RDAP endpoints ----------------------------------------------------------
declare -A RDAP
BOOT="$(curl -fsS --max-time 20 https://data.iana.org/rdap/dns.json 2>/dev/null || true)"
if [ -n "$BOOT" ]; then
  while IFS=$'\t' read -r tld url; do RDAP[$tld]="$url"; done < <(
    echo "$BOOT" | jq -r '.services[] | .[1][0] as $u | .[0][] | "\(.)\t\($u)"')
fi
# Registries with RDAP that are missing from the IANA bootstrap:
RDAP[de]="https://rdap.denic.de/"
RDAP[io]="https://rdap.identitydigital.services/rdap/"
RDAP[ch]="https://rdap.nic.ch/"
RDAP[li]="https://rdap.nic.ch/"

# --- WHOIS servers + "available" markers for TLDs without RDAP ---------------
declare -A WHOIS_SRV=( [eu]=whois.eu [co]=whois.registry.co [at]=whois.nic.at
                       [me]=whois.nic.me [tv]=whois.nic.tv [so]=whois.nic.so [gg]=whois.gg )
FREE_RE='(^|\s)(No match|NOT FOUND|Not found|No Data Found|Status:\s*AVAILABLE|nothing found|No entries found|is free|does not exist|AVAILABLE)'

rdap_status() {   # $1 = domain, $2 = base url → prints free|taken|unknown
  local code i
  for i in 1 2 3 4; do
    code=$(curl -s -L -o /dev/null -w '%{http_code}' --max-time 15 "${2}domain/$1")
    case $code in
      200) echo taken; return ;;
      404) echo free; return ;;
      429|5*|000) sleep $((i * 2 + RANDOM % 3)) ;;   # backoff + jitter (parallel agents)
      *) break ;;
    esac
  done
  echo unknown
}

whois_status() {  # $1 = domain, $2 = server
  [ $HAVE_WHOIS = 1 ] || { echo unknown; return; }
  local out; out=$(timeout 15 whois -h "$2" "$1" 2>/dev/null) || true
  [ -z "$out" ] && { echo unknown; return; }
  if echo "$out" | grep -Eqi "$FREE_RE"; then echo free; else echo taken; fi
}

dns_status() {    # $1 = domain → taken | likely-free | unknown  (DNS over HTTPS)
  # Weaker than RDAP/WHOIS: a domain can be registered without nameservers.
  # So NXDOMAIN is only "likely-free", never "free".
  local st
  st=$(curl -s --max-time 10 -H 'accept: application/dns-json' \
        "https://cloudflare-dns.com/dns-query?name=$1&type=NS" | jq -r '.Status // empty' 2>/dev/null)
  case $st in 0) echo taken ;; 3) echo likely-free ;; *) echo unknown ;; esac
}

check() {         # $1 = domain, $2 = tld → "status<TAB>method"
  local r
  if [ -n "${RDAP[$2]:-}" ]; then
    r=$(rdap_status "$1" "${RDAP[$2]}")
    # RDAP rate-limits (429) under parallel load, notably .ai/.io → DNS fallback.
    if [ "$r" = unknown ]; then echo -e "$(dns_status "$1")\tdns-fallback"; else echo -e "$r\trdap"; fi
    return
  fi
  if [ -n "${WHOIS_SRV[$2]:-}" ]; then
    r=$(whois_status "$1" "${WHOIS_SRV[$2]}")
    [ "$r" != unknown ] && { echo -e "$r\twhois"; return; }
  fi
  # No RDAP, WHOIS unavailable (typical in sandboxes: port 43 blocked) → DNS.
  echo -e "$(dns_status "$1")\tdns"
}

# --- calibration -------------------------------------------------------------
declare -A OK
GIB="xq$(date +%s)zvkw"
for tld in $TLDS; do
  taken=$(check "nic.$tld" "$tld" | cut -f1)
  [ "$taken" != taken ] && taken=$(check "google.$tld" "$tld" | cut -f1)
  free=$(check "$GIB.$tld" "$tld" | cut -f1)
  if [ "$taken" = taken ] && { [ "$free" = free ] || [ "$free" = likely-free ]; }; then OK[$tld]=1
  else OK[$tld]=0; echo "# .$tld cannot be checked reliably here (taken→$taken, gibberish→$free); results will be 'unknown'" >&2
  fi
done

# --- main loop ---------------------------------------------------------------
for name in "${NAMES[@]}"; do
  for tld in $TLDS; do
    if [ "${OK[$tld]}" = 1 ]; then
      res=$(check "$name.$tld" "$tld"); sleep "$DELAY"
    else
      res=$'unknown\tuncalibrated'
    fi
    echo -e "$name\t$tld\t$res"
  done
done

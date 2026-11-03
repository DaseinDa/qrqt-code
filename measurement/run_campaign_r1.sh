#!/usr/bin/env bash
# run_campaign_r1.sh -- ROUND-1 measurement campaign inside WSL2 (approved scope, 2026-10-21):
#   KEM (ML-KEM x3, FrodoKEM salted x6, eFrodoKEM x6) + AES-GCM only; C harness + liboqs speed_kem + openssl speed;
#   no Python venv, no BIOS/powercfg changes; turbo state is whatever the laptop is in, recorded in the label.
# Usage: bash run_campaign_r1.sh <label> [quick]        label e.g. x86_turbo_default_run1
set -euo pipefail
LABEL="${1:?label required}"; QUICK="${2:-}"
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORK=/root/qrqt-bench; SRC=$WORK/liboqs
OUT="$HERE/results/$LABEL"; mkdir -p "$OUT"
CPU=2; PIN="taskset -c $CPU chrt -f 50"
DUR=10; NARGS=""
if [[ "$QUICK" == "quick" ]]; then DUR=2; NARGS="--n-fast 5000 --n-mid 1000 --n-slow 200 --warm 100"; fi
KEMS="ML-KEM-512 ML-KEM-768 ML-KEM-1024 FrodoKEM-640-AES FrodoKEM-976-AES FrodoKEM-1344-AES FrodoKEM-640-SHAKE FrodoKEM-976-SHAKE FrodoKEM-1344-SHAKE eFrodoKEM-640-AES eFrodoKEM-976-AES eFrodoKEM-1344-AES eFrodoKEM-640-SHAKE eFrodoKEM-976-SHAKE eFrodoKEM-1344-SHAKE"
KEMARGS=""; for k in $KEMS; do KEMARGS="$KEMARGS --kem $k"; done

{ echo "label=$LABEL quick=$QUICK utc=$(date -u +%FT%TZ)"; uname -a; lsb_release -ds 2>/dev/null || true
  grep -m1 "model name" /proc/cpuinfo; nproc; lscpu | grep -E "Flags" | grep -oE "avx2|aes|avx512f" | sort -u | tr '\n' ' '; echo
  gcc --version | head -1; openssl version; git -C "$SRC" log -1 --format="liboqs commit %H %cd"; grep -m1 OQS_VERSION_TEXT "$SRC/CMakeLists.txt"
  for v in native generic; do echo "--- CMakeCache $v ---"; grep -E "^OQS_(OPT_TARGET|DIST_BUILD|USE_OPENSSL):" "$SRC/build-$v/CMakeCache.txt"; done
  echo "pin=$PIN  frequency state: not controlled (default Windows power plan, turbo enabled); not observable from WSL"
  echo "--- algorithm sizes (bytes: pk sk ct ss) ---"
  "$SRC/build-native/tests/dump_alg_info" 2>/dev/null | grep -A4 -E "^(ML-KEM|e?FrodoKEM)" | grep -E "^(ML-KEM|e?FrodoKEM)|length" | paste - - - - - 2>/dev/null || true
} > "$OUT/metadata.txt" 2>&1

for v in native generic; do
  impl=$([[ $v == native ]] && echo avx2 || echo generic)
  echo "== C harness ($v) =="
  $PIN "$WORK/bench_oqs_percentiles_$v" --label "$LABEL" --impl "$impl" --host "$(hostname)" --no-sig $NARGS $KEMARGS \
      > "$OUT/c_harness_$v.csv" 2> "$OUT/c_harness_$v.err"
  echo "== speed_kem ($v), $DUR s per op =="
  { for alg in $KEMS; do $PIN "$SRC/build-$v/tests/speed_kem" -d "$DUR" "$alg"; done; } > "$OUT/speed_kem_$v.log" 2>&1
  python3 "$HERE/parse_speed_output.py" "$OUT/speed_kem_$v.log" --label "$LABEL" --impl "$impl" \
      --library-version "$(grep -m1 OQS_VERSION_TEXT "$SRC/CMakeLists.txt" | sed -E 's/.*"([^"]+)".*/\1/')" --out "$OUT/speed_$v.csv" || true
done
echo "== openssl speed AES-GCM, 16-byte blocks =="
$PIN openssl speed -evp aes-128-gcm -bytes 16 -seconds 3 > "$OUT/openssl_aes128gcm.log" 2>&1 || true
{ head -1 "$OUT/c_harness_native.csv"; for f in "$OUT"/c_harness_*.csv "$OUT"/speed_*.csv; do [[ -f $f ]] && tail -n +2 "$f"; done; } > "$OUT/merged_$LABEL.csv"
echo "campaign $LABEL done -> $OUT/merged_$LABEL.csv ($(wc -l < "$OUT/merged_$LABEL.csv") rows)"

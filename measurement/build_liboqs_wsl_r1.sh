#!/usr/bin/env bash
# build_liboqs_wsl_r1.sh -- ROUND-1 build inside WSL2 Ubuntu 24.04, within the scope approved on 2026-10-21:
#   * isolated working directory /root/qrqt-bench (sources, two liboqs prefixes, results)
#   * build dependencies installed in the WSL guest only (cmake, ninja-build, libssl-dev); nothing on the host
#   * NO Python venv / pip (round 1 uses the C harness and liboqs' own speed_kem only)
#   * NO BIOS / powercfg / turbo changes; the frequency state is simply recorded
#   * KEM + AES-GCM only (ML-DSA is built because it is in the default set, but not timed in round 1)
# Usage (from Windows):  wsl -e bash -lc "bash /mnt/c/<path-to-repository>/measurement/build_liboqs_wsl_r1.sh"
set -euo pipefail
export DEBIAN_FRONTEND=noninteractive
WORK=/root/qrqt-bench
SRC=$WORK/liboqs
TAG=0.16.0
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
NJOBS="$(nproc)"
mkdir -p "$WORK"
LOG=$WORK/build.log
exec > >(tee -a "$LOG") 2>&1
echo "== $(date -u +%FT%TZ) round-1 build start; work dir $WORK =="

echo "== step 0: WSL-guest build dependencies (apt) =="
if ! command -v cmake >/dev/null || ! command -v ninja >/dev/null || ! dpkg -s libssl-dev >/dev/null 2>&1; then
  apt-get update -q
  apt-get install -y -q cmake ninja-build libssl-dev
fi
cmake --version | head -1; ninja --version; gcc --version | head -1; openssl version

echo "== step 1: liboqs source at tag $TAG =="
if [[ ! -d "$SRC/.git" ]]; then
  git clone --depth 1 --branch "$TAG" https://github.com/open-quantum-safe/liboqs.git "$SRC"
fi
git -C "$SRC" log -1 --format='liboqs commit %H (%cd)' --date=iso
grep -m1 OQS_VERSION_TEXT "$SRC/CMakeLists.txt" || true
echo "-- KEM algorithm docs present:"; ls "$SRC/docs/algorithms/kem/" || true
echo "-- FrodoKEM naming in this release:"; grep -i -m8 -E "efrodokem|salt|FrodoKEM-640" "$SRC/docs/algorithms/kem/frodokem.md" 2>/dev/null || true
echo "-- CMake options mentioning FRODO:"; grep -rhoE "OQS_ENABLE_KEM_[A-Za-z_]*FRODO[A-Za-z_0-9]*" "$SRC/.CMake" "$SRC/CMakeLists.txt" 2>/dev/null | sort -u | head -20 || true

build_variant () {
  local name="$1" opt_target="$2"
  local bdir="$SRC/build-$name" prefix="$WORK/oqs-$name"
  echo "== step 2/3: build '$name' (OQS_OPT_TARGET=$opt_target) -> $prefix =="
  mkdir -p "$bdir"
  cmake -S "$SRC" -B "$bdir" -GNinja \
    -DCMAKE_BUILD_TYPE=Release -DBUILD_SHARED_LIBS=ON \
    -DCMAKE_INSTALL_PREFIX="$prefix" \
    -DOQS_USE_OPENSSL=ON -DOQS_DIST_BUILD=OFF -DOQS_OPT_TARGET="$opt_target" \
    -DOQS_BUILD_ONLY_LIB=OFF -DOQS_ENABLE_KEM_ML_KEM=ON -DOQS_ENABLE_KEM_FRODOKEM=ON
  grep -E "^OQS_(OPT_TARGET|DIST_BUILD|USE_OPENSSL):" "$bdir/CMakeCache.txt" || true
  grep -E "^OQS_ENABLE_KEM_(ml_kem_512|frodokem_640_aes|efrodokem_640_aes)[a-z_0-9]*:" "$bdir/CMakeCache.txt" || true
  ninja -C "$bdir" -j "$NJOBS"
  cmake --install "$bdir" >/dev/null
}
build_variant native  auto
build_variant generic generic

echo "== step 4: KAT self-tests before timing =="
for v in native generic; do
  b="$SRC/build-$v/tests"
  echo "-- [$v] KEMs available:"; "$b/speed_kem" --algs 2>/dev/null | grep -iE "ML-KEM|Frodo" | tr '\n' ' '; echo
  for alg in $("$b/speed_kem" --algs 2>/dev/null | grep -E "^(ML-KEM-(512|768|1024)|e?FrodoKEM-(640|976|1344)-(AES|SHAKE))$"); do
    if "$b/kat_kem" "$alg" >/dev/null 2>&1; then echo "   [$v] kat_kem $alg OK"; else echo "   [$v] kat_kem $alg FAILED"; fi
  done
done

echo "== step 5: C harness against both prefixes =="
for v in native generic; do
  gcc -O2 -std=c11 -Wall -o "$WORK/bench_oqs_percentiles_$v" "$HERE/bench_oqs_percentiles.c" \
      -I"$WORK/oqs-$v/include" -L"$WORK/oqs-$v/lib" -Wl,-rpath,"$WORK/oqs-$v/lib" -loqs -lcrypto -lm
  echo "   built $WORK/bench_oqs_percentiles_$v"
done
echo "== $(date -u +%FT%TZ) round-1 build done =="

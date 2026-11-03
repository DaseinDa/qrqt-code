/* bench_oqs_percentiles.c -- per-sample latency harness for the QRQT campaign (B3).
 *
 * Measures, with clock_gettime(CLOCK_MONOTONIC_RAW) around EVERY call, the latency of
 *   keygen, encaps, decaps, encaps+decaps (fused)       for each requested liboqs KEM,
 *   keygen, sign, verify                                 for each requested liboqs signature,
 *   AES-128-GCM / AES-256-GCM encrypt and decrypt        of a 16-byte message via OpenSSL EVP,
 *   an empty timed region (timer overhead baseline),
 * and prints one CSV line per operation with n, min, p50, mean, p90, p99, max, stdev in us.
 * The liboqs speed_kem tool reports only mean/stdev; this harness exists to get p50/p99.
 *
 * Build (see build_liboqs_wsl.sh step 6):
 *   gcc -O2 -std=c11 -o bench_oqs_percentiles bench_oqs_percentiles.c \
 *       -I$PREFIX/include -L$PREFIX/lib -Wl,-rpath,$PREFIX/lib -loqs -lcrypto -lm
 * Run:
 *   taskset -c 2 chrt -f 50 ./bench_oqs_percentiles --impl avx2 --label x86_turbo_on_run1 \
 *       [--n-fast 100000 --n-slow 5000 --warm 1000] [--kem ML-KEM-512 ...] [--sig ML-DSA-44 ...]
 * Output columns match results_schema.csv (library=liboqs, timing_method=clock_gettime_monotonic_raw).
 * NOT RUN as of 2026-10-20.
 */
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <math.h>
#include <time.h>
#include <unistd.h>
#include <oqs/oqs.h>
#include <openssl/evp.h>
#include <openssl/rand.h>

static const char *DEFAULT_KEMS[] = {"ML-KEM-512", "ML-KEM-768", "ML-KEM-1024",
                                     "FrodoKEM-640-AES", "FrodoKEM-976-AES", "FrodoKEM-1344-AES",
                                     "FrodoKEM-640-SHAKE", "FrodoKEM-976-SHAKE", "FrodoKEM-1344-SHAKE", NULL};
static const char *DEFAULT_SIGS[] = {"ML-DSA-44", "ML-DSA-65", "ML-DSA-87", NULL};

static inline uint64_t now_ns(void) {
    struct timespec ts; clock_gettime(CLOCK_MONOTONIC_RAW, &ts);
    return (uint64_t)ts.tv_sec * 1000000000ull + (uint64_t)ts.tv_nsec;
}
static int cmp_u64(const void *a, const void *b) {
    uint64_t x = *(const uint64_t *)a, y = *(const uint64_t *)b; return (x > y) - (x < y);
}
/* nearest-rank percentile on a sorted array */
static double pct(const uint64_t *s, size_t n, double p) {
    size_t k = (size_t)ceil(p / 100.0 * (double)n); if (k == 0) k = 1; if (k > n) k = n; return (double)s[k - 1];
}
static const char *g_label = "unlabelled", *g_impl = "unknown", *g_host = "";
static char g_ts[32];

static void report(const char *lib, const char *libver, const char *alg, const char *op,
                   size_t msg_bytes, size_t warm, uint64_t *s, size_t n) {
    double mean = 0, m2 = 0;
    for (size_t i = 0; i < n; i++) { double d = (double)s[i] - mean; mean += d / (double)(i + 1); m2 += d * ((double)s[i] - mean); }
    double sd = n > 1 ? sqrt(m2 / (double)(n - 1)) : 0.0;
    qsort(s, n, sizeof(uint64_t), cmp_u64);
    /* timestamp_utc,host_id,hardware_class,cpu_model,freq_state,core_pinned,os,library,library_version,
       implementation,algorithm,operation,message_bytes,n_reps,warmup_reps,timing_method,
       min_us,p50_us,mean_us,p90_us,p99_us,max_us,stdev_us,tsc_ticks_mean,source,notes */
    printf("%s,%s,x86_laptop,,%s,taskset,linux-wsl2,%s,%s,%s,%s,%s,%zu,%zu,%zu,clock_gettime_monotonic_raw,"
           "%.4f,%.4f,%.4f,%.4f,%.4f,%.4f,%.4f,,bench_oqs_percentiles.c,\n",
           g_ts, g_host, g_label, lib, libver, g_impl, alg, op, msg_bytes, n, warm,
           (double)s[0] / 1e3, pct(s, n, 50) / 1e3, mean / 1e3, pct(s, n, 90) / 1e3, pct(s, n, 99) / 1e3,
           (double)s[n - 1] / 1e3, sd / 1e3);
    fflush(stdout);
}

static size_t choose_n(double probe_us, size_t n_fast, size_t n_mid, size_t n_slow) {
    if (probe_us <= 100.0) return n_fast;
    if (probe_us <= 1000.0) return n_mid;
    return n_slow;
}

static void bench_kem(const char *alg, size_t n_fast, size_t n_mid, size_t n_slow, size_t warm) {
    OQS_KEM *kem = OQS_KEM_new(alg);
    if (!kem) { fprintf(stderr, "KEM %s not enabled in this liboqs build; skipping\n", alg); return; }
    uint8_t *pk = malloc(kem->length_public_key), *sk = malloc(kem->length_secret_key);
    uint8_t *ct = malloc(kem->length_ciphertext), *ss = malloc(kem->length_shared_secret), *ss2 = malloc(kem->length_shared_secret);
    if (OQS_KEM_keypair(kem, pk, sk) != OQS_SUCCESS) { fprintf(stderr, "keypair failed\n"); exit(1); }
    /* probe one encaps+decaps to pick n */
    uint64_t t0 = now_ns(); OQS_KEM_encaps(kem, ct, ss, pk); OQS_KEM_decaps(kem, ss2, ct, sk); double probe_us = (now_ns() - t0) / 1e3;
    size_t n = choose_n(probe_us, n_fast, n_mid, n_slow), w = probe_us > 1000.0 ? warm / 10 + 1 : warm;
    uint64_t *s = malloc(n * sizeof(uint64_t));
    const char *ver = OQS_version();

    for (size_t i = 0; i < w; i++) OQS_KEM_keypair(kem, pk, sk);
    for (size_t i = 0; i < n; i++) { uint64_t a = now_ns(); OQS_KEM_keypair(kem, pk, sk); s[i] = now_ns() - a; }
    report("liboqs", ver, alg, "keygen", 0, w, s, n);

    for (size_t i = 0; i < w; i++) OQS_KEM_encaps(kem, ct, ss, pk);
    for (size_t i = 0; i < n; i++) { uint64_t a = now_ns(); OQS_KEM_encaps(kem, ct, ss, pk); s[i] = now_ns() - a; }
    report("liboqs", ver, alg, "encaps", 0, w, s, n);

    for (size_t i = 0; i < w; i++) OQS_KEM_decaps(kem, ss2, ct, sk);
    for (size_t i = 0; i < n; i++) { uint64_t a = now_ns(); OQS_KEM_decaps(kem, ss2, ct, sk); s[i] = now_ns() - a; }
    if (memcmp(ss, ss2, kem->length_shared_secret) != 0) { fprintf(stderr, "%s: shared secret mismatch!\n", alg); exit(1); }
    report("liboqs", ver, alg, "decaps", 0, w, s, n);

    for (size_t i = 0; i < n; i++) { uint64_t a = now_ns(); OQS_KEM_encaps(kem, ct, ss, pk); OQS_KEM_decaps(kem, ss2, ct, sk); s[i] = now_ns() - a; }
    report("liboqs", ver, alg, "encaps_decaps", 0, w, s, n);

    free(s); free(pk); free(sk); free(ct); free(ss); free(ss2); OQS_KEM_free(kem);
}

static void bench_sig(const char *alg, size_t n_fast, size_t n_mid, size_t n_slow, size_t warm) {
    OQS_SIG *sig = OQS_SIG_new(alg);
    if (!sig) { fprintf(stderr, "SIG %s not enabled; skipping\n", alg); return; }
    uint8_t *pk = malloc(sig->length_public_key), *sk = malloc(sig->length_secret_key), *sm = malloc(sig->length_signature);
    size_t smlen = 0; uint8_t msg[29]; RAND_bytes(msg, sizeof msg);   /* 29 B = nonce+ct+tag of the AEAD object */
    if (OQS_SIG_keypair(sig, pk, sk) != OQS_SUCCESS) { fprintf(stderr, "sig keypair failed\n"); exit(1); }
    uint64_t t0 = now_ns(); OQS_SIG_sign(sig, sm, &smlen, msg, sizeof msg, sk); double probe_us = (now_ns() - t0) / 1e3;
    size_t n = choose_n(probe_us, n_fast, n_mid, n_slow); if (n < 20000) n = 20000;   /* rejection-loop tail: >= 2e4 samples */
    uint64_t *s = malloc(n * sizeof(uint64_t));
    const char *ver = OQS_version();

    for (size_t i = 0; i < warm; i++) OQS_SIG_keypair(sig, pk, sk);
    for (size_t i = 0; i < n; i++) { uint64_t a = now_ns(); OQS_SIG_keypair(sig, pk, sk); s[i] = now_ns() - a; }
    report("liboqs", ver, alg, "keygen", 0, warm, s, n);

    for (size_t i = 0; i < warm; i++) OQS_SIG_sign(sig, sm, &smlen, msg, sizeof msg, sk);
    for (size_t i = 0; i < n; i++) { uint64_t a = now_ns(); OQS_SIG_sign(sig, sm, &smlen, msg, sizeof msg, sk); s[i] = now_ns() - a; }
    report("liboqs", ver, alg, "sign", sizeof msg, warm, s, n);

    for (size_t i = 0; i < warm; i++) OQS_SIG_verify(sig, msg, sizeof msg, sm, smlen, pk);
    for (size_t i = 0; i < n; i++) {
        uint64_t a = now_ns();
        if (OQS_SIG_verify(sig, msg, sizeof msg, sm, smlen, pk) != OQS_SUCCESS) { fprintf(stderr, "verify failed\n"); exit(1); }
        s[i] = now_ns() - a;
    }
    report("liboqs", ver, alg, "verify", sizeof msg, warm, s, n);

    free(s); free(pk); free(sk); free(sm); OQS_SIG_free(sig);
}

static void bench_aead(int keybits, size_t msg_bytes, size_t n, size_t warm) {
    /* msg_bytes = 1: the actual QRQT AEAD payload (two correction bits stored in one byte, plus the
       12-byte nonce and 16-byte tag on the wire = 29 B); msg_bytes = 16: one full AES block, the usual
       microbenchmark reference. Each call = full init + update + final with a fresh nonce, i.e. the
       per-round cost; no key schedule caching across rounds. */
    const EVP_CIPHER *c = keybits == 128 ? EVP_aes_128_gcm() : EVP_aes_256_gcm();
    uint8_t key[32], iv[12], pt[16], ct[16], tag[16], out[16];
    RAND_bytes(key, 32); RAND_bytes(iv, 12); RAND_bytes(pt, 16);
    EVP_CIPHER_CTX *e = EVP_CIPHER_CTX_new(), *d = EVP_CIPHER_CTX_new(); int len = 0;
    const int mb = (int)msg_bytes;
    uint64_t *s = malloc(n * sizeof(uint64_t)); char alg[24]; snprintf(alg, sizeof alg, "AES-%d-GCM", keybits);
#define AEAD_ENC() do { EVP_EncryptInit_ex(e, c, NULL, key, iv); EVP_EncryptUpdate(e, ct, &len, pt, mb); EVP_EncryptFinal_ex(e, ct + len, &len); EVP_CIPHER_CTX_ctrl(e, EVP_CTRL_GCM_GET_TAG, 16, tag); iv[0]++; } while (0)
#define AEAD_DEC() do { EVP_DecryptInit_ex(d, c, NULL, key, iv); EVP_DecryptUpdate(d, out, &len, ct, mb); EVP_CIPHER_CTX_ctrl(d, EVP_CTRL_GCM_SET_TAG, 16, tag); EVP_DecryptFinal_ex(d, out + len, &len); } while (0)
    for (size_t i = 0; i < warm; i++) AEAD_ENC();
    for (size_t i = 0; i < n; i++) { uint64_t a = now_ns(); AEAD_ENC(); s[i] = now_ns() - a; }
    report("openssl", OPENSSL_VERSION_TEXT, alg, "aead_encrypt", msg_bytes, warm, s, n);
    iv[0]--;                     /* decrypt the last ciphertext/tag pair produced above */
    for (size_t i = 0; i < warm; i++) AEAD_DEC();
    for (size_t i = 0; i < n; i++) { uint64_t a = now_ns(); AEAD_DEC(); s[i] = now_ns() - a; }
    report("openssl", OPENSSL_VERSION_TEXT, alg, "aead_decrypt", msg_bytes, warm, s, n);
    free(s); EVP_CIPHER_CTX_free(e); EVP_CIPHER_CTX_free(d);
#undef AEAD_ENC
#undef AEAD_DEC
}

int main(int argc, char **argv) {
    size_t n_fast = 100000, n_mid = 20000, n_slow = 5000, warm = 1000; int no_sig = 0;
    const char *kems[32] = {0}, *sigs[8] = {0}; int nk = 0, ns = 0;
    for (int i = 1; i < argc; i++) {
        if (!strcmp(argv[i], "--no-sig")) no_sig = 1;
        else if (!strcmp(argv[i], "--n-fast") && i + 1 < argc) n_fast = strtoull(argv[++i], 0, 10);
        else if (!strcmp(argv[i], "--n-mid") && i + 1 < argc) n_mid = strtoull(argv[++i], 0, 10);
        else if (!strcmp(argv[i], "--n-slow") && i + 1 < argc) n_slow = strtoull(argv[++i], 0, 10);
        else if (!strcmp(argv[i], "--warm") && i + 1 < argc) warm = strtoull(argv[++i], 0, 10);
        else if (!strcmp(argv[i], "--label") && i + 1 < argc) g_label = argv[++i];
        else if (!strcmp(argv[i], "--impl") && i + 1 < argc) g_impl = argv[++i];
        else if (!strcmp(argv[i], "--host") && i + 1 < argc) g_host = argv[++i];
        else if (!strcmp(argv[i], "--kem") && i + 1 < argc && nk < 31) kems[nk++] = argv[++i];
        else if (!strcmp(argv[i], "--sig") && i + 1 < argc && ns < 7) sigs[ns++] = argv[++i];
        else {
            fprintf(stderr, "usage: %s [--n-fast N] [--n-mid N] [--n-slow N] [--warm N] [--label L] "
                            "[--impl avx2|generic|neon] [--host H] [--kem ALG]... [--sig ALG]...\n", argv[0]);
            return 2;
        }
    }
    time_t t = time(NULL); strftime(g_ts, sizeof g_ts, "%Y-%m-%dT%H:%M:%SZ", gmtime(&t));
    OQS_init();
    fprintf(stderr, "liboqs %s, label=%s impl=%s\n", OQS_version(), g_label, g_impl);
    printf("timestamp_utc,host_id,hardware_class,cpu_model,freq_state,core_pinned,os,library,library_version,"
           "implementation,algorithm,operation,message_bytes,n_reps,warmup_reps,timing_method,min_us,p50_us,"
           "mean_us,p90_us,p99_us,max_us,stdev_us,tsc_ticks_mean,source,notes\n");

    { /* timer/empty-region baseline: what a zero-cost operation measures as */
        uint64_t *s = malloc(n_fast * sizeof(uint64_t));
        for (size_t i = 0; i < n_fast; i++) { uint64_t a = now_ns(); __asm__ volatile("" ::: "memory"); s[i] = now_ns() - a; }
        report("harness", "c11", "none", "timer_overhead", 0, 0, s, n_fast); free(s);
    }
    bench_aead(128, 1, n_fast, warm);    /* the QRQT payload: 1 byte */
    bench_aead(128, 16, n_fast, warm);   /* one-block reference */
    bench_aead(256, 1, n_fast, warm);
    bench_aead(256, 16, n_fast, warm);
    const char **kl = nk ? kems : DEFAULT_KEMS; for (int i = 0; kl[i]; i++) bench_kem(kl[i], n_fast, n_mid, n_slow, warm);
    if (!no_sig) { const char **sl = ns ? sigs : DEFAULT_SIGS; for (int i = 0; sl[i]; i++) bench_sig(sl[i], n_fast, n_mid, n_slow, warm); }
    OQS_destroy();
    return 0;
}

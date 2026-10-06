#!/usr/bin/env python3
"""
toy_rsa_keys.py - generate small "toy" RSA key pairs for classroom demonstration.

NOT SECURE. Each modulus n = p*q has exactly five decimal digits (10000..99999),
so anyone can factor it by trial division in well under a second.

Key-generation rules follow the textbook / FIPS 186-5 pattern, scaled down:
  * p, q distinct primes
  * e odd, gcd(e, lcm(p-1, q-1)) = 1
  * d = e^(-1) mod lcm(p-1, q-1)
Extra classroom rules (not from any standard):
  * all 25 moduli are different
  * d != e (so the private key never looks identical to the public key)
Every key is checked by encrypting and decrypting EVERY message m, 0 <= m < n.

Usage:  python3 toy_rsa_keys.py [count] [seed]
        count defaults to 25; give a seed to get the same list again.
Output: toy_rsa_keys.csv  (full table for the instructor)
        prints a table to the screen
"""
import csv, math, random, sys

COUNT = int(sys.argv[1]) if len(sys.argv) > 1 else 25
rng = random.Random(int(sys.argv[2])) if len(sys.argv) > 2 else random.SystemRandom()

def is_prime(k):
    if k < 2:
        return False
    for f in range(2, math.isqrt(k) + 1):
        if k % f == 0:
            return False
    return True

PRIMES = [k for k in range(11, 1000) if is_prime(k)]   # candidate p, q
E_CHOICES = [3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37]   # small odd public exponents

keys, used_n = [], set()
while len(keys) < COUNT:
    p, q = rng.sample(PRIMES, 2)
    n = p * q
    if not (10000 <= n <= 99999) or n in used_n:
        continue
    lam = math.lcm(p - 1, q - 1)
    e = rng.choice(E_CHOICES)
    if math.gcd(e, lam) != 1:
        continue
    d = pow(e, -1, lam)
    if d == e:
        continue
    # exhaustive check: decryption undoes encryption for every possible message
    assert all(pow(pow(m, e, n), d, n) == m for m in range(n)), (p, q, e, d)
    used_n.add(n)
    keys.append(dict(student=len(keys) + 1, n=n, e=e, d=d, p=min(p, q), q=max(p, q), lcm=lam))

with open("toy_rsa_keys.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=["student", "n", "e", "d", "p", "q", "lcm"])
    w.writeheader()
    w.writerows(keys)

print(f"{'#':>3} {'n':>6} {'e':>3} {'d':>6} {'p':>4} {'q':>4}")
for k in keys:
    print(f"{k['student']:>3} {k['n']:>6} {k['e']:>3} {k['d']:>6} {k['p']:>4} {k['q']:>4}")
print(f"\nAll {COUNT} keys verified for every message 0..n-1. Saved to toy_rsa_keys.csv")

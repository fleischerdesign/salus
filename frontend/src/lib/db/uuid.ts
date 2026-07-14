/**
 * UUIDv7 generator — time-ordered, lexicographically sortable.
 *
 * Layout (128 bits):
 *   48 bits: Unix timestamp (milliseconds)
 *    4 bits: Version (7)
 *   12 bits: rand_a
 *    2 bits: Variant (10xxxxxx)
 *   62 bits: rand_b
 *
 * Matches the backend `uuid7_str()` in `src/salus/services/_helpers.py`.
 */
export function uuid7(): string {
  const msec = Date.now() & 0xffffffffffff;

  const randABytes = new Uint8Array(2);
  crypto.getRandomValues(randABytes);
  const randA = ((randABytes[0] << 8) | randABytes[1]) & 0x0fff;

  const randBBytes = new Uint8Array(8);
  crypto.getRandomValues(randBBytes);
  const randBHigh =
    ((randBBytes[0] & 0x3f) << 24) | (randBBytes[1] << 16) | (randBBytes[2] << 8) | randBBytes[3];
  const randBLow =
    (randBBytes[4] << 24) | (randBBytes[5] << 16) | (randBBytes[6] << 8) | randBBytes[7];

  const uuidInt =
    (BigInt(msec) << 80n) |
    (7n << 76n) |
    (BigInt(randA) << 64n) |
    (0x2n << 62n) |
    (BigInt(randBHigh) << 32n) |
    BigInt(randBLow > 0 ? randBLow : randBLow + 0x100000000);

  const h = uuidInt.toString(16).padStart(32, '0');
  return `${h.slice(0, 8)}-${h.slice(8, 12)}-${h.slice(12, 16)}-${h.slice(16, 20)}-${h.slice(20)}`;
}

export function erf(x: number): number {
  const a1 = 0.254829592;
  const a2 = -0.284496736;
  const a3 = 1.421413741;
  const a4 = -1.453152027;
  const a5 = 1.061405429;
  const p = 0.3275911;
  const sign = x >= 0 ? 1 : -1;
  const absX = Math.abs(x);
  const t = 1.0 / (1.0 + p * absX);
  const y = 1.0 - ((((a5 * t + a4) * t + a3) * t + a2) * t + a1) * t * Math.exp(-absX * absX);
  return sign * y;
}

export function normalCdf(x: number, mu: number = 0.0, sigma: number = 1.0): number {
  return 0.5 * (1.0 + erf((x - mu) / (sigma * Math.SQRT2)));
}

/* eslint-disable no-loss-of-precision */
export function normalPpf(p: number, mu: number = 0.0, sigma: number = 1.0): number {
  if (p <= 0.0) return mu - 8.0 * sigma;
  if (p >= 1.0) return mu + 8.0 * sigma;
  const q = p - 0.5;
  let val: number;
  if (Math.abs(q) <= 0.425) {
    const r = 0.180625 - q * q;
    const n1 =
      ((((((2.5090809287301227 * r + 3.3430575583588128) * r + 2.8552776325268367) * r +
        0.8294365569840007) *
        r -
        0.4388077510967782) *
        r +
        7.7042991422985281) *
        r -
        6.88641701529193005) *
        r +
      2.97484026004410406;
    const d1 =
      (((((((r + 7.7454501427834149) * r + 5.3920148871494961) * r + 1.9761736431147009) * r +
        0.3650846015943261) *
        r +
        0.0214978367432659) *
        r +
        0.0002886126848307) *
        r +
        0.0000001412367643) *
        r +
      1.0;
    val = (q * n1) / d1;
  } else {
    let r = Math.sqrt(-Math.log(Math.min(p, 1.0 - p)));
    if (r <= 5.0) {
      r -= 1.6;
      val =
        ((((((((7.745450142783414e-4 * r + 2.272384498926918e-2) * r + 2.417807251774506e-1) * r +
          1.270458252452368) *
          r +
          3.647848324763204) *
          r +
          5.769497221460691) *
          r +
          4.630337846156545) *
          r +
          1.423437110749683) /
          (((((((1.050750071644416e-9 * r + 5.475938084995343e-4) * r + 1.519866656361645e-2) * r -
            5.388854303969645e-5) *
            r -
            7.48529735699477e-1) *
            r -
            3.764753314822978) *
            r -
            5.025785832006775) *
            r -
            2.011638695399458)) *
          r +
        1.0;
    } else {
      r -= 5.0;
      val =
        (((((((2.010334399292288e-7 * r + 2.711555568743487e-5) * r + 1.242660947388078e-3) * r +
          2.653218952657612e-2) *
          r +
          2.965605718285048e-1) *
          r +
          1.784826539917291) *
          r +
          5.463784911164114) *
          r +
          6.657904643501103) /
        (((((((2.044263103389939e-15 * r + 1.421511758316445e-7) * r + 1.846318317510054e-5) * r +
          7.868691311456132e-4) *
          r +
          1.487536129085061e-2) *
          r +
          1.369298809227358e-1) *
          r +
          5.998322065558879e-1) *
          r +
          1.0);
    }
  }
  if (q < 0) val = -val;
  return mu + sigma * val;
}
/* eslint-enable no-loss-of-precision */

const LANCZOS_G = 7;
const LANCZOS_P: readonly number[] = [
  0.99999999999980993, 676.5203681218851, -1259.1392167224028, 771.32342877765313,
  -176.61502916214059, 12.507343278686905, -0.13857109526572012, 9.9843695780195716e-6,
  1.5056327351493116e-7
];

export function lnGamma(x: number): number {
  if (x <= 0) throw new Error('ln_gamma undefined for x <= 0');
  let y = x;
  if (y < 0.5) {
    return Math.log(Math.PI) - Math.log(Math.sin(Math.PI * y)) - lnGamma(1.0 - y);
  }
  y -= 1.0;
  const base = y + LANCZOS_G + 0.5;
  let s = LANCZOS_P[0];
  for (let i = 1; i < LANCZOS_P.length; i++) {
    s += LANCZOS_P[i] / (y + i);
  }
  return Math.log(Math.sqrt(2.0 * Math.PI)) + (y + 0.5) * Math.log(base) - base + Math.log(s);
}

function lentzCF(a: number, b: number, x: number, maxIter: number = 200): number {
  const tiny = 1.0e-30;
  let f = 1.0;
  let c = 1.0;
  let d = 1.0 - ((a + b) * x) / (a + 1.0);
  if (Math.abs(d) < tiny) d = tiny;
  d = 1.0 / d;
  f = d;
  for (let m = 1; m <= maxIter; m++) {
    const mm = 2 * m;
    const aa = (m * (b - m) * x) / ((a + mm - 1.0) * (a + mm));
    d = 1.0 + aa * d;
    if (Math.abs(d) < tiny) d = tiny;
    c = 1.0 + aa / c;
    if (Math.abs(c) < tiny) c = tiny;
    d = 1.0 / d;
    f *= c * d;
    const aa2 = (-(a + m) * (a + b + m) * x) / ((a + mm) * (a + mm + 1.0));
    d = 1.0 + aa2 * d;
    if (Math.abs(d) < tiny) d = tiny;
    c = 1.0 + aa2 / c;
    if (Math.abs(c) < tiny) c = tiny;
    d = 1.0 / d;
    const delta = c * d;
    f *= delta;
    if (Math.abs(delta - 1.0) < 1.0e-15) break;
  }
  return f;
}

export function incompleteBeta(a: number, b: number, x: number): number {
  if (x < 0.0 || x > 1.0) throw new Error('x must be in [0, 1]');
  if (x === 0.0) return 0.0;
  if (x === 1.0) return 1.0;
  const cf = lentzCF(a, b, x);
  return (
    Math.exp(
      a * Math.log(x) +
        b * Math.log(1.0 - x) -
        Math.log(a) -
        (lnGamma(a) + lnGamma(b) - lnGamma(a + b))
    ) * cf
  );
}

export function tCdf(t: number, df: number): number {
  const x = df / (df + t * t);
  const ib = incompleteBeta(df / 2.0, 0.5, x);
  if (t >= 0) return 1.0 - 0.5 * ib;
  return 0.5 * ib;
}

export function tPpf(p: number, df: number): number {
  if (p <= 0.0) return -Infinity;
  if (p >= 1.0) return Infinity;
  if (p === 0.5) return 0.0;
  let guess: number;
  if (p <= 0.01 || 1.0 - p <= 0.01) {
    guess = normalPpf(p);
  } else {
    guess = Math.tan(Math.PI * (p - 0.5));
  }
  let lo = -1.0e6;
  let hi = 1.0e6;
  if (guess <= lo) lo = guess - 1.0;
  if (guess >= hi) hi = guess + 1.0;
  for (let iter = 0; iter < 150; iter++) {
    const fVal = tCdf(guess, df) - p;
    if (Math.abs(fVal) < 1.0e-15) break;
    if (fVal < 0) lo = guess;
    else hi = guess;
    const gVal = guess * guess;
    let tPrime = 1.0;
    if (df > 0) {
      const norm =
        Math.exp(lnGamma((df + 1.0) / 2.0) - lnGamma(df / 2.0)) / Math.sqrt(Math.PI * df);
      tPrime = norm * Math.pow(df / (df + gVal), (df + 1.0) / 2.0);
    }
    if (tPrime > 0) {
      const newton = guess - fVal / tPrime;
      if (lo <= newton && newton <= hi) {
        guess = newton;
        continue;
      }
    }
    guess = 0.5 * (lo + hi);
  }
  return guess;
}

export function xorshift64(seed: number): [number, number] {
  let s = BigInt.asIntN(64, BigInt(seed));
  s ^= s << 13n;
  s ^= s >> 7n;
  s ^= s << 17n;
  const value = Number(s & 0xffffffffffffffffn) / 0x10000000000000000;
  return [value % 1.0, Number(s)];
}

export function yuleWalkerAR1(residuals: number[]): [number, number] | null {
  const n = residuals.length;
  if (n < 2) return null;
  let num = 0.0;
  for (let t = 1; t < n; t++) num += residuals[t] * residuals[t - 1];
  let den = 0.0;
  for (let i = 0; i < n - 1; i++) den += residuals[i] * residuals[i];
  if (den === 0.0) return [0.0, 0.0];
  const phi = Math.max(-0.99, Math.min(0.99, num / den));
  let sigma2 = 0.0;
  for (let t = 1; t < n; t++) {
    sigma2 += (residuals[t] - phi * residuals[t - 1]) ** 2;
  }
  sigma2 /= n;
  return [phi, sigma2];
}

export function rank(xs: number[]): number[] {
  const indexed = xs.map((v, i) => ({ v, i })).sort((a, b) => a.v - b.v);
  const result = new Array<number>(xs.length);
  let i = 0;
  while (i < indexed.length) {
    let j = i;
    while (j < indexed.length && indexed[j].v === indexed[i].v) j++;
    const avgRank = (i + j - 1) / 2.0 + 1.0;
    for (let k = i; k < j; k++) result[indexed[k].i] = avgRank;
    i = j;
  }
  return result;
}

export function quantile(xs: number[], p: number): number | null {
  if (xs.length === 0 || p <= 0.0 || p > 1.0) return null;
  const n = xs.length;
  if (n === 1) return xs[0];
  const sorted = [...xs].sort((a, b) => a - b);
  const h = (n - 1) * p + 1;
  let lo = Math.floor(h) - 1;
  lo = Math.max(0, Math.min(lo, n - 1));
  const hi = lo + 1;
  if (hi >= n) return sorted[lo];
  const frac = h - Math.floor(h);
  return sorted[lo] + frac * (sorted[hi] - sorted[lo]);
}

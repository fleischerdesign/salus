import math


def erf_f(x: float) -> float:
    a1 = 0.254829592
    a2 = -0.284496736
    a3 = 1.421413741
    a4 = -1.453152027
    a5 = 1.061405429
    p = 0.3275911
    sign = 1.0 if x >= 0 else -1.0
    x = abs(x)
    t = 1.0 / (1.0 + p * x)
    y = 1.0 - (((((a5 * t + a4) * t) + a3) * t + a2) * t + a1) * t * math.exp(-x * x)
    return sign * y


def erf(x: float) -> float:
    return erf_f(x)


def normal_cdf(x: float, mu: float = 0.0, sigma: float = 1.0) -> float:
    return 0.5 * (1.0 + erf((x - mu) / (sigma * math.sqrt(2.0))))


def normal_ppf(p: float, mu: float = 0.0, sigma: float = 1.0) -> float:
    if p <= 0.0:
        return mu - 8.0 * sigma
    if p >= 1.0:
        return mu + 8.0 * sigma
    q = p - 0.5
    if abs(q) <= 0.425:
        r = 0.180625 - q * q
        val = (
            q
            * (((((((2.5090809287301227 * r + 3.3430575583588128) * r)
                 + 2.8552776325268367) * r + 0.8294365569840007) * r
                - 0.4388077510967782) * r + 7.7042991422985281) * r
                - 6.88641701529193005) * r
                + 2.97484026004410406
        ) / (
            (((((((r + 7.7454501427834149) * r + 5.3920148871494961) * r
                 + 1.9761736431147009) * r + 0.3650846015943261) * r
                + 0.0214978367432659) * r + 0.0002886126848307) * r
                + 0.0000001412367643) * r
                + 1.0
        )
    else:
        r = math.sqrt(-math.log(min(p, 1.0 - p)))
        if r <= 5.0:
            r -= 1.6
            val = (
                (((((((7.745450142783414e-4 * r + 2.272384498926918e-2) * r
                     + 2.417807251774506e-1) * r + 1.270458252452368e0) * r
                    + 3.647848324763204e0) * r + 5.769497221460691e0) * r
                    + 4.630337846156545e0) * r
                    + 1.423437110749683e0)
            ) / (
                (((((((1.050750071644416e-9 * r + 5.475938084995343e-4) * r
                     + 1.519866656361645e-2) * r - 5.388854303969645e-5) * r
                    - 7.485297356994770e-1) * r - 3.764753314822978e0) * r
                    - 5.025785832006775e0) * r
                    - 2.011638695399458e0) * r
                    + 1.0
            )
        else:
            r -= 5.0
            val = (
                (((((((2.010334399292288e-7 * r + 2.711555568743487e-5) * r
                     + 1.242660947388078e-3) * r + 2.653218952657612e-2) * r
                    + 2.965605718285048e-1) * r + 1.784826539917291e0) * r
                    + 5.463784911164114e0) * r
                    + 6.657904643501103e0)
            ) / (
                (((((((2.044263103389939e-15 * r + 1.421511758316445e-7) * r
                     + 1.846318317510054e-5) * r + 7.868691311456132e-4) * r
                    + 1.487536129085061e-2) * r + 1.369298809227358e-1) * r
                    + 5.998322065558879e-1) * r
                    + 1.0)
            )
    if q < 0:
        val = -val
    return mu + sigma * val


_LANCZOS_G = 7
_LANCZOS_P = (
    0.99999999999980993,
    676.5203681218851,
    -1259.1392167224028,
    771.32342877765313,
    -176.61502916214059,
    12.507343278686905,
    -0.13857109526572012,
    9.9843695780195716e-6,
    1.5056327351493116e-7,
)


def ln_gamma(x: float) -> float:
    if x <= 0:
        raise ValueError("ln_gamma undefined for x <= 0")
    y = x
    if y < 0.5:
        return math.log(math.pi) - math.log(math.sin(math.pi * y)) - ln_gamma(1.0 - y)
    y -= 1.0
    base = y + _LANCZOS_G + 0.5
    s = _LANCZOS_P[0]
    for i in range(1, len(_LANCZOS_P)):
        s += _LANCZOS_P[i] / (y + i)
    return math.log(math.sqrt(2.0 * math.pi)) + (y + 0.5) * math.log(base) - base + math.log(s)


def _gamma_f(x: float) -> float:
    return math.exp(ln_gamma(x))


def _beta_f(a: float, b: float) -> float:
    return math.exp(ln_gamma(a) + ln_gamma(b) - ln_gamma(a + b))


def _lentz_continued_fraction(a: float, b: float, x: float, max_iter: int = 200) -> float:
    tiny = 1.0e-30
    f = 1.0
    c = 1.0
    d = 1.0 - (a + b) * x / (a + 1.0)
    if abs(d) < tiny:
        d = tiny
    d = 1.0 / d
    f = d
    for m in range(1, max_iter + 1):
        mm = 2 * m
        aa = m * (b - m) * x / ((a + mm - 1.0) * (a + mm))
        d = 1.0 + aa * d
        if abs(d) < tiny:
            d = tiny
        c = 1.0 + aa / c
        if abs(c) < tiny:
            c = tiny
        d = 1.0 / d
        f *= c * d
        aa = -(a + m) * (a + b + m) * x / ((a + mm) * (a + mm + 1.0))
        d = 1.0 + aa * d
        if abs(d) < tiny:
            d = tiny
        c = 1.0 + aa / c
        if abs(c) < tiny:
            c = tiny
        d = 1.0 / d
        delta = c * d
        f *= delta
        if abs(delta - 1.0) < 1.0e-15:
            break
    return f


def incomplete_beta(a: float, b: float, x: float) -> float:
    if x < 0.0 or x > 1.0:
        raise ValueError("x must be in [0, 1] for incomplete_beta")
    if x == 0.0:
        return 0.0
    if x == 1.0:
        return 1.0
    cf = _lentz_continued_fraction(a, b, x)
    return math.exp(a * math.log(x) + b * math.log(1.0 - x) - math.log(a) - (ln_gamma(a) + ln_gamma(b) - ln_gamma(a + b))) * cf


def t_cdf(t: float, df: float) -> float:
    x = df / (df + t * t)
    ib = incomplete_beta(df / 2.0, 0.5, x)
    if t >= 0:
        return 1.0 - 0.5 * ib
    return 0.5 * ib


def t_ppf(p: float, df: float) -> float:
    if p <= 0.0:
        return float("-inf")
    if p >= 1.0:
        return float("inf")
    if p == 0.5:
        return 0.0
    if p <= 0.01 or (1.0 - p) <= 0.01:
        guess = normal_ppf(p)
    else:
        guess = math.tan(math.pi * (p - 0.5))
    lo = -1.0e6
    hi = 1.0e6
    if guess <= lo:
        lo = guess - 1.0
    if guess >= hi:
        hi = guess + 1.0
    for _iter in range(150):
        f_val = t_cdf(guess, df) - p
        if abs(f_val) < 1.0e-15:
            break
        if f_val < 0:
            lo = guess
        else:
            hi = guess
        g_val = guess * guess
        t_prime = 1.0
        if df > 0:
            t_prime = (df / (df + g_val)) ** ((df + 1.0) / 2.0)
            norm = (
                math.exp(ln_gamma((df + 1.0) / 2.0) - ln_gamma(df / 2.0))
                / math.sqrt(math.pi * df)
            )
            t_prime = norm * t_prime
        if t_prime > 0:
            newton = guess - f_val / t_prime
            if lo <= newton <= hi:
                guess = newton
                continue
        guess = 0.5 * (lo + hi)
    return guess


def xorshift64(seed: int) -> tuple[float, int]:
    s = seed & 0xFFFFFFFFFFFFFFFF
    s ^= (s << 13) & 0xFFFFFFFFFFFFFFFF
    s ^= (s >> 7) & 0xFFFFFFFFFFFFFFFF
    s ^= (s << 17) & 0xFFFFFFFFFFFFFFFF
    value = (s / float(0x10000000000000000)) % 1.0
    return value, s


def yule_walker_ar1(residuals: list[float]) -> tuple[float, float] | None:
    n = len(residuals)
    if n < 2:
        return None
    num = sum(residuals[t] * residuals[t - 1] for t in range(1, n))
    den = sum(r * r for r in residuals[:-1])
    if den == 0.0:
        return 0.0, 0.0
    phi = max(-0.99, min(0.99, num / den))
    sigma2 = sum((residuals[t] - phi * residuals[t - 1]) ** 2 for t in range(1, n)) / n
    return phi, sigma2


def rank(xs: list[float]) -> list[float]:
    indexed = sorted(enumerate(xs), key=lambda kv: kv[1])
    result = [0.0] * len(xs)
    i = 0
    while i < len(indexed):
        j = i
        while j < len(indexed) and indexed[j][1] == indexed[i][1]:
            j += 1
        avg_rank = (i + j - 1) / 2.0 + 1.0
        for k in range(i, j):
            result[indexed[k][0]] = avg_rank
        i = j
    return result


def quantile(xs: list[float], p: float) -> float | None:
    if not xs or p <= 0.0 or p > 1.0:
        return None
    n = len(xs)
    if n == 1:
        return xs[0]
    sorted_xs = sorted(xs)
    h = (n - 1) * p + 1
    lo = int(h) - 1
    lo = max(0, min(lo, n - 1))
    hi = lo + 1
    if hi >= n:
        return sorted_xs[lo]
    frac = h - int(h)
    return sorted_xs[lo] + frac * (sorted_xs[hi] - sorted_xs[lo])

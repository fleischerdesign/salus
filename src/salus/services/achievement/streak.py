from datetime import date, timedelta


def compute_streak(dates: list[date], today: date) -> tuple[int, int]:
    """Current and longest consecutive-day streak, anchored at ``today``.

    ``today`` is the caller's local "today" (see ADR-009) — the server's clock is
    never a valid fallback.
    """
    if not dates:
        return 0, 0
    unique = sorted(set(dates), reverse=True)
    current = 0
    expected = today
    for d in unique:
        if d == expected:
            current += 1
            expected = d - timedelta(days=1)
        elif d < expected:
            break
    longest = 1
    run = 1
    for i in range(1, len(unique)):
        if unique[i - 1] - timedelta(days=1) == unique[i]:
            run += 1
        else:
            run = 1
        if run > longest:
            longest = run
    return current, longest

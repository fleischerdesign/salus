from datetime import date, timedelta


def compute_streak(dates: list[date], today: date | None = None) -> tuple[int, int]:
    if not dates:
        return 0, 0
    today = today or date.today()
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

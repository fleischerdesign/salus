import math


def change_point_pelt(series: list[float], penalty: str = "BIC") -> dict | None:
    n = len(series)
    if n < 2:
        return None
    mean_all = sum(series) / n
    varest = sum((series[i] - mean_all) ** 2 for i in range(n)) / (n - 1) if n > 1 else 1.0
    if penalty == "BIC":
        pen = math.log(n) * varest
    else:
        pen = math.log(n) + math.log(n - 1) if n > 1 else math.log(n) * varest
    cost = [float("inf")] * (n + 1)
    cost[0] = -pen
    cp_list: list[int] = []
    last_cp = [0] * (n + 1)
    R: list[int] = []
    for t in range(1, n + 1):
        best_cost = float("inf")
        best_cp = 0
        next_R = [0]
        for s_val in (R if R else [0]):
            s = s_val
            seg_len = t - s
            if seg_len < 1:
                continue
            seg = series[s:t]
            seg_mean = sum(seg) / seg_len
            seg_cost = sum((series[i] - seg_mean) ** 2 for i in range(s, t))
            total = cost[s] + seg_cost + pen
            if total < best_cost:
                best_cost = total
                best_cp = s
            if total <= cost[t] + pen:
                next_R.append(s_val)
                if len(next_R) > 50:
                    break
        R = list(set(next_R))
        cost[t] = best_cost
        last_cp[t] = best_cp
    pos = n
    while pos > 0 and last_cp[pos] > 0:
        cp_list.append(last_cp[pos])
        pos = last_cp[pos]
    cp_list.sort()
    return {"indices": cp_list, "costs": cost}

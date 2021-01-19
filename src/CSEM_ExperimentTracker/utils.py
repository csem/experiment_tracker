import pandas as pd


def topk(series, k=5, min=True):
    target = series.sort_values().index.droplevel(-1)
    seen = set()
    return [x for x in target if not (x in seen or seen.add(x))][:k]

from typing import Dict, List

import numpy as np
import pandas as pd


def is_row_notna(df: pd.DataFrame) -> pd.Series:
    return df.notna().sum(axis=1) == len(df.columns)


def get_col_nan_statistics(data: Dict[str, pd.DataFrame]):
    metrics = dict()
    for name, df in data.items():
        if is_number(name):
            per_col_nans = df.isna().sum(axis=0)
            for column in df.columns:
                if column not in metrics:
                    metrics[column] = [per_col_nans[column]]
                else:
                    metrics[column].append(per_col_nans[column])

    metrics = pd.DataFrame(metrics)
    metrics = metrics.mean().sort_values(ascending=False)
    metrics = metrics[metrics > metrics.mean()]
    print(f'Top columns with most nan values are [(Column name, nan mean values)]:\n{metrics}')

    return metrics.index.values


def is_number(string: str) -> bool:
    try:
        int(string)
        return True
    except ValueError:
        return False


def compute_acronym(string: str) -> str:
    if not string or (not isinstance(string, str) and np.isnan(string)):
        return ''

    return ''.join(e[0] for e in string.split())


def extract_years_from(data: Dict[str, pd.DataFrame]) -> List[str]:
    years = []
    for name, df in data.items():
        if is_number(name):
            years.append(name)

    return years

import glob
import os
from typing import Dict, List

import bs4 as bs
import numpy as np
import pandas as pd
import requests


def get_sp500_tickers():
    resp = requests.get('http://en.wikipedia.org/wiki/List_of_S%26P_500_companies')
    soup = bs.BeautifulSoup(resp.text, 'lxml')
    table = soup.find('table', {'class': 'wikitable sortable'})
    tickers = []
    for row in table.findAll('tr')[1:]:
        ticker = row.findAll('td')[0].text.strip('\n ')
        tickers.append(ticker)

    return sorted(tickers)


def load_data(storage_dir: str) -> dict:
    data = dict()
    for file in glob.glob(os.path.join(storage_dir, '*.csv')):
        file_name = os.path.basename(file).split('.')[0]
        if 'prices' not in file_name:
            data[file_name] = pd.read_csv(file, index_col='Ticker')
        else:
            data['prices'] = pd.read_csv(file)

    for file_name, df in data.items():
        if is_number(file_name):
            data[file_name] = pd.concat([data[file_name], data['info']], axis=1)

    return data


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

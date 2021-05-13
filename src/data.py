import glob
import os

import bs4 as bs
import pandas as pd
import requests

from src import utils
from src.utils import is_number

FUNDAMENTALS_RENAME_MAPPINGS = {
    'year': {
        'Total Liab': 'Total Liabilities',
        'Total Current Liabilities': 'Current Liabilities',
        'Total Stockholder Equity': 'Total Equity',
        'Total Assets': 'Total Assets',
        'Total Current Assets': 'Current Assets',
        'Total Revenue': 'Revenue',
        'Gross Profit': 'Gross Profit',
        'Operating Income': 'Operating Income',
        'Net Income From Continuing Ops': 'Net Income',
        'Selling General Administrative': 'Marketing',
        'Research Development': 'Research',
        'Total Cashflows From Investing Activities': 'Investing',
        'Total Cash From Financing Activities': 'Financing'
    },
    'info': {
        'sector': 'Sector',
        'industry': 'Industry',
        'marketCap': 'Market Cap',
        'sharesOutstanding': 'Shares',
        'trailingPE': 'PE'
    }
}


def load_data(storage_dir: str) -> dict:
    data = dict()
    all_tickers = set()
    valid_data_mask = None
    for file in glob.glob(os.path.join(storage_dir, '*.csv')):
        file_name = os.path.basename(file).split('.')[0]
        if 'prices' not in file_name:
            data[file_name] = pd.read_csv(file, index_col='Ticker')
            if utils.is_number(file_name):
                data[file_name] = data[file_name].rename(columns=FUNDAMENTALS_RENAME_MAPPINGS['year'])
                all_tickers = all_tickers.union(set(data[file_name].index))
            else:
                data[file_name] = data[file_name].rename(columns=FUNDAMENTALS_RENAME_MAPPINGS[file_name])
        else:
            data['prices'] = pd.read_csv(file)

    info_data = data.pop('info')
    num_rows = len(info_data.index)
    print(f'\nThere are a total of {num_rows} entries.')

    # Add info data at fundamental data for simplicity & consistency. We want all the df, except the prices, to have
    # the same columns.
    for file_name, df in data.items():
        if is_number(file_name):
            data[file_name] = pd.concat([data[file_name], info_data], axis=1)

    # Find the columns that have too many nan values. We want to drop them, otherwise we will drop too many rows too
    # not have any nan values.
    columns_to_drop = utils.get_col_nan_statistics(data)

    # Compute valid data mask. We want to keep only rows that have all the data available.
    for file_name, df in data.items():
        if utils.is_number(file_name):
            data[file_name] = data[file_name].drop(columns=columns_to_drop)

        if 'prices' not in file_name:
            if valid_data_mask is None:
                valid_data_mask = utils.is_row_notna(data[file_name])
            else:
                valid_data_mask = valid_data_mask & utils.is_row_notna(data[file_name])

    assert all_tickers == set(valid_data_mask.index), 'The same tickers should preserve over time.'

    for file_name, df in data.items():
        # Drop rows where there are missing values.
        if 'prices' not in file_name:
            data[file_name] = data[file_name][valid_data_mask]

    return data


def get_sp500_tickers():
    resp = requests.get('http://en.wikipedia.org/wiki/List_of_S%26P_500_companies')
    soup = bs.BeautifulSoup(resp.text, 'lxml')
    table = soup.find('table', {'class': 'wikitable sortable'})
    tickers = []
    for row in table.findAll('tr')[1:]:
        ticker = row.findAll('td')[0].text.strip('\n ')
        tickers.append(ticker)

    return sorted(tickers)

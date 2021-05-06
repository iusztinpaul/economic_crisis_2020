import os
from pathlib import Path
from typing import List, Dict

import yfinance as yf
import pandas as pd

from tqdm import tqdm

from src.utils import get_sp500_tickers

EXTRACTION_TREE = {
    'balancesheet/year': (
        'Total Liab',
        'Total Current Liabilities',
        'Total Stockholder Equity',
        'Total Assets',
        'Total Current Assets'
    ),
    'financials/year': (
        'Total Revenue',
        'Gross Profit',
        'Operating Income',
        'Net Income From Continuing Ops',
        'Selling General Administrative',
        'Research Development'
    ),
    'cashflow/year': (
        'Total Cashflows From Investing Activities',
        'Total Cash From Financing Activities'
    ),
    'info': (
        'sector',
        'industry',
        'marketCap',
        'sharesOutstanding',
        'trailingPE'
    )
}


def export_csv(tickers: List[str], storage_path: str):
    Path(storage_path).mkdir(parents=True, exist_ok=True)

    data = dict()
    for ticker in tqdm(tickers):
        ticker_data = extract_data(ticker, EXTRACTION_TREE)
        for year, year_data in ticker_data.items():
            if year not in data:
                data[year] = []
            data[year].append(year_data)

    save_as_csv(data, storage_path, EXTRACTION_TREE)


def extract_data(ticker_string: str, extraction_tree: dict) -> dict:
    ticker = yf.Ticker(ticker_string)
    if ticker.balancesheet.shape[0] == 0:
        return dict()

    years = {date.strftime('%Y'): date for date in ticker.balancesheet.columns}
    extracted_data = {year: [ticker_string] for year in years}

    for attribute, rows in extraction_tree.items():
        if '/year' in attribute:
            attribute = attribute.split('/year')[0]
            df = getattr(ticker, attribute)
            for year, date_column_name in years.items():
                for row in rows:
                    try:
                        data_row = float(df.loc[row, [date_column_name]].values[0])
                    except TypeError:
                        data_row = None
                    extracted_data[year].append(data_row)
        else:
            extracted_data[attribute] = [ticker_string]
            data = getattr(ticker, attribute)
            for row in rows:
                try:
                    data_row = data[row]
                except KeyError:
                    data_row = None
                extracted_data[attribute].append(data_row)

    return extracted_data


def save_as_csv(data: Dict[str, list], storage_path: str, extraction_tree: dict):
    per_year_df_columns, df_columns = get_columns(extraction_tree)
    for file_name, file_data in data.items():
        try:
            file_name = int(file_name)
            df = pd.DataFrame(data=file_data, columns=per_year_df_columns)
        except ValueError:
            df = pd.DataFrame(data=file_data, columns=df_columns)

        df.to_csv(os.path.join(storage_path, f'{file_name}.csv'), index=False)


def get_columns(extraction_tree: dict):
    per_year_df_columns = []
    df_columns = []
    for attribute, columns in extraction_tree.items():
        if 'year' in attribute:
            per_year_df_columns.extend(columns)
        else:
            df_columns.extend(columns)

    return ['Ticker'] + per_year_df_columns, ['Ticker'] + df_columns


if __name__ == '__main__':
    tickers = get_sp500_tickers()
    export_csv(tickers, 'data/')

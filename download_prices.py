import os
from pathlib import Path
from typing import List

import yfinance as yf

from src import data


def export_prices(tickers: List[str], storage_path: str):
    Path(storage_path).mkdir(parents=True, exist_ok=True)

    data = yf.download(
        ' '.join(tickers),
        start="2017-01-01",
        end="2021-01-01",
        threads=True,
        interval='1d'
    )
    data = data.stack()
    data = data.loc[:, ['Close']]
    data = data.unstack()

    data.to_csv(os.path.join(storage_path, 'prices.csv'))


if __name__ == '__main__':
    tickers = data.get_sp500_tickers()
    export_prices(tickers, './data')

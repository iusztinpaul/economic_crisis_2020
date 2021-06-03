from typing import Dict, List

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from src import data
from src import utils


def plot_mean_prices(prices: pd.DataFrame, show=False):
    if show:
        prices.mean(axis=1).plot()

        plt.ylabel('Prices')
        plt.show()


def plot_mean_prices_by_sector(prices: pd.DataFrame, info: pd.DataFrame, ylabel='Prices', show=False):
    legend = []
    if show:
        with sns.color_palette("Set1", n_colors=len(info['Sector'].unique())):
            for sector in info['Sector'].unique():
                tickers = info[info['Sector'] == sector].index
                prices[tickers].mean(axis=1).plot()

                legend.append(sector)

        plt.ylabel(ylabel)
        plt.legend(legend)

        plt.show()


def plot_price_per_earning_by_sector(data: Dict[str, pd.DataFrame], info: pd.DataFrame, show=False):
    plot_price_per_column_by_sector(data, info, column='Net Income', show=show)


def plot_price_per_revenue_by_sector(data: Dict[str, pd.DataFrame], info: pd.DataFrame, show=False):
    plot_price_per_column_by_sector(data, info, column='Revenue', show=show)


def plot_price_per_column_by_sector(data: Dict[str, pd.DataFrame], info: pd.DataFrame, column, show=False):
    statistics_name_mapping = {
        'Net Income': 'Price/Earnings',
        'Revenue': 'Price/Sales'
    }
    statistics = statistics_name_mapping[column]

    prices = data['prices']
    price_per_earnings = pd.DataFrame(
        index=pd.MultiIndex.from_product(
            (info.index, ('2017', '2018', '2019', '2020')),
            names=('Tickers', 'Years')
        ),
        columns=('Sector', statistics),
    )
    for sector in info['Sector'].unique():
        sector_tickers = info[info['Sector'] == sector].index
        for start, end in (('2017', '2017-12-31'), ('2018', '2018-12-31'), ('2019', '2019-12-31'), ('2020', '2020-12-31')):
            year_sector_earnings = data[start].loc[sector_tickers, column]

            datetime_year_mask = prices.index.to_series().between(start, end, inclusive=True)
            last_year_prices = prices.loc[datetime_year_mask, sector_tickers].iloc[-1]
            year_sector_price_per_earnings = pd.DataFrame(
                index=pd.MultiIndex.from_product(
                    (sector_tickers, (start, )),
                    names=('Tickers', 'Years')
                ),
                columns=('Sector', statistics),
                data={
                    statistics: ((info.loc[sector_tickers, 'Shares'] * last_year_prices) / year_sector_earnings).values,
                    'Sector': sector
                }
            )

            price_per_earnings.update(year_sector_price_per_earnings)

    price_per_earnings = price_per_earnings.reset_index(level=1)
    price_per_earnings['Sector'] = price_per_earnings['Sector'].apply(utils.every_word_on_different_line)

    if show:
        sns.set(rc={'figure.figsize': (15, 10)})
        sns.barplot(
            x='Sector',
            y=statistics,
            hue='Years',
            data=price_per_earnings,
            palette='Set3',
            ci='sd'
        )
        plt.title('Higher = overpriced | Negative = no income', fontweight='bold', fontsize=20)
        plt.ylabel(statistics, fontweight='bold', fontsize=20)
        plt.tight_layout()

        plt.show()


def plot_best_performing_assets(prices: pd.DataFrame, year='2020', k=5, show=False) -> Dict[str, List[str]]:
    start = year
    end = f'{year}-12-31'
    prices = prices[prices.index.to_series().between(start, end, inclusive=True)]

    min_values_index = prices.idxmin(axis=0)
    max_values_index = prices.idxmax(axis=0)
    best_mask = min_values_index[(min_values_index < max_values_index)]
    least_mask = min_values_index[(min_values_index >= max_values_index)]
    best_performing = prices[best_mask.index]
    least_performing = prices[least_mask.index]

    best_min_values = best_performing.min(axis=0)
    best_max_values = best_performing.max(axis=0)
    best_change = (best_max_values - best_min_values) / best_min_values
    best_change = best_change.sort_values(ascending=False)
    best_change = best_change.reset_index()
    best_change.columns = ('Ticker', 'Growth %')
    best_change['Growth %'] = best_change['Growth %'] * 100
    best_performing_tickers = best_change[:k]

    least_min_values = least_performing.min(axis=0)
    least_max_values = least_performing.max(axis=0)
    least_change = (least_min_values - least_max_values) / least_max_values
    least_change = least_change.sort_values(ascending=True)
    least_change = least_change.reset_index()
    least_change.columns = ('Ticker', 'Growth %')
    least_change['Growth %'] = least_change['Growth %'] * 100
    least_performing_tickers = least_change[:k]

    if show:
        fig, axis = plt.subplots(nrows=1, ncols=2, figsize=(10, 10))
        sns.barplot(x='Ticker', y='Growth %', data=best_performing_tickers, palette='Set3', ci='sd', ax=axis[0])
        axis[0].set_title('Best performing stocks.', fontweight='bold', fontsize=20)

        sns.barplot(x='Ticker', y='Growth %', data=least_performing_tickers, palette='Set3', ci='sd', ax=axis[1])
        axis[1].set_title('Least performing stocks.', fontweight='bold', fontsize=20)

        plt.show()

    return {
        'best': list(best_performing_tickers['Ticker'].values),
        'least': list(least_performing_tickers['Ticker'].values)
    }


def plot_tickers(prices: pd.DataFrame, tickers: List[List[str]], show=False):
    if show:
        current_xticks = prices[tickers[0][0]].index

        _, axis = plt.subplots(nrows=1, ncols=len(tickers), figsize=(15, 9))
        for i, set_of_tickers in enumerate(tickers):
            for ticker in set_of_tickers:
                axis[i].plot(prices[ticker])

            axis[i].set_xticks(current_xticks[::len(current_xticks) // 5])
            axis[i].set_ylabel('Prices')
            axis[i].legend(set_of_tickers)

        plt.show()


if __name__ == '__main__':
    data, info = data.load_data('../data')

    # Plot mean prices.
    plot_mean_prices(data['prices'], show=False)
    plot_mean_prices_by_sector(data['prices'], info, show=True)

    # Plot statistics.
    plot_price_per_earning_by_sector(data, info, show=False)
    plot_price_per_revenue_by_sector(data, info, show=False)

    # Plot best & least performing tickers.
    stats_dict = plot_best_performing_assets(data['prices'], show=False)
    plot_tickers(data['prices'], tickers=[stats_dict['best'], stats_dict['least']], show=False)

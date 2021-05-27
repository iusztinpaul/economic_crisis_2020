import pandas as pd
import matplotlib.pyplot as plt

import src.data


def plot_prices(prices: pd.DataFrame):
    prices.mean(axis=1).plot()

    plt.ylabel('Prices')
    plt.show()


def plot_prices_by_sector(prices: pd.DataFrame, info: pd.DataFrame):
    legend = []
    for sector in info['Sector'].unique():
        tickers = info[info['Sector'] == sector].index
        prices[tickers].mean(axis=1).plot()

        legend.append(sector)

    plt.ylabel('Prices')
    plt.legend(legend)
    plt.show()


if __name__ == '__main__':
    data, info = src.data.load_data('../data')
    plot_prices(data['prices'])
    plot_prices_by_sector(data['prices'], info)

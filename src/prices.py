import pandas as pd
import matplotlib.pyplot as plt

import src.data


def plot_prices(prices: pd.DataFrame):
    prices = prices.mean(axis=1)
    prices.plot()

    plt.show()


if __name__ == '__main__':
    data = src.data.load_data('../data')
    plot_prices(data['prices'])

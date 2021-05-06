from typing import Dict

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn import preprocessing

import src.utils as utils


def box_plot_balance_sheet(data: Dict[str, pd.DataFrame], columns: list):
    # TODO: Find a better way to scale the values ( now it is too cluttered)
    # TODO: Find a better way to display the legend / to display the sectors

    min_max_scaler = preprocessing.MinMaxScaler()

    years = utils.extract_years_from(data)
    tickers = data['info'].index
    box_plot_columns = columns
    columns = columns + data['info'].columns.values.tolist()
    initial_sectors = None
    acronym_sectors = None

    df_data = np.zeros(shape=(0, len(columns)))
    for year in years:
        year_df = data[year].copy()
        if initial_sectors is None:
            initial_sectors = np.unique(year_df['sector'].dropna().values)
        year_df['sector'] = year_df['sector'].apply(utils.compute_acronym)
        if acronym_sectors is None:
            acronym_sectors = [utils.compute_acronym(sector) for sector in initial_sectors]
        year_df[box_plot_columns] = min_max_scaler.fit_transform(year_df[box_plot_columns].values)

        df_data = np.concatenate(
            [
                df_data,
                year_df[columns]
            ],
            axis=0
        )

    df = pd.DataFrame(
        index=pd.MultiIndex.from_product(
            iterables=[tickers, years],
            names=['ticker', 'year']
        ),
        columns=columns,
        data=df_data
    )

    # TODO: Why is this working ?
    df = df.reset_index(level=0, drop=True).sort_index().reset_index()

    for column in box_plot_columns:
        box_plot = sns.boxplot(
            x='sector',
            y=column,
            hue='year',
            data=df,
            palette='Set3'
        )
        box_plot.figure.tight_layout()
        plt.legend(labels=list(zip(initial_sectors, acronym_sectors)))
        plt.show()


if __name__ == '__main__':
    data = utils.load_data('./data')
    box_plot_balance_sheet(
        data,
        columns=['Total Liab', 'Total Stockholder Equity', 'Total Assets'],
    )



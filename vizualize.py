from typing import Dict

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

import src.data
import src.utils as utils


def box_plot_balance_sheet(data: Dict[str, pd.DataFrame], columns: list):
    # TODO: Find a better way to scale the values ( now it is too cluttered)
    # TODO: Find a better way to display the legend / to display the sectors
    # TODO: Display tickers that are outliers in the box plots.

    years = utils.extract_years_from(data)
    tickers = data['2020'].index
    box_plot_columns = columns
    columns = data['2020'].columns.values.tolist()
    sectors = None
    acronym_sectors = None

    df_data = np.zeros(shape=(0, len(columns)))
    for year in years:
        year_df = data[year].copy()
        if sectors is None:
            sectors = np.unique(year_df['Sector'].values)
        year_df['Sector'] = year_df['Sector'].apply(utils.compute_acronym)
        if acronym_sectors is None:
            acronym_sectors = [utils.compute_acronym(sector) for sector in sectors]

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
            names=['Ticker', 'Year']
        ),
        columns=columns,
        data=df_data
    )

    # Create year column.
    df = df.reset_index(level=1).sort_values(by='Year')

    for column in box_plot_columns:
        q1 = df[column].quantile(q=0.25)
        q3 = df[column].quantile(q=0.75)
        iqr = q3 - q1
        top_outliers_threshold = q3 + iqr * 1.5
        bottom_outliers_threshold = q1 - iqr * 1.5

        outliers_mask = (df[column] <= bottom_outliers_threshold) | (df[column] >= top_outliers_threshold)
        plot_df = df[~outliers_mask]
        outliers_df = df[outliers_mask]

        box_plot = sns.boxplot(
            x='Sector',
            y=column,
            hue='Year',
            data=plot_df,
            palette='Set3'
        )
        box_plot.figure.tight_layout()
        # TODO: Plot legend in a more pretty way
        # plt.legend(labels=list(zip(sectors, acronym_sectors)))
        plt.show()


if __name__ == '__main__':
    data = src.data.load_data('./data')
    box_plot_balance_sheet(
        data,
        columns=['Total Liabilities', 'Total Equity', 'Total Assets'],
    )



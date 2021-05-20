import os
from typing import Dict

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

import src.data
import src.utils as utils


def box_plot_balance_sheet(data: Dict[str, pd.DataFrame], columns: list):
    years = utils.extract_years_from(data)
    tickers = data['2020'].index
    box_plot_columns = columns
    columns = data['2020'].columns.values.tolist()

    df_data = np.zeros(shape=(0, len(columns)))
    for year in years:
        year_df = data[year].copy()
        year_df['Sector'] = year_df['Sector'].apply(utils.every_word_on_different_line)

        # TODO: This piece of code is NOT OK. data is mixed up --> take as point of reference Sectors.
        df_data = np.concatenate(
            [
                df_data,
                year_df[columns].values
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
    df = df.reset_index(level=1).reset_index().sort_values(by=['Ticker', 'Year'])
    df = df.set_index('Ticker')

    sns.set(rc={'figure.figsize': (15, 10)})
    for column in box_plot_columns:
        column_2020_df = df[df['Year'] == '2020'][column]
        q1 = column_2020_df.quantile(q=0.25)
        q3 = column_2020_df.quantile(q=0.75)
        iqr = q3 - q1
        top_outliers_threshold = q3 + iqr * 1.5

        outliers_mask = column_2020_df >= top_outliers_threshold
        outliers_tickers = set(column_2020_df[outliers_mask].index)
        outliers_df = df.loc[outliers_tickers]

        sns.barplot(
            x='Sector',
            y=column,
            hue='Year',
            data=df,
            palette='Set3'
        )
        plt.show()

        sns.barplot(
            x='Sector',
            y=column,
            hue='Year',
            data=outliers_df,
            palette='Set3'
        )
        plt.show()


if __name__ == '__main__':
    # TODO: Solve concat bug.
    # TODO: Plots for Cash Flow & Balance Sheet
    # TODO: Plot Revenue & Net Earnings relative to the stock price in time
    # TODO: See other types of plots

    storage_path = os.path.join(os.path.dirname(__file__), '..', 'data')
    data = src.data.load_data(storage_path)
    box_plot_balance_sheet(
        data,
        columns=['Revenue']
    )
    # box_plot_balance_sheet(
    #     data,
    #     columns=['Total Liabilities', 'Total Equity', 'Total Assets'],
    # )

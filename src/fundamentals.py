import os
from typing import Dict

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from src import data
from src import utils


def plot_sectors(data: Dict[str, pd.DataFrame], columns: list, show_barplot: bool = False, show_outliers: bool = False):
    years = utils.extract_years_from(data)
    tickers = data['2020'].index
    box_plot_columns = columns
    columns = data['2020'].columns.values.tolist()

    df = pd.DataFrame(
        index=pd.MultiIndex.from_product(
            iterables=[tickers, years],
            names=['Ticker', 'Year']
        ),
        columns=columns,
    )
    for year in years:
        year_df = data[year].copy()
        year_df['Sector'] = year_df['Sector'].apply(utils.every_word_on_different_line)
        year_df['Year'] = year
        year_df = year_df.set_index('Year', append=True)

        df.update(year_df)

    # Create year column.
    df = df.reset_index(level=1).reset_index().sort_values(by=['Ticker', 'Year'])
    df = df.set_index('Ticker')

    all_sectors = df['Sector'].unique()
    sns.set(rc={'figure.figsize': (20, 10)})
    outliers = {column: dict() for column in box_plot_columns}
    for column in box_plot_columns:
        column_2020_df = df[df['Year'] == '2020'][column]
        q1 = column_2020_df.quantile(q=0.25)
        q3 = column_2020_df.quantile(q=0.75)
        iqr = q3 - q1
        if q1 >= 0:
            top_outliers_threshold = q3 + iqr * 1.5
            top_outliers_mask = column_2020_df >= top_outliers_threshold
        else:
            # It means that the data has a negative trend. There will be the outliers of interest.
            top_outliers_threshold = q1 - iqr * 1.5
            top_outliers_mask = column_2020_df <= top_outliers_threshold

        top_outliers_tickers = column_2020_df[top_outliers_mask].index.unique()
        top_outliers_df = df.loc[top_outliers_tickers]
        top_outliers_count = top_outliers_df.groupby('Sector').count()[column]
        outliers[column]['tickers'] = set(top_outliers_tickers.values)
        outliers[column]['count'] = top_outliers_count

        if show_barplot:
            sns.barplot(
                x='Sector',
                y=column,
                hue='Year',
                data=df,
                palette='Set3',
                order=all_sectors,
                ci='sd',
            )
            plt.title('All', fontweight='bold', fontsize=20)
            plt.ylabel(column, fontweight='bold', fontsize=20)
            plt.tight_layout()
            plt.show()

            sns.barplot(
                x='Sector',
                y=column,
                hue='Year',
                data=top_outliers_df,
                palette='Set3',
                order=all_sectors,
                ci='sd',
            )
            plt.title('Top outliers', fontweight='bold', fontsize=20)
            plt.ylabel(column, fontweight='bold', fontsize=20)
            plt.tight_layout()
            plt.show()

    if show_outliers:
        qualitative_colors = sns.color_palette("Set3", 10)
        color_mappings = {
            'Communication\nServices': qualitative_colors[0],
            'Consumer\nCyclical': qualitative_colors[1],
            'Consumer\nDefensive': qualitative_colors[2],
            'Energy': qualitative_colors[3],
            'Financial\nServices': qualitative_colors[4],
            'Healthcare': qualitative_colors[5],
            'Industrials': qualitative_colors[6],
            'Technology': qualitative_colors[7],
            'Basic\nMaterials': qualitative_colors[8],
            'Utilities': qualitative_colors[9]
        }
        fig, ax = plt.subplots(nrows=1, ncols=len(box_plot_columns))
        for i, column in enumerate(box_plot_columns):
            outliers[column]['count'] = outliers[column]['count'].sort_index()
            colors = [color_mappings[sector] for sector in outliers[column]['count'].index.values]
            ax[i].pie(
                outliers[column]['count'],
                startangle=90,
                wedgeprops={'edgecolor': 'black'},
                shadow=True,
                radius=1.2,
                labels=outliers[column]['count'].index,
                colors=colors,
                explode=[0.0125 for _ in range(len(outliers[column]['count'].index))]
            )
            ax[i].axis('equal')
            ax[i].set_title(column, fontweight='bold', fontsize=20)

        plt.tight_layout()
        plt.show()

    return outliers


if __name__ == '__main__':
    storage_path = os.path.join(os.path.dirname(__file__), '', '../data')
    data, info = data.load_data(storage_path)

    income_statement_outliers = plot_sectors(
        data,
        columns=['Revenue', 'Net Income'],
        show_barplot=True,
        show_outliers=True
    )
    balance_sheet_outliers = plot_sectors(
        data,
        columns=['Total Liabilities', 'Total Equity', 'Total Assets'],
        show_barplot=False,
        show_outliers=False
    )
    cash_flow_outliers = plot_sectors(
        data,
        columns=['Investing', 'Financing'],
        show_barplot=False,
        show_outliers=False
    )

import pandas as pd
import numpy as np

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_54/training_0.csv", index_col=0)

grouped = df0.groupby('msno')['date_diff'].agg(
    date_diff='mean',
    date_diff_min='min',
    date_diff_max='max',
    date_diff_median='median',
    date_diff_std='std'
).reset_index()

grouped['date_diff_min'] = grouped['date_diff_min'].astype(int)
grouped['date_diff_max'] = grouped['date_diff_max'].astype(int)
grouped['date_diff_median'] = grouped['date_diff_median'].astype(int)
grouped['date_diff_std'] = grouped['date_diff_std'].fillna(0).round().astype(int)

grouped.rename(columns={
    'date_diff_min': 'date_diff-min',
    'date_diff_max': 'date_diff-max',
    'date_diff_median': 'date_diff-median',
    'date_diff_std': 'date_diff-std'
}, inplace=True)

grouped.to_csv("autopipeline-benchmarks/github-pipelines/length5_54/target_multisource_mcts.csv", index=False)
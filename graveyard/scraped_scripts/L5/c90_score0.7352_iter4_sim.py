import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_90/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_90/training_1.csv", index_col=0)

merged = pd.merge(df0, df1, how='inner', left_on='city', right_on='city')

agg = merged.groupby(['city', 'type'], as_index=False).agg(
    **{
        'Average Fare': ('fare', 'mean'),
        'ride_id': ('ride_id', 'mean'),
        'Total Number of Rides': ('ride_id', 'count'),
        'Total Number of Drivers': ('driver_count', 'sum')
    }
)

agg = agg.rename(columns={'type': 'City Type'})

agg['Total Number of Rides'] = agg['Total Number of Rides'].astype(int)
agg['Total Number of Drivers'] = agg['Total Number of Drivers'].astype(int)

agg.to_csv("autopipeline-benchmarks/github-pipelines/length5_90/target_multisource_mcts.csv", index=False)
import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_73/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_73/training_1.csv", index_col=0)

merged = pd.merge(df0, df1, on='city', how='inner')

agg = merged.groupby(['city', 'type']).agg(
    **{
        'Average Fare ($)': ('fare', 'mean'),
        'Number of Rides': ('ride_id', 'count'),
        'Number of Drivers': ('driver_count', 'sum')
    }
).reset_index()

agg = agg.rename(columns={
    'city': 'City',
    'type': 'City Type'
})

agg['Number of Drivers'] = agg['Number of Drivers'].astype('Int64')

agg.to_csv("autopipeline-benchmarks/github-pipelines/length4_73/target_multisource_mcts.csv", index=False)
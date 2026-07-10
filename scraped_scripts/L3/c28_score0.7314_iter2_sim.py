import pandas as pd

df0 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length3_28/training_0.csv', index_col=0)
df1 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length3_28/training_1.csv', index_col=0)

union_result = df0.copy()

merged = pd.merge(union_result, df1, on='city')

grouped = merged.groupby(['city', 'type'], as_index=False).agg(
    driver_count=('driver_count', 'sum'),
    Average_Fare=('fare', 'mean'),
    Ride_Count=('ride_id', 'count')
)

grouped = grouped.rename(columns={
    'Average_Fare': 'Average Fare',
    'Ride_Count': 'Ride Count'
})

grouped.to_csv('autopipeline-benchmarks/github-pipelines/length3_28/target_multisource_mcts.csv', index=False)
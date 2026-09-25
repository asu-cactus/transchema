import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_44/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_44/training_1.csv", index_col=0)

df0_unpivot = df0.copy()
df0_unpivot['type'] = 'Urban'
df0_unpivot_grouped = df0_unpivot.groupby(['city', 'type']).agg(
    **{
        'Ride Count': ('ride_id', 'count'),
        'Average Fare': ('fare', 'mean')
    }
).reset_index()

df_merged = pd.merge(df0_unpivot_grouped, df1, on=['city', 'type'], how='inner')

df_merged = df_merged[['city', 'driver_count', 'type', 'Average Fare', 'Ride Count']]

df_merged.to_csv("autopipeline-benchmarks/github-pipelines/length3_44/target_multisource_mcts.csv", index=False)
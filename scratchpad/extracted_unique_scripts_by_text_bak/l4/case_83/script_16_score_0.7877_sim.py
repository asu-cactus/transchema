import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_83/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_83/training_1.csv", index_col=0)

unpivot_rows = []
for _, row in source1.iterrows():
    unpivot_rows.append({'city': row['city'], 'driver_count': row['driver_count'], 'type': row['type']})
unpivot_df = pd.DataFrame(unpivot_rows)

joined = pd.merge(unpivot_df, source0, on='city', how='inner')

grouped = joined.groupby(['city', 'driver_count', 'type'], as_index=False).agg(average_fare=('fare', 'mean'))

grouped['driver_count'] = grouped['driver_count'].astype(int)
grouped['city'] = grouped['city'].astype(str)
grouped['type'] = grouped['type'].astype(str)
grouped['average_fare'] = grouped['average_fare'].astype(float)

grouped.to_csv("autopipeline-benchmarks/github-pipelines/length4_83/target_multisource_mcts.csv", index=False)
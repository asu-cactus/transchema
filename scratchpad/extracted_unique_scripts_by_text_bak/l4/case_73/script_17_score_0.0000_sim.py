import pandas as pd
import numpy as np
from scipy import stats

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_73/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_73/training_1.csv", index_col=0)

df0['fare'] = pd.to_numeric(df0['fare'], errors='coerce')
df0['ride_id'] = df0['ride_id'].astype(str)
df1['driver_count'] = pd.to_numeric(df1['driver_count'], errors='coerce')
df1['type'] = df1['type'].astype(str)

merged = pd.merge(df0, df1, on='city', how='inner')

grouped = merged.groupby('city').agg(
    min_fare = ('fare', 'min'),
    count_rides = ('ride_id', 'count'),
    min_driver_count = ('driver_count', 'min'),
    max_driver_count = ('driver_count', 'max'),
    mode_type = (lambda x: stats.mode(x)[0][0])
)

grouped['Number of Drivers'] = ((grouped['min_driver_count'] + grouped['max_driver_count']) / 2).round().astype('Int64')

result = pd.DataFrame({
    'City': grouped.index,
    'Average Fare ($)': grouped['min_fare'].astype(float),
    'Number of Rides': grouped['count_rides'].astype(float),
    'Number of Drivers': grouped['Number of Drivers'],
    'City Type': grouped['mode_type'].astype(str)
})

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_73/target_multisource_mcts.csv", index=False)
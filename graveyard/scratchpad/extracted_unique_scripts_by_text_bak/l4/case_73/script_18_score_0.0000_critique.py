import pandas as pd
from scipy import stats

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_73/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_73/training_1.csv", index_col=0)

df0['fare'] = pd.to_numeric(df0['fare'], errors='coerce')
df0['ride_id'] = df0['ride_id'].astype(str)
df1['driver_count'] = pd.to_numeric(df1['driver_count'], errors='coerce')
df1['type'] = df1['type'].astype(str)

merged = pd.merge(df0, df1, on='city', how='inner')

grouped = merged.groupby('city').agg(
    avg_fare = ('fare', 'mean'),
    num_rides = ('ride_id', 'count'),
    num_drivers = ('driver_count', 'max'),
    city_type = ('type', lambda x: stats.mode(x)[0][0])
)

result = pd.DataFrame({
    'City': grouped.index,
    'Average Fare ($)': grouped['avg_fare'].astype(float),
    'Number of Rides': grouped['num_rides'].astype(float),
    'Number of Drivers': grouped['num_drivers'].astype('Int64'),
    'City Type': grouped['city_type'].astype(str)
})

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_73/target_multisource_mcts.csv", index=False)
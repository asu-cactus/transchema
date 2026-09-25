import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_72/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_72/training_1.csv", index_col=0)

# Join on city
joined = pd.merge(source0, source1, on='city', how='inner')

# Aggregate over entire joined data (no group by)
result = pd.DataFrame({
    'type': [joined['type'].mode().iloc[0] if not joined['type'].mode().empty else joined['type'].iloc[0]],
    'fare': [joined['fare'].sum()],
    'ride_id': [joined['ride_id'].count()],
    'driver_count': [joined['driver_count'].sum()]
})

result.to_csv("autopipeline-benchmarks/github-pipelines/length2_72/target_multisource_mcts.csv", index=False)
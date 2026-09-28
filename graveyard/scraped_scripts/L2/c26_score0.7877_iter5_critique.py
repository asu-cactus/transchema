import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_26/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_26/training_1.csv", index_col=0)

# Convert 'time' to hour (integer)
source1['time'] = pd.to_datetime(source1['time'], errors='coerce').dt.hour

# Fill NaN in 'bet' and 'win' with 0 and convert to int
source1[['bet', 'win']] = source1[['bet', 'win']].fillna(0).astype(int)

# Merge on 'user_id' (inner join)
merged = pd.merge(source1, source0, on='user_id', how='inner')

# Convert 'email' and 'geo' to string lengths
merged['email'] = merged['email'].astype(str).str.len()
merged['geo'] = merged['geo'].astype(str).str.len()

# Group by 'user_id' and aggregate
result = merged.groupby('user_id').agg(
    time=('time', 'count'),  # count of rows per user_id
    bet=('bet', 'sum'),
    win=('win', 'sum'),
    email=('email', 'max'),  # user attribute, max or min is fine
    geo=('geo', 'max')
).reset_index()

result.to_csv("autopipeline-benchmarks/github-pipelines/length2_26/target_multisource_mcts.csv", index=False)
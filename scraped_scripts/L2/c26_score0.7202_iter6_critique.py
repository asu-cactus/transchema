import pandas as pd

src0_path = "autopipeline-benchmarks/github-pipelines/length2_26/training_0.csv"
src1_path = "autopipeline-benchmarks/github-pipelines/length2_26/training_1.csv"
target_path = "autopipeline-benchmarks/github-pipelines/length2_26/target_multisource_mcts.csv"

df0 = pd.read_csv(src0_path, index_col=0)
df1 = pd.read_csv(src1_path, index_col=0)

# Convert 'time' to datetime, then keep original values for aggregation of distinct counts
df1['time'] = pd.to_datetime(df1['time'], errors='coerce')

# Convert bet and win to numeric, fill NaN with 0
df1['bet'] = pd.to_numeric(df1['bet'], errors='coerce').fillna(0).astype(int)
df1['win'] = pd.to_numeric(df1['win'], errors='coerce').fillna(0).astype(int)

# Join on user_id
merged = pd.merge(df1, df0, on='user_id', how='inner')

# Group by user_id and aggregate
agg_df = merged.groupby('user_id').agg(
    time=('time', lambda x: x.nunique()),  # count distinct times per user
    bet=('bet', 'sum'),
    win=('win', 'sum'),
    email=('email', lambda x: x.nunique()),  # count distinct emails per user
    geo=('geo', lambda x: x.nunique())       # count distinct geos per user
).reset_index()

# Convert all columns except user_id to int (target schema expects integers)
agg_df['time'] = agg_df['time'].astype(int)
agg_df['bet'] = agg_df['bet'].astype(int)
agg_df['win'] = agg_df['win'].astype(int)
agg_df['email'] = agg_df['email'].astype(int)
agg_df['geo'] = agg_df['geo'].astype(int)

agg_df.to_csv(target_path, index=False)
import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_22/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_22/training_1.csv", index_col=0)

# Join on First Room = Room to keep only classes in rooms listed in df1
joined = pd.merge(df0, df1, left_on="First Room", right_on="Room", how="inner")

# Group by Department and Term, sum Reg Count
grouped = joined.groupby(['Department', 'Term'], as_index=False)['Reg Count'].sum()

# Pivot Term to columns
pivoted = grouped.pivot(index='Department', columns='Term', values='Reg Count').fillna(0)

# Convert columns to string to match target schema
pivoted.columns = pivoted.columns.astype(str)

result = pivoted.reset_index()

# Ensure all target term columns exist
for col in ['20153', '20161', '20162']:
    if col not in result.columns:
        result[col] = 0.0

# Select and order columns exactly as target schema
result = result[['Department', '20153', '20161', '20162']]

# Convert term columns to float
result[['20153', '20161', '20162']] = result[['20153', '20161', '20162']].astype(float)

result.to_csv("autopipeline-benchmarks/github-pipelines/length3_22/target_multisource_mcts.csv", index=False)
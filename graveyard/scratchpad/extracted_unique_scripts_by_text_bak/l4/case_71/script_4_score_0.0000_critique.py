import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_71/training_0.csv", index_col=0)

cols_target = ['Name', 'Age', 'G', 'MP', 'FG', 'FGA', '3P', '3PA', 'FT', 'FTA', 'ORB', 'TRB', 'AST', 'STL', 'BLK', 'TOV', 'PF', 'PTS', 'FG%', '3P%', 'FT%', 'MP.1', 'PTS.1', 'TRB.1', 'AST.1']

# Group by 'Name' and aggregate other columns by mean
df_grouped = df0.groupby('Name', as_index=False)[cols_target[1:]].mean()

# Add 'Name' column back
df_result = pd.concat([df0[['Name']].drop_duplicates().reset_index(drop=True), df_grouped], axis=1)

# The above concat duplicates 'Name' column, so better to just do:
# Actually, groupby with as_index=False keeps 'Name' column, so just use df_grouped directly

df_result = df0.groupby('Name', as_index=False)[cols_target[1:]].mean()
df_result.insert(0, 'Name', df_result.pop('Name'))  # Ensure 'Name' is first column

# But groupby with as_index=False already keeps 'Name' as first column, so no need to insert

# Reorder columns exactly as in target schema
df_result = df_result[cols_target]

df_result.to_csv("autopipeline-benchmarks/github-pipelines/length4_71/target_multisource_mcts.csv", index=False)
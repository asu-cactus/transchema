import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_79/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_79/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_79/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_79/training_3.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_79/training_4.csv", index_col=0)

join_23 = pd.merge(s2, s3, on="hero", suffixes=('_2', '_3'))
join_01 = pd.merge(s0, s1, on="hero", suffixes=('_0', '_1'))

# For union, columns must be aligned and same schema as target:
# The join results have duplicated columns with suffixes, so we need to reshape them to the target schema:
# The target schema is ['hero', 'disadvantage', 'winrate', 'matches']

# Extract columns from join_23: hero, disadvantage_2, winrate_2, matches_2 and hero, disadvantage_3, winrate_3, matches_3
# We want to stack these two sets vertically (unpivot)
df_23_part1 = join_23[['hero', 'disadvantage_2', 'winrate_2', 'matches_2']].rename(
    columns={'disadvantage_2': 'disadvantage', 'winrate_2': 'winrate', 'matches_2': 'matches'})
df_23_part2 = join_23[['hero', 'disadvantage_3', 'winrate_3', 'matches_3']].rename(
    columns={'disadvantage_3': 'disadvantage', 'winrate_3': 'winrate', 'matches_3': 'matches'})
df_23_unpivoted = pd.concat([df_23_part1, df_23_part2], ignore_index=True)

# Similarly for join_01:
df_01_part1 = join_01[['hero', 'disadvantage_0', 'winrate_0', 'matches_0']].rename(
    columns={'disadvantage_0': 'disadvantage', 'winrate_0': 'winrate', 'matches_0': 'matches'})
df_01_part2 = join_01[['hero', 'disadvantage_1', 'winrate_1', 'matches_1']].rename(
    columns={'disadvantage_1': 'disadvantage', 'winrate_1': 'winrate', 'matches_1': 'matches'})
df_01_unpivoted = pd.concat([df_01_part1, df_01_part2], ignore_index=True)

# s4 already matches target schema
df_all = pd.concat([df_01_unpivoted, df_23_unpivoted, s4], ignore_index=True)

# Ensure correct dtypes
df_all['hero'] = df_all['hero'].astype(str)
df_all['disadvantage'] = pd.to_numeric(df_all['disadvantage'], errors='coerce')
df_all['winrate'] = pd.to_numeric(df_all['winrate'], errors='coerce')
df_all['matches'] = pd.to_numeric(df_all['matches'], errors='coerce').astype('Int64')

df_all.to_csv("autopipeline-benchmarks/github-pipelines/length4_79/target_multisource_mcts.csv", index=False)
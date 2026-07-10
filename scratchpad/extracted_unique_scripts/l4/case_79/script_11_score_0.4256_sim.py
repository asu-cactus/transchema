import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_79/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_79/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_79/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_79/training_3.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_79/training_4.csv", index_col=0)

join_0 = pd.merge(s2, s3, on="hero", suffixes=('_2', '_3'))
join_1 = pd.merge(s0, s4, on="hero", suffixes=('_0', '_4'))

union_1 = pd.concat([join_1, s1], ignore_index=True, sort=False)
union_2 = pd.concat([union_1, join_0], ignore_index=True, sort=False)

grouped = union_2.groupby("hero", as_index=False).agg({
    'disadvantage_0': 'sum' if 'disadvantage_0' in union_2 else 'sum',
    'disadvantage_2': 'sum' if 'disadvantage_2' in union_2 else 'sum',
    'disadvantage_3': 'sum' if 'disadvantage_3' in union_2 else 'sum',
    'disadvantage_4': 'sum' if 'disadvantage_4' in union_2 else 'sum',
    'disadvantage': 'sum' if 'disadvantage' in union_2 else 'sum',
    'winrate_0': 'sum' if 'winrate_0' in union_2 else 'sum',
    'winrate_2': 'sum' if 'winrate_2' in union_2 else 'sum',
    'winrate_3': 'sum' if 'winrate_3' in union_2 else 'sum',
    'winrate_4': 'sum' if 'winrate_4' in union_2 else 'sum',
    'winrate': 'sum' if 'winrate' in union_2 else 'sum',
    'matches_0': 'sum' if 'matches_0' in union_2 else 'sum',
    'matches_2': 'sum' if 'matches_2' in union_2 else 'sum',
    'matches_3': 'sum' if 'matches_3' in union_2 else 'sum',
    'matches_4': 'sum' if 'matches_4' in union_2 else 'sum',
    'matches': 'sum' if 'matches' in union_2 else 'sum',
})

# Because columns have suffixes, sum all disadvantage columns, winrate columns weighted by matches, and matches columns
# We need to handle columns carefully

# Extract columns by suffix
disadv_cols = [c for c in grouped.columns if c.startswith('disadvantage')]
winrate_cols = [c for c in grouped.columns if c.startswith('winrate')]
matches_cols = [c for c in grouped.columns if c.startswith('matches')]

# If original columns without suffix exist, include them
if 'disadvantage' in grouped.columns:
    disadv_cols.append('disadvantage')
if 'winrate' in grouped.columns:
    winrate_cols.append('winrate')
if 'matches' in grouped.columns:
    matches_cols.append('matches')

# Sum matches
grouped['matches'] = grouped[matches_cols].sum(axis=1)

# Calculate weighted average winrate
winrate_weighted_sum = 0
for wcol, mcol in zip(winrate_cols, matches_cols):
    winrate_weighted_sum += grouped[wcol] * grouped[mcol]
grouped['winrate'] = winrate_weighted_sum / grouped['matches']
grouped['winrate'] = grouped['winrate'].fillna(0)

# Sum disadvantage weighted by matches as well (assuming disadvantage is also weighted)
disadv_weighted_sum = 0
for dcol, mcol in zip(disadv_cols, matches_cols):
    disadv_weighted_sum += grouped[dcol] * grouped[mcol]
grouped['disadvantage'] = disadv_weighted_sum / grouped['matches']
grouped['disadvantage'] = grouped['disadvantage'].fillna(0)

result = grouped[['hero', 'disadvantage', 'winrate', 'matches']]

result['hero'] = result['hero'].astype(str)
result['disadvantage'] = result['disadvantage'].astype(float)
result['winrate'] = result['winrate'].astype(float)
result['matches'] = result['matches'].astype(int)

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_79/target_multisource_mcts.csv", index=False)
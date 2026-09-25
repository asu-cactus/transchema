import pandas as pd

paths = [
    "autopipeline-benchmarks/github-pipelines/length5_37/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length5_37/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length5_37/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length5_37/training_3.csv",
    "autopipeline-benchmarks/github-pipelines/length5_37/training_4.csv",
    "autopipeline-benchmarks/github-pipelines/length5_37/training_5.csv"
]

dfs = [pd.read_csv(p, index_col=0) for p in paths]

df = pd.concat(dfs, ignore_index=True)

# Define group by columns (leftmost key columns)
group_by_cols = ['tourney_id', 'tourney_name', 'surface', 'draw_size', 'tourney_level', 'tourney_date', 'match_num', 'winner_id']

# All columns in df
all_cols = df.columns.tolist()

# Columns to aggregate (all except group_by_cols)
agg_cols = [col for col in all_cols if col not in group_by_cols]

# Define aggregation dict: use 'first' to preserve values
agg_dict = {col: 'first' for col in agg_cols}

df = df.groupby(group_by_cols, dropna=False, as_index=False).agg(agg_dict)

# Enforce target schema types explicitly
df = df.astype({
    'tourney_id': str,
    'tourney_name': str,
    'surface': str,
    'draw_size': 'Int64',
    'tourney_level': str,
    'tourney_date': 'Int64',
    'match_num': 'Int64',
    'winner_id': 'Int64',
    'winner_seed': 'float64',
    'winner_entry': str,
    'winner_name': str,
    'winner_hand': str,
    'winner_ht': 'float64',
    'winner_ioc': str,
    'winner_age': 'float64',
    'winner_rank': 'float64',
    'winner_rank_points': 'float64',
    'loser_id': 'Int64',
    'loser_seed': 'float64',
    'loser_entry': str,
    'loser_name': str,
    'loser_hand': str,
    'loser_ht': 'float64',
    'loser_ioc': str,
    'loser_age': 'float64',
    'loser_rank': 'float64',
    'loser_rank_points': 'float64',
    'score': str,
    'best_of': 'Int64',
    'round': str,
    'minutes': 'float64',
    'w_ace': 'float64',
    'w_df': 'float64',
    'w_svpt': 'float64',
    'w_1stIn': 'float64',
    'w_1stWon': 'float64',
    'w_2ndWon': 'float64',
    'w_SvGms': 'float64',
    'w_bpSaved': 'float64',
    'w_bpFaced': 'float64',
    'l_ace': 'float64',
    'l_df': 'float64',
    'l_svpt': 'float64',
    'l_1stIn': 'float64',
    'l_1stWon': 'float64',
    'l_2ndWon': 'float64',
    'l_SvGms': 'float64',
    'l_bpSaved': 'float64',
    'l_bpFaced': 'float64'
}, errors='ignore')

df.to_csv("autopipeline-benchmarks/github-pipelines/length5_37/target_multisource_mcts.csv", index=False)
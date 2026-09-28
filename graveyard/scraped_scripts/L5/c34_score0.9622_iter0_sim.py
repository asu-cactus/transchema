import pandas as pd

paths = [
    "autopipeline-benchmarks/github-pipelines/length5_34/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length5_34/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length5_34/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length5_34/training_3.csv",
    "autopipeline-benchmarks/github-pipelines/length5_34/training_4.csv",
    "autopipeline-benchmarks/github-pipelines/length5_34/training_5.csv"
]

dfs = [pd.read_csv(p, index_col=0) for p in paths]

df = pd.concat(dfs, ignore_index=True)

# Enforce target schema dtypes
df['tourney_id'] = df['tourney_id'].astype(str)
df['tourney_name'] = df['tourney_name'].astype(str)
df['surface'] = df['surface'].astype(str)
df['draw_size'] = pd.to_numeric(df['draw_size'], errors='coerce').astype('Int64')
df['tourney_level'] = df['tourney_level'].astype(str)
df['tourney_date'] = pd.to_numeric(df['tourney_date'], errors='coerce').astype('Int64')
df['match_num'] = pd.to_numeric(df['match_num'], errors='coerce').astype('Int64')
df['winner_id'] = pd.to_numeric(df['winner_id'], errors='coerce').astype('Int64')
df['winner_seed'] = pd.to_numeric(df['winner_seed'], errors='coerce').astype(float)
df['winner_entry'] = df['winner_entry'].astype(str).replace({'nan': None})
df['winner_name'] = df['winner_name'].astype(str)
df['winner_hand'] = df['winner_hand'].astype(str)
df['winner_ht'] = pd.to_numeric(df['winner_ht'], errors='coerce').astype(float)
df['winner_ioc'] = df['winner_ioc'].astype(str)
df['winner_age'] = pd.to_numeric(df['winner_age'], errors='coerce').astype(float)
df['winner_rank'] = pd.to_numeric(df['winner_rank'], errors='coerce').astype(float)
df['winner_rank_points'] = pd.to_numeric(df['winner_rank_points'], errors='coerce').astype(float)
df['loser_id'] = pd.to_numeric(df['loser_id'], errors='coerce').astype('Int64')
df['loser_seed'] = pd.to_numeric(df['loser_seed'], errors='coerce').astype(float)
df['loser_entry'] = df['loser_entry'].astype(str).replace({'nan': None})
df['loser_name'] = df['loser_name'].astype(str)
df['loser_hand'] = df['loser_hand'].astype(str)
df['loser_ht'] = pd.to_numeric(df['loser_ht'], errors='coerce').astype(float)
df['loser_ioc'] = df['loser_ioc'].astype(str)
df['loser_age'] = pd.to_numeric(df['loser_age'], errors='coerce').astype(float)
df['loser_rank'] = pd.to_numeric(df['loser_rank'], errors='coerce').astype(float)
df['loser_rank_points'] = pd.to_numeric(df['loser_rank_points'], errors='coerce').astype(float)
df['score'] = df['score'].astype(str)
df['best_of'] = pd.to_numeric(df['best_of'], errors='coerce').astype('Int64')
df['round'] = df['round'].astype(str)
df['minutes'] = pd.to_numeric(df['minutes'], errors='coerce').astype(float)
df['w_ace'] = pd.to_numeric(df['w_ace'], errors='coerce').astype(float)
df['w_df'] = pd.to_numeric(df['w_df'], errors='coerce').astype(float)
df['w_svpt'] = pd.to_numeric(df['w_svpt'], errors='coerce').astype(float)
df['w_1stIn'] = pd.to_numeric(df['w_1stIn'], errors='coerce').astype(float)
df['w_1stWon'] = pd.to_numeric(df['w_1stWon'], errors='coerce').astype(float)
df['w_2ndWon'] = pd.to_numeric(df['w_2ndWon'], errors='coerce').astype(float)
df['w_SvGms'] = pd.to_numeric(df['w_SvGms'], errors='coerce').astype(float)
df['w_bpSaved'] = pd.to_numeric(df['w_bpSaved'], errors='coerce').astype(float)
df['w_bpFaced'] = pd.to_numeric(df['w_bpFaced'], errors='coerce').astype(float)
df['l_ace'] = pd.to_numeric(df['l_ace'], errors='coerce').astype(float)
df['l_df'] = pd.to_numeric(df['l_df'], errors='coerce').astype(float)
df['l_svpt'] = pd.to_numeric(df['l_svpt'], errors='coerce').astype(float)
df['l_1stIn'] = pd.to_numeric(df['l_1stIn'], errors='coerce').astype(float)
df['l_1stWon'] = pd.to_numeric(df['l_1stWon'], errors='coerce').astype(float)
df['l_2ndWon'] = pd.to_numeric(df['l_2ndWon'], errors='coerce').astype(float)
df['l_SvGms'] = pd.to_numeric(df['l_SvGms'], errors='coerce').astype(float)
df['l_bpSaved'] = pd.to_numeric(df['l_bpSaved'], errors='coerce').astype(float)
df['l_bpFaced'] = pd.to_numeric(df['l_bpFaced'], errors='coerce').astype(float)

df.to_csv("autopipeline-benchmarks/github-pipelines/length5_34/target_multisource_mcts.csv", index=False)
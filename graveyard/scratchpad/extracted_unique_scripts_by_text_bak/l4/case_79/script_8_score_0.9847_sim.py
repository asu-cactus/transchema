import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_79/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_79/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_79/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_79/training_3.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_79/training_4.csv", index_col=0)

join_result = pd.merge(s2, s3, on="hero", suffixes=('_2', '_3'))

union_0_1_4 = pd.concat([s0, s1, s4], ignore_index=True)

# The join_result has duplicated columns for disadvantage, winrate, matches from s2 and s3.
# We need to unpivot these columns to match the target schema.
# The target schema expects one row per hero with columns: hero, disadvantage, winrate, matches.
# Since join_result has columns: hero, disadvantage_2, winrate_2, matches_2, disadvantage_3, winrate_3, matches_3
# We unpivot disadvantage, winrate, matches from the two sources into rows.

unpivot_cols = ['disadvantage', 'winrate', 'matches']
df_list = []
for suffix in ['_2', '_3']:
    df_temp = join_result[['hero'] + [col + suffix for col in unpivot_cols]].copy()
    df_temp.columns = ['hero'] + unpivot_cols
    df_list.append(df_temp)
unpivoted = pd.concat(df_list, ignore_index=True)

final_df = pd.concat([union_0_1_4, unpivoted], ignore_index=True)

final_df['hero'] = final_df['hero'].astype(str)
final_df['disadvantage'] = final_df['disadvantage'].astype(float)
final_df['winrate'] = final_df['winrate'].astype(float)
final_df['matches'] = final_df['matches'].astype(int)

final_df.to_csv("autopipeline-benchmarks/github-pipelines/length4_79/target_multisource_mcts.csv", index=False)
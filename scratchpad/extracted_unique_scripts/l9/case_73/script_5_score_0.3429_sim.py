import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_73/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_73/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_73/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_73/training_3.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_73/training_4.csv", index_col=0)
s5 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_73/training_5.csv", index_col=0)
s6 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_73/training_6.csv", index_col=0)
s7 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_73/training_7.csv", index_col=0)
s8 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_73/training_8.csv", index_col=0)
s9 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_73/training_9.csv", index_col=0)

join_0 = pd.merge(s5, s0, left_on="sampled_bid_id", right_on="bid_id", how="inner")
union_1 = pd.concat([s1, s2, s3, s4, s6, s7, s8, s9], ignore_index=True)
join_1 = pd.merge(join_0[['bid_id', 'message']], union_1[['bid_id', 'pii_cleaned_message']], on='bid_id', how='inner')

join_0_sel = join_0[['bid_id', 'message']]
join_1_sel = join_1[['bid_id', 'pii_cleaned_message']].rename(columns={'pii_cleaned_message': 'message'})

final_df = pd.concat([join_0_sel, join_1_sel], ignore_index=True)
final_df['bid_id'] = final_df['bid_id'].astype(int)
final_df['message'] = final_df['message'].astype(str)

final_df.to_csv("autopipeline-benchmarks/github-pipelines/length9_73/target_multisource_mcts.csv", index=False)
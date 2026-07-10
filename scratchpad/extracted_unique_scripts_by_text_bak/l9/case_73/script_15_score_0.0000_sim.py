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

join_result = pd.merge(s6, s0, on="bid_id", how="inner", suffixes=('_6', '_0'))
join_result = join_result[["bid_id", "pii_cleaned_message_0"]].rename(columns={"pii_cleaned_message_0": "message"})

union_sources = [s1, s2, s3, s4, s5, s7, s8, s9]
union_list = []
for df in union_sources:
    if 'pii_cleaned_message' in df.columns:
        union_list.append(df[["bid_id", "pii_cleaned_message"]].rename(columns={"pii_cleaned_message": "message"}))
    elif 'message' in df.columns:
        # Source 5 has 'message' column instead of 'pii_cleaned_message'
        union_list.append(df[["sampled_bid_id", "message"]].rename(columns={"sampled_bid_id": "bid_id"}))
    else:
        # If any source does not have message or pii_cleaned_message, skip (not expected here)
        pass

union_result = pd.concat(union_list, ignore_index=True)

final_df = pd.concat([join_result, union_result], ignore_index=True)

final_df = final_df[["bid_id", "message"]]

final_df.to_csv("autopipeline-benchmarks/github-pipelines/length9_73/target_multisource_mcts.csv", index=False)
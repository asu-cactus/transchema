import pandas as pd

# Read all sources
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

# Prepare list for union
union_list = []

# Sources 0,1,2,3,4,6,7,8,9 have 'bid_id' and 'pii_cleaned_message'
for df in [s0, s1, s2, s3, s4, s6, s7, s8, s9]:
    # Select only needed columns and rename pii_cleaned_message to message
    union_list.append(df[["bid_id", "pii_cleaned_message"]].rename(columns={"pii_cleaned_message": "message"}))

# Source 5 has 'sampled_bid_id' and 'message'
union_list.append(s5[["sampled_bid_id", "message"]].rename(columns={"sampled_bid_id": "bid_id"}))

# Concatenate all
all_data = pd.concat(union_list, ignore_index=True)

# Group by bid_id and take the first non-null message per bid_id
# This ensures one message per bid_id as in target
final_df = all_data.dropna(subset=["bid_id", "message"])  # drop rows with missing keys or messages

# Convert bid_id to int (target schema is integer)
final_df["bid_id"] = final_df["bid_id"].astype(int)

# Group by bid_id and take first message (stable)
final_df = final_df.groupby("bid_id", as_index=False).agg({"message": "first"})

# Write output
final_df.to_csv("autopipeline-benchmarks/github-pipelines/length9_73/target_multisource_mcts.csv", index=False)
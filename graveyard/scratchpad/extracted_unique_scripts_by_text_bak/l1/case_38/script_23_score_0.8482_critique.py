import pandas as pd
import glob

# Read all source CSV files matching the pattern in the folder
file_pattern = "autopipeline-benchmarks/github-pipelines/length1_38/training_*.csv"
all_files = glob.glob(file_pattern)

# Read and concatenate all source tables (union)
df_list = [pd.read_csv(f, index_col=0) for f in all_files]
df_all = pd.concat(df_list, ignore_index=True)

# Group by user_id and aggregate mean of sad.depressed and open.stressed
agg_df = df_all.groupby("user_id").agg({
    "sad.depressed": "mean",
    "open.stressed": "mean"
}).reset_index()

# Rename columns to match target schema
agg_df = agg_df.rename(columns={
    "sad.depressed": "sad",
    "open.stressed": "stressed"
})

# Write output
agg_df.to_csv("autopipeline-benchmarks/github-pipelines/length1_38/target_multisource_mcts.csv", index=False)
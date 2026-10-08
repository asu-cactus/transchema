import pandas as pd
import glob

# Load and process all source CSV files
sources = glob.glob("autopipeline-benchmarks/github-pipelines/length1_80/training_*.csv")

# Read all sources into a single DataFrame
all_data = []
for source in sources:
    df = pd.read_csv(source, index_col=0)
    all_data.append(df)

# Combine all sources using UNION
combined_df = pd.concat(all_data, ignore_index=True)

# GROUP BY and AGGREGATE
final_df = combined_df.groupby("movieId")["rating"].mean().reset_index()

# Save to target CSV
final_df.to_csv("autopipeline-benchmarks/github-pipelines/length1_80/target_multisource_mcts_recovery_test_val.csv", index=False)
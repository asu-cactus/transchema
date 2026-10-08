import pandas as pd

paths = {
    "Source9_59_0": "autopipeline-benchmarks/github-pipelines/length9_59/training_0.csv",
    "Source9_59_1": "autopipeline-benchmarks/github-pipelines/length9_59/training_1.csv",
    "Source9_59_2": "autopipeline-benchmarks/github-pipelines/length9_59/training_2.csv",
    "Source9_59_3": "autopipeline-benchmarks/github-pipelines/length9_59/training_3.csv",
    "Source9_59_5": "autopipeline-benchmarks/github-pipelines/length9_59/training_5.csv",
    "Source9_59_6": "autopipeline-benchmarks/github-pipelines/length9_59/training_6.csv",
    "Source9_59_7": "autopipeline-benchmarks/github-pipelines/length9_59/training_7.csv",
    "Source9_59_8": "autopipeline-benchmarks/github-pipelines/length9_59/training_8.csv",
    "Source9_59_9": "autopipeline-benchmarks/github-pipelines/length9_59/training_9.csv",
    "Source9_59_10": "autopipeline-benchmarks/github-pipelines/length9_59/training_10.csv",
    "Source9_59_11": "autopipeline-benchmarks/github-pipelines/length9_59/training_11.csv",
    "Source9_59_12": "autopipeline-benchmarks/github-pipelines/length9_59/training_12.csv",
    "Source9_59_15": "autopipeline-benchmarks/github-pipelines/length9_59/training_15.csv",
    "Source9_59_16": "autopipeline-benchmarks/github-pipelines/length9_59/training_16.csv",
}

df_7 = pd.read_csv(paths["Source9_59_7"], index_col=0)
df_0 = pd.read_csv(paths["Source9_59_0"], index_col=0)

joined_7_0 = pd.merge(df_7, df_0, on="country", suffixes=('_7', '_0'))

# After join, keep only 'country' and 'cpi_7' (or 'cpi_0') as cpi, since target schema is ['country', 'cpi']
# We choose cpi_7 as cpi (from Source9_59_7) because Source9_59_7 has different cpi values (float with decimals)
joined_7_0 = joined_7_0[['country', 'cpi_7']].rename(columns={'cpi_7': 'cpi'})

# Load all other sources for union (excluding Source9_59_4 and Source9_59_13 and Source9_59_14 which are not in union list)
union_sources = [
    "Source9_59_0", "Source9_59_1", "Source9_59_2", "Source9_59_3",
    "Source9_59_5", "Source9_59_6", "Source9_59_8", "Source9_59_9",
    "Source9_59_10", "Source9_59_11", "Source9_59_12", "Source9_59_15", "Source9_59_16"
]

dfs_union = []
for src in union_sources:
    df = pd.read_csv(paths[src], index_col=0)
    dfs_union.append(df)

union_df = pd.concat(dfs_union, ignore_index=True)

# Combine the join result with the union result
final_df = pd.concat([joined_7_0, union_df], ignore_index=True)

# Ensure columns are exactly ['country', 'cpi'] and types match target schema
final_df = final_df[['country', 'cpi']]
final_df['country'] = final_df['country'].astype(str)
final_df['cpi'] = final_df['cpi'].astype(float)

final_df.to_csv("autopipeline-benchmarks/github-pipelines/length9_59/target_multisource_mcts.csv", index=False)
import pandas as pd

paths = {
    "Source9_59_0": "autopipeline-benchmarks/github-pipelines/length9_59/training_0.csv",
    "Source9_59_1": "autopipeline-benchmarks/github-pipelines/length9_59/training_1.csv",
    "Source9_59_2": "autopipeline-benchmarks/github-pipelines/length9_59/training_2.csv",
    "Source9_59_3": "autopipeline-benchmarks/github-pipelines/length9_59/training_3.csv",
    "Source9_59_4": "autopipeline-benchmarks/github-pipelines/length9_59/training_4.csv",
    "Source9_59_5": "autopipeline-benchmarks/github-pipelines/length9_59/training_5.csv",
    "Source9_59_6": "autopipeline-benchmarks/github-pipelines/length9_59/training_6.csv",
    "Source9_59_7": "autopipeline-benchmarks/github-pipelines/length9_59/training_7.csv",
    "Source9_59_8": "autopipeline-benchmarks/github-pipelines/length9_59/training_8.csv",
    "Source9_59_9": "autopipeline-benchmarks/github-pipelines/length9_59/training_9.csv",
    "Source9_59_10": "autopipeline-benchmarks/github-pipelines/length9_59/training_10.csv",
    "Source9_59_11": "autopipeline-benchmarks/github-pipelines/length9_59/training_11.csv",
    "Source9_59_12": "autopipeline-benchmarks/github-pipelines/length9_59/training_12.csv",
    "Source9_59_13": "autopipeline-benchmarks/github-pipelines/length9_59/training_13.csv",
    "Source9_59_14": "autopipeline-benchmarks/github-pipelines/length9_59/training_14.csv",
    "Source9_59_15": "autopipeline-benchmarks/github-pipelines/length9_59/training_15.csv",
    "Source9_59_16": "autopipeline-benchmarks/github-pipelines/length9_59/training_16.csv",
}

df_13 = pd.read_csv(paths["Source9_59_13"], index_col=0)
df_10 = pd.read_csv(paths["Source9_59_10"], index_col=0)
joined_13_10 = pd.merge(df_13, df_10, on="country", suffixes=('_13', '_10'))

# After join, keep 'country' and average 'cpi' from both sources to unify
joined_13_10['cpi'] = joined_13_10[['cpi_13', 'cpi_10']].mean(axis=1)
joined_13_10 = joined_13_10[['country', 'cpi']]

dfs = []
for i in range(17):
    df = pd.read_csv(paths[f"Source9_59_{i}"], index_col=0)
    dfs.append(df)

# Replace Source9_59_10 and Source9_59_13 with the joined dataframe in the union list
# The union order from plan:
union_order = [
    "Source9_59_0", "Source9_59_1", "Source9_59_2", "Source9_59_3", "Source9_59_5",
    "Source9_59_6", "Source9_59_7", "Source9_59_8", "Source9_59_9", "Source9_59_10",
    "Source9_59_11", "Source9_59_12", "Source9_59_13", "Source9_59_14", "Source9_59_15",
    "Source9_59_16", "Source9_59_4"
]

union_dfs = []
for name in union_order:
    if name == "Source9_59_10" or name == "Source9_59_13":
        # Use joined dataframe only once
        if "joined" not in locals():
            union_dfs.append(joined_13_10)
            joined = True
    else:
        union_dfs.append(dfs[int(name.split('_')[-1])])

result = pd.concat(union_dfs, ignore_index=True)

result.to_csv("autopipeline-benchmarks/github-pipelines/length9_59/target_multisource_mcts.csv", index=False)
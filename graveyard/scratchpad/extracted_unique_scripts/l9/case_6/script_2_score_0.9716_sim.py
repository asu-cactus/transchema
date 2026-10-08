import pandas as pd

paths = {
    "Source9_6_0": "autopipeline-benchmarks/github-pipelines/length9_6/training_0.csv",
    "Source9_6_1": "autopipeline-benchmarks/github-pipelines/length9_6/training_1.csv",
    "Source9_6_2": "autopipeline-benchmarks/github-pipelines/length9_6/training_2.csv",
    "Source9_6_3": "autopipeline-benchmarks/github-pipelines/length9_6/training_3.csv",
    "Source9_6_4": "autopipeline-benchmarks/github-pipelines/length9_6/training_4.csv",
    "Source9_6_5": "autopipeline-benchmarks/github-pipelines/length9_6/training_5.csv",
    "Source9_6_6": "autopipeline-benchmarks/github-pipelines/length9_6/training_6.csv",
    "Source9_6_7": "autopipeline-benchmarks/github-pipelines/length9_6/training_7.csv",
    "Source9_6_8": "autopipeline-benchmarks/github-pipelines/length9_6/training_8.csv",
    "Source9_6_9": "autopipeline-benchmarks/github-pipelines/length9_6/training_9.csv",
    "Source9_6_10": "autopipeline-benchmarks/github-pipelines/length9_6/training_10.csv",
    "Source9_6_11": "autopipeline-benchmarks/github-pipelines/length9_6/training_11.csv",
    "Source9_6_12": "autopipeline-benchmarks/github-pipelines/length9_6/training_12.csv",
    "Source9_6_13": "autopipeline-benchmarks/github-pipelines/length9_6/training_13.csv",
    "Source9_6_14": "autopipeline-benchmarks/github-pipelines/length9_6/training_14.csv",
    "Source9_6_15": "autopipeline-benchmarks/github-pipelines/length9_6/training_15.csv",
    "Source9_6_16": "autopipeline-benchmarks/github-pipelines/length9_6/training_16.csv",
}

df_0 = pd.read_csv(paths["Source9_6_0"], index_col=0)
df_13 = pd.read_csv(paths["Source9_6_13"], index_col=0)

joined_0_13 = pd.merge(df_0, df_13, on="country", how="inner", suffixes=('_0', '_13'))

# The join produces columns: country, cpi_0, cpi_13
# Target schema is ['country', 'cpi'] with cpi as float.
# We need to unify cpi columns into one. Since both are floats, we can average or choose one.
# The partial plan suggests union of all sources except Source9_6_13 (which is joined with Source9_6_0).
# But the union list includes Source9_6_0, so we must replace Source9_6_0 by the joined result for union.

# Prepare the joined dataframe for union by renaming cpi column:
joined_0_13['cpi'] = joined_0_13[['cpi_0', 'cpi_13']].mean(axis=1)
joined_0_13 = joined_0_13[['country', 'cpi']]

# Load all other sources except Source9_6_0 and Source9_6_13
union_sources = [
    "Source9_6_1", "Source9_6_2", "Source9_6_3", "Source9_6_4", "Source9_6_5",
    "Source9_6_6", "Source9_6_7", "Source9_6_8", "Source9_6_9", "Source9_6_10",
    "Source9_6_11", "Source9_6_12", "Source9_6_14", "Source9_6_15", "Source9_6_16"
]

dfs = [joined_0_13]

for src in union_sources:
    df = pd.read_csv(paths[src], index_col=0)
    # Ensure columns are exactly ['country', 'cpi'] and cpi is float
    df = df[['country', 'cpi']]
    df['country'] = df['country'].astype(str)
    df['cpi'] = df['cpi'].astype(float)
    dfs.append(df)

result = pd.concat(dfs, ignore_index=True)

result.to_csv("autopipeline-benchmarks/github-pipelines/length9_6/target_multisource_mcts.csv", index=False)
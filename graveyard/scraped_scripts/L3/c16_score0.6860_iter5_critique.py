import pandas as pd
import numpy as np

# Read sources with index_col=0 as instructed
source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_16/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_16/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_16/training_2.csv", index_col=0)

# Join Source0 and Source1 on user_id
join_01 = pd.merge(source0, source1, on="user_id", how="inner")

# Join the above with Source2 on movie_id to get titles
join_012 = pd.merge(join_01, source2, on="movie_id", how="inner")

# Group by title and compute mean rating by gender
grouped = join_012.groupby('title').apply(
    lambda g: pd.Series({
        'F': g.loc[g['gender'] == 'F', 'rating'].mean(),
        'M': g.loc[g['gender'] == 'M', 'rating'].mean()
    })
).reset_index()

# Remove rows with NaN in F or M to match target data completeness
grouped = grouped.dropna(subset=['F', 'M'])

# Ensure correct dtypes
grouped = grouped.astype({'F': 'float', 'M': 'float'})

# Write output with exact column names
grouped.to_csv("autopipeline-benchmarks/github-pipelines/length3_16/target_multisource_mcts.csv", index=False)
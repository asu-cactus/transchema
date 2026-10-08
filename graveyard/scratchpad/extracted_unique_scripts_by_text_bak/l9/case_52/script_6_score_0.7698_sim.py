import pandas as pd

paths = {
    "Source9_52_0": "autopipeline-benchmarks/github-pipelines/length9_52/training_0.csv",
    "Source9_52_1": "autopipeline-benchmarks/github-pipelines/length9_52/training_1.csv",
    "Source9_52_2": "autopipeline-benchmarks/github-pipelines/length9_52/training_2.csv",
    "Source9_52_3": "autopipeline-benchmarks/github-pipelines/length9_52/training_3.csv",
    "Source9_52_4": "autopipeline-benchmarks/github-pipelines/length9_52/training_4.csv",
    "Source9_52_5": "autopipeline-benchmarks/github-pipelines/length9_52/training_5.csv",
    "Source9_52_6": "autopipeline-benchmarks/github-pipelines/length9_52/training_6.csv",
    "Source9_52_7": "autopipeline-benchmarks/github-pipelines/length9_52/training_7.csv",
    "Source9_52_8": "autopipeline-benchmarks/github-pipelines/length9_52/training_8.csv",
    "Source9_52_9": "autopipeline-benchmarks/github-pipelines/length9_52/training_9.csv",
    "Source9_52_10": "autopipeline-benchmarks/github-pipelines/length9_52/training_10.csv",
    "Source9_52_11": "autopipeline-benchmarks/github-pipelines/length9_52/training_11.csv",
    "Source9_52_12": "autopipeline-benchmarks/github-pipelines/length9_52/training_12.csv",
    "Source9_52_13": "autopipeline-benchmarks/github-pipelines/length9_52/training_13.csv",
    "Source9_52_14": "autopipeline-benchmarks/github-pipelines/length9_52/training_14.csv",
}

df_2 = pd.read_csv(paths["Source9_52_2"], index_col=0)
df_3 = pd.read_csv(paths["Source9_52_3"], index_col=0)

joined = pd.merge(df_2, df_3, on="zip_code", how="inner", suffixes=('_2', '_3'))

# UNPIVOT: convert columns to rows, but here joined has columns zip_code, zip_code_3 (actually both named zip_code after merge)
# After merge on zip_code, columns are: zip_code, zip_code_3 does not exist, suffixes only apply if columns differ.
# Actually, since both have only 'zip_code', merge on zip_code results in one column 'zip_code' only.
# So the join is effectively an inner join on zip_code, resulting in unique zip_code values present in both.
# UNPIVOT here means to convert columns to rows, but joined has only one column 'zip_code'.
# So no unpivot needed on joined, just keep the zip_code column.

# To follow the plan, we treat the join result as a DataFrame with one column 'zip_code'.

joined_unpivoted = joined[["zip_code"]].copy()

# Load all other sources except 2 and 3
sources_to_union = [
    "Source9_52_0", "Source9_52_1", "Source9_52_4", "Source9_52_5", "Source9_52_6",
    "Source9_52_7", "Source9_52_8", "Source9_52_9", "Source9_52_10", "Source9_52_11",
    "Source9_52_12", "Source9_52_13", "Source9_52_14"
]

dfs = [pd.read_csv(paths[src], index_col=0) for src in sources_to_union]

dfs.append(joined_unpivoted)

result = pd.concat(dfs, ignore_index=True)

result = result.astype({"zip_code": "int64"})

result.to_csv("autopipeline-benchmarks/github-pipelines/length9_52/target_multisource_mcts.csv", index=False)
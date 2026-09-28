import pandas as pd
import glob

# Read all CSV files matching the pattern for Source1_54_0 (assuming multiple files)
# Since only one source file is given, we read that one file.
# If multiple files existed, we would glob and read all.

# For this problem, only one source file is given, so union is trivial.

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_54/training_0.csv", index_col=0)

# If there were multiple source files, e.g.:
# files = glob.glob("autopipeline-benchmarks/github-pipelines/length1_54/training_*.csv")
# dfs = [pd.read_csv(f, index_col=0) for f in files]
# df0 = pd.concat(dfs, ignore_index=True)

result = df0.groupby("condition", as_index=False).agg(click=("click", "sum"))

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_54/target_multisource_mcts.csv", index=False)
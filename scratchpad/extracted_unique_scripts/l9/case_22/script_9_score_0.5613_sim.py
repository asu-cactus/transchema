import pandas as pd

paths = {
    "Source9_22_0": "autopipeline-benchmarks/github-pipelines/length9_22/training_0.csv",
    "Source9_22_1": "autopipeline-benchmarks/github-pipelines/length9_22/training_1.csv",
    "Source9_22_2": "autopipeline-benchmarks/github-pipelines/length9_22/training_2.csv",
    "Source9_22_5": "autopipeline-benchmarks/github-pipelines/length9_22/training_5.csv",
    "Source9_22_6": "autopipeline-benchmarks/github-pipelines/length9_22/training_6.csv",
    "Source9_22_9": "autopipeline-benchmarks/github-pipelines/length9_22/training_9.csv",
}

dfs = {}
for name, path in paths.items():
    dfs[name] = pd.read_csv(path, index_col=0)

unpivoted_frames = []
for name, df in dfs.items():
    id_col = 'ROW_WID'
    # Identify the numeric column other than ROW_WID
    value_cols = [c for c in df.columns if c != id_col]
    # Unpivot: melt to get ROW_WID and value columns as rows
    melted = df.melt(id_vars=[id_col], value_vars=value_cols, var_name='metric', value_name='value')
    # Keep only rows where value is not null and metric ends with '_NUM'
    melted = melted[melted['value'].notna()]
    # Filter metrics to only those ending with '_NUM' to match target numeric counts
    melted = melted[melted['metric'].str.endswith('_NUM')]
    unpivoted_frames.append(melted)

unpivoted = pd.concat(unpivoted_frames, ignore_index=True)

# Group by the numeric values (value column) to count how many times each INBOUND_CALLS_NUM appears
# But target schema is INBOUND_CALLS_NUM only, so we need to extract INBOUND_CALLS_NUM values from the unpivoted data
# The partial plan says GROUP_BY : [INBOUND_CALLS_NUM], so we need to isolate INBOUND_CALLS_NUM values

# Extract rows where metric == 'INBOUND_CALLS_NUM'
inbound_calls = unpivoted[unpivoted['metric'] == 'INBOUND_CALLS_NUM']

# Group by the value of INBOUND_CALLS_NUM and count occurrences
result = inbound_calls.groupby('value').size().reset_index(name='count')

# Rename columns to match target schema: INBOUND_CALLS_NUM and count of occurrences
# The target schema only has INBOUND_CALLS_NUM column, but target examples show counts of INBOUND_CALLS_NUM values
# So we output the counts as rows with INBOUND_CALLS_NUM repeated accordingly

# To match target examples, we output one row per INBOUND_CALLS_NUM occurrence (not aggregated counts)
# So we repeat each INBOUND_CALLS_NUM value count times

expanded = result.loc[result.index.repeat(result['count'])].copy()
expanded = expanded[['value']].rename(columns={'value': 'INBOUND_CALLS_NUM'}).reset_index(drop=True)

expanded.to_csv("autopipeline-benchmarks/github-pipelines/length9_22/target_multisource_mcts.csv", index=False)
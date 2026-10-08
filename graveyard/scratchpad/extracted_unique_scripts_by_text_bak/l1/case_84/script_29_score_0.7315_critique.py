import pandas as pd

# Read the single source table (if more exist, they should be read similarly and unioned)
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_84/training_0.csv", index_col=0)

# Extract V_GENE from V_CALL
df0['V_GENE'] = df0['V_CALL'].str.split('*').str[0]

# Since only one source table is given, union is trivial; if multiple, concat them here
# Drop duplicates to get unique V_GENE values
result = df0[['V_GENE']].drop_duplicates().reset_index(drop=True)

# Write output
result.to_csv("autopipeline-benchmarks/github-pipelines/length1_84/target_multisource_mcts.csv", index=False)
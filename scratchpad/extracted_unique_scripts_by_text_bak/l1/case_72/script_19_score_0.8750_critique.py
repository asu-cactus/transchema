import pandas as pd

# Read all source tables
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_72/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_72/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_72/training_2.csv", index_col=0)

# UNION all source tables
df_union = pd.concat([df0, df1, df2], ignore_index=True)

# GROUP BY 'condition' and sum 'click'
pivoted = df_union.groupby('condition', as_index=False)['click'].sum()

# Rename columns to match target schema
pivoted.columns = ['condition', '0']

# Ensure correct types
pivoted['condition'] = pivoted['condition'].astype(int)
pivoted['0'] = pivoted['0'].astype(int)

# Write output
pivoted.to_csv("autopipeline-benchmarks/github-pipelines/length1_72/target_multisource_mcts.csv", index=False)
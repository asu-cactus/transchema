import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_29/training_0.csv", index_col=0)

# Since only one source table is given, UNION is trivial here.
# If more source tables existed, they would be read and concatenated here.

# Group by Gender and count Purchase ID to get counts per gender
result = df0.groupby('Gender', as_index=False)['Purchase ID'].count()

# Rename the count column to '0' as per target schema
result = result.rename(columns={'Purchase ID': '0'})

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_29/target_multisource_mcts.csv", index=False)
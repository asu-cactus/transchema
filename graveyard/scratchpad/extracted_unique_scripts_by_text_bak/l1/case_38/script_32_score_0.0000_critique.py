import pandas as pd

# Read all source CSVs with index_col=0 as per hint 22
src0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_38/training_0.csv", index_col=0)
src1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_38/training_1.csv", index_col=0)
src2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_38/training_2.csv", index_col=0)
src3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_38/training_3.csv", index_col=0)
src4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_38/training_4.csv", index_col=0)

# UNION all source tables (concatenate)
df_all = pd.concat([src0, src1, src2, src3, src4], ignore_index=True)

# GROUP BY user_id and aggregate mean of sad.depressed and open.stressed
result = df_all.groupby('user_id', as_index=False).agg({
    'sad.depressed': 'mean',
    'open.stressed': 'mean'
})

# Rename columns to match target schema
result.rename(columns={
    'sad.depressed': 'sad',
    'open.stressed': 'stressed'
}, inplace=True)

# Write output CSV with exact target schema column names
result.to_csv("autopipeline-benchmarks/github-pipelines/length1_38/target_multisource_mcts.csv", index=False)
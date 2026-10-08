import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_61/training_0.csv", index_col=0)

# Convert provider_id and provider_zip_code to int before grouping to avoid grouping issues
df0['provider_id'] = df0['provider_id'].astype(int)
df0['provider_zip_code'] = df0['provider_zip_code'].astype(int)
df0['provider_name'] = df0['provider_name'].astype(str)

agg_df = df0.groupby(
    ['provider_id', 'provider_name', 'provider_zip_code'],
    as_index=False
).agg({
    'average_covered_charges': 'mean',
    'average_total_payments': 'mean',
    'average_medicare_payments': 'mean'
})

# Ensure output types match target schema
agg_df['average_covered_charges'] = agg_df['average_covered_charges'].astype(float)
agg_df['average_total_payments'] = agg_df['average_total_payments'].astype(float)
agg_df['average_medicare_payments'] = agg_df['average_medicare_payments'].astype(float)

agg_df.to_csv("autopipeline-benchmarks/github-pipelines/length1_61/target_multisource_mcts.csv", index=False)
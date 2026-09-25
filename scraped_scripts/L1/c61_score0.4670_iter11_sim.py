import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_61/training_0.csv", index_col=0)

# The partial plan suggests a JOIN of Source1_61_0 with itself on provider_name and provider_zip_code.
# This is unusual but we follow the plan literally.
df_joined = pd.merge(df0, df0, on=['provider_name', 'provider_zip_code'], suffixes=('_left', '_right'))

# UNPIVOT operation: The target schema requires average_covered_charges, average_total_payments, average_medicare_payments as columns.
# The source has these columns directly, so unpivoting is not necessary to separate these columns.
# Instead, we select distinct provider_id, provider_name, provider_zip_code and average columns from the joined dataframe.
# Since the join duplicates columns with suffixes, we pick the left side columns for provider_id and averages.

# Extract relevant columns and drop duplicates to match target schema
df_result = df_joined[['provider_id_left', 'provider_name', 'provider_zip_code', 
                       'average_covered_charges_left', 'average_total_payments_left', 'average_medicare_payments_left']].drop_duplicates()

# Rename columns to target schema
df_result = df_result.rename(columns={
    'provider_id_left': 'provider_id',
    'average_covered_charges_left': 'average_covered_charges',
    'average_total_payments_left': 'average_total_payments',
    'average_medicare_payments_left': 'average_medicare_payments'
})

# Ensure correct dtypes
df_result['provider_id'] = df_result['provider_id'].astype(int)
df_result['provider_zip_code'] = df_result['provider_zip_code'].astype(int)
df_result['provider_name'] = df_result['provider_name'].astype(str)
df_result['average_covered_charges'] = df_result['average_covered_charges'].astype(float)
df_result['average_total_payments'] = df_result['average_total_payments'].astype(float)
df_result['average_medicare_payments'] = df_result['average_medicare_payments'].astype(float)

df_result.to_csv("autopipeline-benchmarks/github-pipelines/length1_61/target_multisource_mcts.csv", index=False)
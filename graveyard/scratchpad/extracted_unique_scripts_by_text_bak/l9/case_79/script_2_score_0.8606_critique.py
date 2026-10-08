import pandas as pd

# List of source file paths
source_files = [
    "autopipeline-benchmarks/github-pipelines/length9_79/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length9_79/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length9_79/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length9_79/training_3.csv",
    "autopipeline-benchmarks/github-pipelines/length9_79/training_4.csv",
    "autopipeline-benchmarks/github-pipelines/length9_79/training_5.csv",
    "autopipeline-benchmarks/github-pipelines/length9_79/training_6.csv",
    "autopipeline-benchmarks/github-pipelines/length9_79/training_7.csv",
    "autopipeline-benchmarks/github-pipelines/length9_79/training_8.csv",
    "autopipeline-benchmarks/github-pipelines/length9_79/training_9.csv",
    "autopipeline-benchmarks/github-pipelines/length9_79/training_10.csv",
    "autopipeline-benchmarks/github-pipelines/length9_79/training_11.csv",
    "autopipeline-benchmarks/github-pipelines/length9_79/training_12.csv",
    "autopipeline-benchmarks/github-pipelines/length9_79/training_13.csv",
    "autopipeline-benchmarks/github-pipelines/length9_79/training_14.csv",
    "autopipeline-benchmarks/github-pipelines/length9_79/training_15.csv",
    "autopipeline-benchmarks/github-pipelines/length9_79/training_16.csv",
    "autopipeline-benchmarks/github-pipelines/length9_79/training_17.csv",
    "autopipeline-benchmarks/github-pipelines/length9_79/training_18.csv",
    "autopipeline-benchmarks/github-pipelines/length9_79/training_19.csv",
    "autopipeline-benchmarks/github-pipelines/length9_79/training_20.csv",
    "autopipeline-benchmarks/github-pipelines/length9_79/training_21.csv",
    "autopipeline-benchmarks/github-pipelines/length9_79/training_22.csv",
    "autopipeline-benchmarks/github-pipelines/length9_79/training_23.csv",
    "autopipeline-benchmarks/github-pipelines/length9_79/training_24.csv",
    "autopipeline-benchmarks/github-pipelines/length9_79/training_25.csv",
    "autopipeline-benchmarks/github-pipelines/length9_79/training_26.csv",
    "autopipeline-benchmarks/github-pipelines/length9_79/training_27.csv",
    "autopipeline-benchmarks/github-pipelines/length9_79/training_28.csv",
    "autopipeline-benchmarks/github-pipelines/length9_79/training_29.csv",
    "autopipeline-benchmarks/github-pipelines/length9_79/training_30.csv",
    "autopipeline-benchmarks/github-pipelines/length9_79/training_31.csv",
    "autopipeline-benchmarks/github-pipelines/length9_79/training_32.csv",
    "autopipeline-benchmarks/github-pipelines/length9_79/training_33.csv",
    "autopipeline-benchmarks/github-pipelines/length9_79/training_34.csv",
    "autopipeline-benchmarks/github-pipelines/length9_79/training_35.csv",
    "autopipeline-benchmarks/github-pipelines/length9_79/training_36.csv",
    "autopipeline-benchmarks/github-pipelines/length9_79/training_37.csv",
    "autopipeline-benchmarks/github-pipelines/length9_79/training_38.csv",
    "autopipeline-benchmarks/github-pipelines/length9_79/training_39.csv",
    "autopipeline-benchmarks/github-pipelines/length9_79/training_40.csv",
    "autopipeline-benchmarks/github-pipelines/length9_79/training_41.csv",
    "autopipeline-benchmarks/github-pipelines/length9_79/training_42.csv",
    "autopipeline-benchmarks/github-pipelines/length9_79/training_43.csv",
    "autopipeline-benchmarks/github-pipelines/length9_79/training_44.csv",
    "autopipeline-benchmarks/github-pipelines/length9_79/training_45.csv",
    "autopipeline-benchmarks/github-pipelines/length9_79/training_46.csv",
    "autopipeline-benchmarks/github-pipelines/length9_79/training_47.csv",
    "autopipeline-benchmarks/github-pipelines/length9_79/training_48.csv",
    "autopipeline-benchmarks/github-pipelines/length9_79/training_49.csv",
    "autopipeline-benchmarks/github-pipelines/length9_79/training_50.csv",
    "autopipeline-benchmarks/github-pipelines/length9_79/training_51.csv",
    "autopipeline-benchmarks/github-pipelines/length9_79/training_52.csv",
    "autopipeline-benchmarks/github-pipelines/length9_79/training_53.csv",
    "autopipeline-benchmarks/github-pipelines/length9_79/training_54.csv",
    "autopipeline-benchmarks/github-pipelines/length9_79/training_55.csv",
    "autopipeline-benchmarks/github-pipelines/length9_79/training_56.csv",
]

# Read and union all source tables
dfs = [pd.read_csv(f, index_col=0) for f in source_files]
df_all = pd.concat(dfs, ignore_index=True)

# Define group by columns (leftmost non-float unique columns)
group_by_cols = [
    'transaction_datetime', 'transaction_id', 'outlet', 'outlet_district',
    'transact_details_id', 'item', 'item_desc', 'age_group', 'time_of_day',
    'item_type', 'item_cat', 'group_category'
]

# Define aggregation dictionary
agg_dict = {
    'qty': 'sum',
    'price': 'mean',
    'spending': 'sum',
    'age': 'mean',
    'd_price': 'mean',
    'numpax': 'mean'
}

# Perform group by and aggregation
df_final = df_all.groupby(group_by_cols, dropna=False, as_index=False).agg(agg_dict)

# Ensure column order and types match target schema exactly
target_columns = [
    'transaction_datetime', 'transaction_id', 'outlet', 'outlet_district',
    'transact_details_id', 'item', 'item_desc', 'qty', 'price', 'spending',
    'customer_id', 'age', 'age_group', 'time_of_day', 'item_type', 'item_cat',
    'd_price', 'numpax', 'group_category'
]

# customer_id is missing in group_by_cols and agg_dict, so we need to handle it:
# customer_id is integer and appears unique per transaction_id and transact_details_id,
# but since it's not in group_by, we must aggregate it.
# Since customer_id is an integer ID, and likely unique per group, we can take first or max.
# To be safe, take first non-null value.

# Add customer_id aggregation:
df_final_customer = df_all.groupby(group_by_cols, dropna=False, as_index=False)['customer_id'].first()

# Merge customer_id back
df_final = pd.merge(df_final, df_final_customer, on=group_by_cols, how='left')

# Reorder columns to target schema
df_final = df_final[target_columns]

# Cast columns to correct types as per target schema
df_final['transaction_id'] = df_final['transaction_id'].astype(int)
df_final['outlet_district'] = df_final['outlet_district'].astype(int)
df_final['transact_details_id'] = df_final['transact_details_id'].astype(int)
df_final['qty'] = df_final['qty'].astype(int)
df_final['customer_id'] = df_final['customer_id'].astype(int)
df_final['age'] = df_final['age'].round().astype(int)  # age mean rounded to int
# price, spending, d_price, numpax are float, no cast needed
# transaction_datetime, outlet, item, item_desc, age_group, time_of_day, item_type, item_cat, group_category are strings

# Write to output CSV
df_final.to_csv("autopipeline-benchmarks/github-pipelines/length9_79/target_multisource_mcts.csv", index=False)
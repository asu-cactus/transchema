import pandas as pd

# List all source file paths
source_files = [
    "autopipeline-benchmarks/github-pipelines/length9_78/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length9_78/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length9_78/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length9_78/training_3.csv",
    "autopipeline-benchmarks/github-pipelines/length9_78/training_4.csv",
    "autopipeline-benchmarks/github-pipelines/length9_78/training_5.csv",
    "autopipeline-benchmarks/github-pipelines/length9_78/training_6.csv",
    "autopipeline-benchmarks/github-pipelines/length9_78/training_7.csv",
    "autopipeline-benchmarks/github-pipelines/length9_78/training_8.csv",
    "autopipeline-benchmarks/github-pipelines/length9_78/training_9.csv",
    "autopipeline-benchmarks/github-pipelines/length9_78/training_10.csv",
    "autopipeline-benchmarks/github-pipelines/length9_78/training_11.csv",
    "autopipeline-benchmarks/github-pipelines/length9_78/training_12.csv",
    "autopipeline-benchmarks/github-pipelines/length9_78/training_13.csv",
    "autopipeline-benchmarks/github-pipelines/length9_78/training_14.csv",
    "autopipeline-benchmarks/github-pipelines/length9_78/training_15.csv",
    "autopipeline-benchmarks/github-pipelines/length9_78/training_16.csv",
    "autopipeline-benchmarks/github-pipelines/length9_78/training_17.csv",
    "autopipeline-benchmarks/github-pipelines/length9_78/training_18.csv",
    "autopipeline-benchmarks/github-pipelines/length9_78/training_19.csv",
    "autopipeline-benchmarks/github-pipelines/length9_78/training_20.csv",
    "autopipeline-benchmarks/github-pipelines/length9_78/training_21.csv",
    "autopipeline-benchmarks/github-pipelines/length9_78/training_22.csv",
    "autopipeline-benchmarks/github-pipelines/length9_78/training_23.csv",
    "autopipeline-benchmarks/github-pipelines/length9_78/training_24.csv",
    "autopipeline-benchmarks/github-pipelines/length9_78/training_25.csv",
    "autopipeline-benchmarks/github-pipelines/length9_78/training_26.csv",
    "autopipeline-benchmarks/github-pipelines/length9_78/training_27.csv",
    "autopipeline-benchmarks/github-pipelines/length9_78/training_28.csv",
    "autopipeline-benchmarks/github-pipelines/length9_78/training_29.csv",
    "autopipeline-benchmarks/github-pipelines/length9_78/training_30.csv",
    "autopipeline-benchmarks/github-pipelines/length9_78/training_31.csv",
    "autopipeline-benchmarks/github-pipelines/length9_78/training_32.csv",
    "autopipeline-benchmarks/github-pipelines/length9_78/training_33.csv",
    "autopipeline-benchmarks/github-pipelines/length9_78/training_34.csv",
    "autopipeline-benchmarks/github-pipelines/length9_78/training_35.csv",
    "autopipeline-benchmarks/github-pipelines/length9_78/training_36.csv",
    "autopipeline-benchmarks/github-pipelines/length9_78/training_37.csv",
    "autopipeline-benchmarks/github-pipelines/length9_78/training_38.csv",
    "autopipeline-benchmarks/github-pipelines/length9_78/training_39.csv",
    "autopipeline-benchmarks/github-pipelines/length9_78/training_40.csv",
    "autopipeline-benchmarks/github-pipelines/length9_78/training_41.csv",
    "autopipeline-benchmarks/github-pipelines/length9_78/training_42.csv",
    "autopipeline-benchmarks/github-pipelines/length9_78/training_43.csv",
    "autopipeline-benchmarks/github-pipelines/length9_78/training_44.csv",
    "autopipeline-benchmarks/github-pipelines/length9_78/training_45.csv",
    "autopipeline-benchmarks/github-pipelines/length9_78/training_46.csv",
    "autopipeline-benchmarks/github-pipelines/length9_78/training_47.csv",
    "autopipeline-benchmarks/github-pipelines/length9_78/training_48.csv",
    "autopipeline-benchmarks/github-pipelines/length9_78/training_49.csv",
    "autopipeline-benchmarks/github-pipelines/length9_78/training_50.csv",
    "autopipeline-benchmarks/github-pipelines/length9_78/training_51.csv",
    "autopipeline-benchmarks/github-pipelines/length9_78/training_52.csv",
    "autopipeline-benchmarks/github-pipelines/length9_78/training_53.csv",
    "autopipeline-benchmarks/github-pipelines/length9_78/training_54.csv",
    "autopipeline-benchmarks/github-pipelines/length9_78/training_55.csv",
    "autopipeline-benchmarks/github-pipelines/length9_78/training_56.csv",
]

# Read and union all source tables
dfs = [pd.read_csv(f, index_col=0) for f in source_files]
df = pd.concat(dfs, ignore_index=True)

# Define group by columns (all non-float columns except qty which is aggregated)
group_by_cols = [
    'transaction_datetime', 'transaction_id', 'outlet', 'outlet_district',
    'transact_details_id', 'item', 'item_desc', 'customer_id', 'age',
    'age_group', 'time_of_day', 'item_type', 'item_cat', 'group_category'
]

# Aggregate columns: sum for qty, price, spending, d_price, numpax
agg_dict = {
    'qty': 'sum',
    'price': 'sum',
    'spending': 'sum',
    'd_price': 'sum',
    'numpax': 'sum'
}

# Perform group by and aggregation
df_final = df.groupby(group_by_cols, dropna=False, as_index=False).agg(agg_dict)

# Ensure column order matches target schema exactly
target_columns = [
    'transaction_datetime', 'transaction_id', 'outlet', 'outlet_district',
    'transact_details_id', 'item', 'item_desc', 'qty', 'price', 'spending',
    'customer_id', 'age', 'age_group', 'time_of_day', 'item_type', 'item_cat',
    'd_price', 'numpax', 'group_category'
]

df_final = df_final[target_columns]

# Write to output CSV
df_final.to_csv("autopipeline-benchmarks/github-pipelines/length9_78/target_multisource_mcts.csv", index=False)
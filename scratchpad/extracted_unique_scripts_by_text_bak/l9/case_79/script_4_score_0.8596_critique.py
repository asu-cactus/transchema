import pandas as pd

# List all source CSV file paths
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

# Read all source files with index_col=0 to ignore the first index column
dfs = [pd.read_csv(f, index_col=0) for f in source_files]

# Concatenate all dataframes
df = pd.concat(dfs, ignore_index=True)

# Enforce correct data types according to target schema
# Target schema:
# ['transaction_datetime': string,
#  'transaction_id': integer,
#  'outlet': string,
#  'outlet_district': integer,
#  'transact_details_id': integer,
#  'item': string,
#  'item_desc': string,
#  'qty': integer,
#  'price': float,
#  'spending': float,
#  'customer_id': integer,
#  'age': integer,
#  'age_group': string,
#  'time_of_day': string,
#  'item_type': string,
#  'item_cat': string,
#  'd_price': float,
#  'numpax': float,
#  'group_category': string]

# Convert columns to appropriate types
df['transaction_datetime'] = df['transaction_datetime'].astype(str)
df['transaction_id'] = pd.to_numeric(df['transaction_id'], errors='coerce').astype('Int64')
df['outlet'] = df['outlet'].astype(str)
df['outlet_district'] = pd.to_numeric(df['outlet_district'], errors='coerce').astype('Int64')
df['transact_details_id'] = pd.to_numeric(df['transact_details_id'], errors='coerce').astype('Int64')
df['item'] = df['item'].astype(str)
df['item_desc'] = df['item_desc'].astype(str)
df['qty'] = pd.to_numeric(df['qty'], errors='coerce').astype('Int64')
df['price'] = pd.to_numeric(df['price'], errors='coerce').astype(float)
df['spending'] = pd.to_numeric(df['spending'], errors='coerce').astype(float)
df['customer_id'] = pd.to_numeric(df['customer_id'], errors='coerce').astype('Int64')
df['age'] = pd.to_numeric(df['age'], errors='coerce').astype('Int64')
df['age_group'] = df['age_group'].astype(str)
df['time_of_day'] = df['time_of_day'].astype(str)
df['item_type'] = df['item_type'].astype(str)
df['item_cat'] = df['item_cat'].astype(str)
df['d_price'] = pd.to_numeric(df['d_price'], errors='coerce').astype(float)
df['numpax'] = pd.to_numeric(df['numpax'], errors='coerce').astype(float)
df['group_category'] = df['group_category'].astype(str)

# Write to target CSV
df.to_csv("autopipeline-benchmarks/github-pipelines/length9_79/target_multisource_mcts.csv", index=False)
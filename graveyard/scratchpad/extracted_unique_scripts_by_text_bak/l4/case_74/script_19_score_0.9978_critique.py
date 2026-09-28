import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_74/training_0.csv", index_col=0)

# Group by Gender and count Purchase ID per Gender
grouped = df0.groupby('Gender', as_index=False).agg({'Purchase ID': 'count'})

# Rename the count column to 'Purchase ID' (already named)
# Assign the count value to all integer columns in target schema except Gender
count_col = 'Purchase ID'
int_cols = ['Purchase ID', 'SN', 'Age', 'Item ID', 'Item Name', 'Price']

for col in int_cols:
    grouped[col] = grouped[count_col]

# Reorder columns to match target schema
grouped = grouped[['Gender', 'Purchase ID', 'SN', 'Age', 'Item ID', 'Item Name', 'Price']]

# Ensure correct dtypes
grouped['Gender'] = grouped['Gender'].astype(str)
for col in int_cols:
    grouped[col] = grouped[col].astype(int)

grouped.to_csv("autopipeline-benchmarks/github-pipelines/length4_74/target_multisource_mcts.csv", index=False)
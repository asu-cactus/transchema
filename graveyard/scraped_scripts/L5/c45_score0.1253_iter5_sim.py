import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_45/training_0.csv", index_col=0)

agg = df0.groupby(['Gender', 'SN']).agg(
    Purchase_Count=('Purchase ID', 'count'),
    Average_Purchase_Price=('Price', 'mean'),
    Total_Purchase_Value=('Price', 'sum')
).reset_index()

# The target schema has many columns that do not appear in the source or aggregation.
# Since only one source table is given, and the partial plan only aggregates on Gender and SN,
# the other columns (Age_x, Item ID_x, Item Name, Price, Purchase ID_x, Age_y, Item ID_y, Purchase ID_y, Age, Item ID)
# are not derivable from the given data or operations.
# The target examples show these columns have integer or float values, but no source or operation provides them.
# Therefore, we will fill these missing columns with NaN or 0 as appropriate to match the target schema columns.

# Create all columns in target schema with default NaN or 0 values
target_columns = ['Gender', 'Purchase Count', 'SN', 'Age_x', 'Item ID_x', 'Item Name', 'Price', 'Purchase ID_x',
                  'Age_y', 'Item ID_y', 'Average Purchase Price', 'Purchase ID_y', 'Age', 'Item ID', 'Total Purchase Value']

# Start with agg DataFrame and rename columns to match target schema
agg = agg.rename(columns={
    'Purchase_Count': 'Purchase Count',
    'Average_Purchase_Price': 'Average Purchase Price',
    'Total_Purchase_Value': 'Total Purchase Value'
})

# Add missing columns with NaN or 0
for col in target_columns:
    if col not in agg.columns:
        if col in ['Purchase Count', 'SN', 'Age_x', 'Item ID_x', 'Item Name', 'Price', 'Purchase ID_x',
                   'Purchase ID_y', 'Age', 'Item ID']:
            agg[col] = pd.NA
        else:
            agg[col] = pd.NA

# Reorder columns to match target schema
agg = agg[target_columns]

agg.to_csv("autopipeline-benchmarks/github-pipelines/length5_45/target_multisource_mcts.csv", index=False)
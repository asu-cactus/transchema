import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_74/training_0.csv", index_col=0)

# Group by Gender and count Purchase ID
grouped = df0.groupby('Gender', as_index=False).agg({'Purchase ID': 'count'})

# Rename count column to a temporary name
grouped = grouped.rename(columns={'Purchase ID': 'count'})

# Fill all columns except Gender with the count value
for col in ['Purchase ID', 'SN', 'Age', 'Item ID', 'Item Name', 'Price']:
    grouped[col] = grouped['count']

# Drop the temporary count column
grouped = grouped.drop(columns=['count'])

# Reorder columns to match target schema
result = grouped[['Gender', 'Purchase ID', 'SN', 'Age', 'Item ID', 'Item Name', 'Price']]

# Ensure correct dtypes: Gender string, others int
result['Gender'] = result['Gender'].astype(str)
for col in result.columns[1:]:
    result[col] = result[col].astype(int)

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_74/target_multisource_mcts.csv", index=False)
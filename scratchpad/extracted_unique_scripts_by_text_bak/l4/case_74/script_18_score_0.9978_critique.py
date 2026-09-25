import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_74/training_0.csv", index_col=0)

# Group by Gender and count the number of Purchase ID per gender
agg_df = df0.groupby("Gender").agg({"Purchase ID": "count"}).reset_index()

# Assign the count value to all columns except Gender
for col in ['Purchase ID', 'SN', 'Age', 'Item ID', 'Item Name', 'Price']:
    agg_df[col] = agg_df["Purchase ID"]

# Reorder columns to match target schema
agg_df = agg_df[['Gender', 'Purchase ID', 'SN', 'Age', 'Item ID', 'Item Name', 'Price']]

# Set correct dtypes
agg_df = agg_df.astype({
    "Gender": "string",
    "Purchase ID": "int64",
    "SN": "int64",
    "Age": "int64",
    "Item ID": "int64",
    "Item Name": "int64",
    "Price": "int64"
})

agg_df.to_csv("autopipeline-benchmarks/github-pipelines/length4_74/target_multisource_mcts.csv", index=False)
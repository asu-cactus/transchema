import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_74/training_0.csv", index_col=0)

# Convert columns that are strings but expected as integers in target to integers if possible
# For 'SN' and 'Item Name', since they are strings, we try to convert them to categorical codes (integers)
df0["SN"] = df0["SN"].astype('category').cat.codes
df0["Item Name"] = df0["Item Name"].astype('category').cat.codes

# Group by Gender and aggregate other columns by max (or mean)
df_grouped = df0.groupby("Gender", as_index=False).agg({
    "Purchase ID": "max",
    "SN": "max",
    "Age": "max",
    "Item ID": "max",
    "Item Name": "max",
    "Price": "max"
})

# Convert all aggregated columns to int as per target schema
df_grouped["Purchase ID"] = df_grouped["Purchase ID"].astype(int)
df_grouped["SN"] = df_grouped["SN"].astype(int)
df_grouped["Age"] = df_grouped["Age"].astype(int)
df_grouped["Item ID"] = df_grouped["Item ID"].astype(int)
df_grouped["Item Name"] = df_grouped["Item Name"].astype(int)
df_grouped["Price"] = df_grouped["Price"].astype(int)

df_grouped.to_csv("autopipeline-benchmarks/github-pipelines/length4_74/target_multisource_mcts.csv", index=False)
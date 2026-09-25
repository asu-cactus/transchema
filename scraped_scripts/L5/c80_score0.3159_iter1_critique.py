import pandas as pd

# Read the same source table twice
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_80/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_80/training_0.csv", index_col=0)

# Convert data types for df0
df0['Purchase ID'] = pd.to_numeric(df0['Purchase ID'], errors='coerce').astype('Int64')
df0['SN'] = pd.to_numeric(df0['SN'], errors='coerce', downcast='integer')
df0['Age'] = pd.to_numeric(df0['Age'], errors='coerce').astype('Int64')
df0['Gender'] = df0['Gender'].map({'Male':1, 'Female':2}).astype('Int64')
df0['Item ID'] = pd.to_numeric(df0['Item ID'], errors='coerce').astype('Int64')
df0['Price'] = pd.to_numeric(df0['Price'], errors='coerce')

# Convert data types for df1 (same as df0)
df1['Purchase ID'] = pd.to_numeric(df1['Purchase ID'], errors='coerce').astype('Int64')
df1['SN'] = pd.to_numeric(df1['SN'], errors='coerce', downcast='integer')
df1['Age'] = pd.to_numeric(df1['Age'], errors='coerce').astype('Int64')
df1['Gender'] = df1['Gender'].map({'Male':1, 'Female':2}).astype('Int64')
df1['Item ID'] = pd.to_numeric(df1['Item ID'], errors='coerce').astype('Int64')
df1['Price'] = pd.to_numeric(df1['Price'], errors='coerce')

# Rename columns in df0 to suffix _x except 'Item Name' and 'SN' and 'Gender' which appear without suffix in target
df0_renamed = df0.rename(columns={
    'Purchase ID': 'Purchase ID_x',
    'Age': 'Age_x',
    'Item ID': 'Item ID_x',
    'Price': 'Price_x'
})

# Rename columns in df1 to suffix _y except 'Item Name' and 'SN' and 'Gender' which appear without suffix in target
df1_renamed = df1.rename(columns={
    'Purchase ID': 'Purchase ID_y',
    'Age': 'Age_y',
    'Item ID': 'Item ID_y',
    'Price': 'Price_y'
})

# Join on Purchase ID (df0.Purchase ID_x == df1.Purchase ID_y)
df_joined = pd.merge(
    df0_renamed,
    df1_renamed,
    left_on='Purchase ID_x',
    right_on='Purchase ID_y',
    how='inner',
    suffixes=('_x', '_y')
)

# Construct final dataframe with columns exactly as target schema:
# ['Item Name', 'Purchase ID', 'SN', 'Age', 'Gender', 'Item ID',
#  'Price_x', 'Purchase ID_x', 'Age_x', 'Item ID_x',
#  'Price_y', 'Item ID_y', 'Purchase ID_y', 'Age_y']

# According to target examples:
# - 'Item Name' comes from df0 (no suffix)
# - 'Purchase ID', 'SN', 'Age', 'Gender', 'Item ID' come from df0 (no suffix)
# - The rest are suffixed columns from both sides

df_final = pd.DataFrame({
    'Item Name': df_joined['Item Name_x'],
    'Purchase ID': df_joined['Purchase ID_x'],
    'SN': df_joined['SN_x'],
    'Age': df_joined['Age_x'],
    'Gender': df_joined['Gender_x'],
    'Item ID': df_joined['Item ID_x'],
    'Price_x': df_joined['Price_x'],
    'Purchase ID_x': df_joined['Purchase ID_x'],
    'Age_x': df_joined['Age_x'],
    'Item ID_x': df_joined['Item ID_x'],
    'Price_y': df_joined['Price_y'],
    'Item ID_y': df_joined['Item ID_y'],
    'Purchase ID_y': df_joined['Purchase ID_y'],
    'Age_y': df_joined['Age_y']
})

# Ensure correct dtypes matching target schema
df_final['Purchase ID'] = df_final['Purchase ID'].astype('Int64')
df_final['SN'] = pd.to_numeric(df_final['SN'], errors='coerce', downcast='integer')
df_final['Age'] = df_final['Age'].astype('Int64')
df_final['Gender'] = df_final['Gender'].astype('Int64')
df_final['Item ID'] = df_final['Item ID'].astype('Int64')
df_final['Price_x'] = pd.to_numeric(df_final['Price_x'], errors='coerce')
df_final['Purchase ID_x'] = df_final['Purchase ID_x'].astype('Int64')
df_final['Age_x'] = df_final['Age_x'].astype('Int64')
df_final['Item ID_x'] = df_final['Item ID_x'].astype('Int64')
df_final['Price_y'] = pd.to_numeric(df_final['Price_y'], errors='coerce')
df_final['Item ID_y'] = df_final['Item ID_y'].astype('Int64')
df_final['Purchase ID_y'] = df_final['Purchase ID_y'].astype('Int64')
df_final['Age_y'] = df_final['Age_y'].astype('Int64')

# Write to output CSV
df_final.to_csv("autopipeline-benchmarks/github-pipelines/length5_80/target_multisource_mcts.csv", index=False)
import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_74/training_0.csv", index_col=0)

# First operation: JOIN Source4_74_0 with itself on Purchase ID
joined = pd.merge(df0, df0, on="Purchase ID", suffixes=('_left', '_right'))

# The join duplicates columns, but since it's the same table joined with itself,
# we can select columns from one side (left) to keep schema consistent.
joined = joined[[ 'Gender_left', 'Purchase ID', 'SN_left', 'Age_left', 'Item ID_left', 'Item Name_left', 'Price_left']]
joined.columns = ['Gender', 'Purchase ID', 'SN', 'Age', 'Item ID', 'Item Name', 'Price']

# Second operation: UNION Source4_74_0 with itself (union of df0 and df0)
unioned = pd.concat([df0, df0], ignore_index=True)

# The target schema requires:
# Gender: string
# Purchase ID: integer
# SN: integer
# Age: integer
# Item ID: integer
# Item Name: integer
# Price: integer

# From source, 'SN' and 'Item Name' are strings, need to convert to integer.
# We will convert 'SN' and 'Item Name' by extracting digits if possible or map unique strings to integers.

def convert_to_int_series(s):
    # Try to convert directly to int, if fails, map unique strings to integers
    try:
        return s.astype(int)
    except:
        return s.astype('category').cat.codes

# Apply conversions on unioned dataframe to match target schema
result = unioned.copy()
result['Gender'] = result['Gender'].astype(str)
result['Purchase ID'] = pd.to_numeric(result['Purchase ID'], errors='coerce').fillna(0).astype(int)
result['SN'] = convert_to_int_series(result['SN'])
result['Age'] = pd.to_numeric(result['Age'], errors='coerce').fillna(0).astype(int)
result['Item ID'] = pd.to_numeric(result['Item ID'], errors='coerce').fillna(0).astype(int)
result['Item Name'] = convert_to_int_series(result['Item Name'])
result['Price'] = pd.to_numeric(result['Price'], errors='coerce').fillna(0).astype(int)

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_74/target_multisource_mcts.csv", index=False)
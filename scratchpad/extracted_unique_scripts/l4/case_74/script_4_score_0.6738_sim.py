import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_74/training_0.csv", index_col=0)

# The source schema is already aligned with the target schema except:
# - 'Gender' should be string (already string)
# - 'Purchase ID', 'SN', 'Age', 'Item ID', 'Item Name', 'Price' need to be converted to correct types
# 'SN' and 'Item Name' are strings in source but target expects integers, which is unusual.
# However, target schema says 'Item Name': integer, but source example shows string names.
# This is likely a mistake in the prompt or a hint that 'Item Name' should be converted to some integer representation.
# Since the partial plan says PIVOT twice, let's interpret that as pivoting categorical columns to numeric codes.

# Convert 'Gender' to string (already string)
df0['Gender'] = df0['Gender'].astype(str)

# Convert 'Purchase ID', 'Age', 'Item ID', 'Price' to integer if possible
df0['Purchase ID'] = pd.to_numeric(df0['Purchase ID'], errors='coerce').fillna(0).astype(int)
df0['Age'] = pd.to_numeric(df0['Age'], errors='coerce').fillna(0).astype(int)
df0['Item ID'] = pd.to_numeric(df0['Item ID'], errors='coerce').fillna(0).astype(int)
df0['Price'] = pd.to_numeric(df0['Price'], errors='coerce').fillna(0).astype(int)

# 'SN' and 'Item Name' are strings but target expects integers.
# We will encode them as categorical codes (pivot operation)
df0['SN'] = df0['SN'].astype('category').cat.codes
df0['Item Name'] = df0['Item Name'].astype('category').cat.codes

df0 = df0[['Gender', 'Purchase ID', 'SN', 'Age', 'Item ID', 'Item Name', 'Price']]

df0.to_csv("autopipeline-benchmarks/github-pipelines/length4_74/target_multisource_mcts.csv", index=False)
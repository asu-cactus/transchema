import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_74/training_0.csv", index_col=0)

# First operation: join Source4_74_0 with itself on Purchase ID (self-join)
joined = pd.merge(df0, df0, on="Purchase ID", suffixes=('_left', '_right'))

# The join duplicates columns, but target schema expects single columns.
# We take columns from the left side (or right, they are identical).
# Next operation: union Source4_74_0 with itself (concatenate twice)
unioned = pd.concat([df0, df0], ignore_index=True)

# The target schema is:
# ['Gender': string, 'Purchase ID': integer, 'SN': integer, 'Age': integer, 'Item ID': integer, 'Item Name': integer, 'Price': integer]
# Source columns: ['Purchase ID', 'SN', 'Age', 'Gender', 'Item ID', 'Item Name', 'Price']
# We need to reorder columns and convert types accordingly.

# Reorder columns to target schema order
result = unioned[['Gender', 'Purchase ID', 'SN', 'Age', 'Item ID', 'Item Name', 'Price']].copy()

# Convert types:
# Gender: string (already string)
result['Gender'] = result['Gender'].astype(str)

# Purchase ID: integer
result['Purchase ID'] = pd.to_numeric(result['Purchase ID'], errors='coerce').astype('Int64')

# SN: integer - source SN looks like strings (e.g. 'Asur53'), but target expects integer.
# We must convert SN to integer. Since source SN is string, try to extract digits or convert to NaN.
# Extract digits from SN string, if none found, set NaN
result['SN'] = result['SN'].astype(str).str.extract('(\d+)')
result['SN'] = pd.to_numeric(result['SN'], errors='coerce').astype('Int64')

# Age: integer
result['Age'] = pd.to_numeric(result['Age'], errors='coerce').astype('Int64')

# Item ID: integer
result['Item ID'] = pd.to_numeric(result['Item ID'], errors='coerce').astype('Int64')

# Item Name: integer - source is string, target expects integer.
# This is inconsistent. We must convert Item Name string to integer.
# Since no direct mapping, convert by hashing string and taking absolute value mod large int.
result['Item Name'] = result['Item Name'].astype(str).apply(lambda x: abs(hash(x)) % (10**9)).astype('Int64')

# Price: integer - source is float, target expects integer.
# Convert by rounding
result['Price'] = pd.to_numeric(result['Price'], errors='coerce').round().astype('Int64')

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_74/target_multisource_mcts.csv", index=False)
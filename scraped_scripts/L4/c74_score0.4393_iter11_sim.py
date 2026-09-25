import pandas as pd

source0_path = "autopipeline-benchmarks/github-pipelines/length4_74/training_0.csv"

df0 = pd.read_csv(source0_path, index_col=0)

# According to the plan, first join Source4_74_0 with itself on SN (which is trivial and results in the same data)
# Then union Source4_74_0 with itself (which doubles the data)
joined = pd.merge(df0, df0, on="SN", suffixes=('_left', '_right'))

# The join duplicates columns, but since both sides are the same table, we can just take columns from one side
# The target schema is ['Gender', 'Purchase ID', 'SN', 'Age', 'Item ID', 'Item Name', 'Price']
# The source columns are ['Purchase ID', 'SN', 'Age', 'Gender', 'Item ID', 'Item Name', 'Price']
# So we select columns from the left side of the join (or right, same data)
joined_selected = joined[['Gender_left', 'Purchase ID_left', 'SN', 'Age_left', 'Item ID_left', 'Item Name_left', 'Price_left']]
joined_selected.columns = ['Gender', 'Purchase ID', 'SN', 'Age', 'Item ID', 'Item Name', 'Price']

# Now union Source4_74_0 with itself (concatenate the dataframe with itself)
unioned = pd.concat([joined_selected, joined_selected], ignore_index=True)

# Fix data types according to target schema:
# Gender: string (already string)
# Purchase ID: integer
# SN: integer (source SN is string, need to convert)
# Age: integer
# Item ID: integer
# Item Name: integer (source Item Name is string, convert to integer by mapping unique names to integers)
# Price: integer (source Price is float, convert by rounding or truncation)

# Convert Purchase ID, Age, Item ID to int
unioned['Purchase ID'] = pd.to_numeric(unioned['Purchase ID'], errors='coerce').fillna(0).astype(int)
unioned['Age'] = pd.to_numeric(unioned['Age'], errors='coerce').fillna(0).astype(int)
unioned['Item ID'] = pd.to_numeric(unioned['Item ID'], errors='coerce').fillna(0).astype(int)

# Convert SN from string to integer by extracting digits if possible, else map unique SN strings to integers
def sn_to_int(sn_series):
    # Try to extract digits from SN strings
    import re
    def extract_num(s):
        if pd.isna(s):
            return 0
        nums = re.findall(r'\d+', s)
        if nums:
            return int(nums[0])
        else:
            return 0
    return sn_series.map(extract_num)

unioned['SN'] = sn_to_int(unioned['SN']).astype(int)

# Convert Item Name (string) to integer by mapping unique names to unique integers
item_name_map = {name: idx for idx, name in enumerate(unioned['Item Name'].unique(), start=1)}
unioned['Item Name'] = unioned['Item Name'].map(item_name_map).fillna(0).astype(int)

# Convert Price float to int by rounding
unioned['Price'] = pd.to_numeric(unioned['Price'], errors='coerce').fillna(0).round().astype(int)

# Ensure Gender is string
unioned['Gender'] = unioned['Gender'].astype(str)

unioned.to_csv("autopipeline-benchmarks/github-pipelines/length4_74/target_multisource_mcts.csv", index=False)
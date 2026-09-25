import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_45/training_0.csv", index_col=0)

df0['Purchase ID'] = pd.to_numeric(df0['Purchase ID'], errors='coerce')
df0['SN'] = pd.to_numeric(df0['SN'], errors='coerce')
df0['Age'] = pd.to_numeric(df0['Age'], errors='coerce')
df0['Item ID'] = pd.to_numeric(df0['Item ID'], errors='coerce')
df0['Item Name'] = pd.to_numeric(df0['Item Name'], errors='coerce')
df0['Price'] = pd.to_numeric(df0['Price'], errors='coerce')

pivot_cols = ['Purchase ID', 'SN', 'Age', 'Item ID', 'Item Name', 'Price']
df_pivot = df0.pivot_table(index=[], columns='Gender', values=pivot_cols, aggfunc='mean')

df_pivot.columns = [f"{col[0]}_{col[1]}" for col in df_pivot.columns]
df_pivot = df_pivot.reset_index(drop=True)

df_pivot['Gender'] = df_pivot.columns.str.split('_').str[1].unique()[0]  # placeholder, will fix below

# The pivot above produces one row with columns for each Gender, but target has 3 rows, one per Gender.
# So we need to reshape pivoted data to long format by Gender.

# Instead, do pivot without index, then stack Gender to rows:
df_pivot = df0.pivot_table(index=[], columns='Gender', values=pivot_cols, aggfunc='mean')
df_pivot.columns = [f"{col[0]}_{col[1]}" for col in df_pivot.columns]
df_pivot = df_pivot.reset_index(drop=True)

# Extract genders from columns
genders = sorted(df0['Gender'].dropna().unique())

rows = []
for gender in genders:
    row = {}
    row['Gender'] = gender
    for col in pivot_cols:
        col_name = f"{col}_{gender}"
        if col_name in df_pivot.columns:
            row[col_name] = df_pivot.at[0, col_name]
        else:
            row[col_name] = None
    rows.append(row)

df_result = pd.DataFrame(rows)

# Add 'Purchase Count' and 'SN' columns as integer counts per Gender
purchase_counts = df0.groupby('Gender').size()
df_result['Purchase Count'] = df_result['Gender'].map(purchase_counts).fillna(0).astype(int)

# 'SN' in target is integer, but source SN is string, so count distinct SN per Gender
sn_counts = df0.groupby('Gender')['SN'].nunique()
df_result['SN'] = df_result['Gender'].map(sn_counts).fillna(0).astype(int)

# 'Purchase ID_x' and 'Purchase ID_y' are float and int respectively in target
# We have only one source, so we create these columns by splitting Purchase ID mean and count or sum

# For 'Purchase ID_x' (float), use mean Purchase ID per Gender
purchase_id_mean = df0.groupby('Gender')['Purchase ID'].mean()
df_result['Purchase ID_x'] = df_result['Gender'].map(purchase_id_mean).astype(float)

# For 'Purchase ID_y' (int), use count of Purchase ID per Gender
purchase_id_count = df0.groupby('Gender')['Purchase ID'].count()
df_result['Purchase ID_y'] = df_result['Gender'].map(purchase_id_count).astype(int)

# 'Age_x' int, 'Age_y' float, 'Age' int
age_mean = df0.groupby('Gender')['Age'].mean()
age_median = df0.groupby('Gender')['Age'].median()
age_min = df0.groupby('Gender')['Age'].min()

df_result['Age_x'] = df_result['Gender'].map(age_median).fillna(0).astype(int)
df_result['Age_y'] = df_result['Gender'].map(age_mean).astype(float)
df_result['Age'] = df_result['Gender'].map(age_min).fillna(0).astype(int)

# 'Item ID_x' int, 'Item ID_y' float, 'Item ID' int
item_id_mean = df0.groupby('Gender')['Item ID'].mean()
item_id_median = df0.groupby('Gender')['Item ID'].median()
item_id_min = df0.groupby('Gender')['Item ID'].min()

df_result['Item ID_x'] = df_result['Gender'].map(item_id_median).fillna(0).astype(int)
df_result['Item ID_y'] = df_result['Gender'].map(item_id_mean).astype(float)
df_result['Item ID'] = df_result['Gender'].map(item_id_min).fillna(0).astype(int)

# 'Item Name' int (from source is string, convert to int by factorizing)
item_name_codes = df0['Item Name'].astype('category').cat.codes
df0['Item Name Code'] = item_name_codes
item_name_mode = df0.groupby('Gender')['Item Name Code'].agg(lambda x: x.mode().iloc[0] if not x.mode().empty else -1)
df_result['Item Name'] = df_result['Gender'].map(item_name_mode).astype(int)

# 'Price' int (from source float, convert by rounding)
price_mean = df0.groupby('Gender')['Price'].mean()
df_result['Price'] = df_result['Gender'].map(price_mean).round().astype(int)

# 'Average Purchase Price' float (mean Price)
df_result['Average Purchase Price'] = df_result['Gender'].map(price_mean).astype(float)

# 'Total Purchase Value' float (sum Price)
price_sum = df0.groupby('Gender')['Price'].sum()
df_result['Total Purchase Value'] = df_result['Gender'].map(price_sum).astype(float)

# Reorder columns to match target schema
target_cols = ['Gender', 'Purchase Count', 'SN', 'Age_x', 'Item ID_x', 'Item Name', 'Price', 'Purchase ID_x',
               'Age_y', 'Item ID_y', 'Average Purchase Price', 'Purchase ID_y', 'Age', 'Item ID', 'Total Purchase Value']

df_result = df_result[target_cols]

df_result.to_csv("autopipeline-benchmarks/github-pipelines/length5_45/target_multisource_mcts.csv", index=False)
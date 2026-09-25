import pandas as pd

# File paths for the sources
source_paths = [
    "autopipeline-benchmarks/github-pipelines/length4_43/test_0.csv",
    "autopipeline-benchmarks/github-pipelines/length4_43/test_1.csv",
    "autopipeline-benchmarks/github-pipelines/length4_43/test_2.csv",
    "autopipeline-benchmarks/github-pipelines/length4_43/test_3.csv"
]

# Read all source files with index_col=0 (ignore the first numeric index column)
dfs = [pd.read_csv(path, index_col=0) for path in source_paths]

# Since all source schemas are identical:
# ['title', 'company', 'location', 'summary', 'salary', 'href', 'rate', 'reviews', 'org_salary_period']
# and the target schema is:
# ['company': string, 'title': integer, 'location': integer, 'summary': integer, 'salary': integer,
#  'href': integer, 'rate': integer, 'reviews': integer, 'org_salary_period': integer]
#
# Transformation plan:
# 1. Concatenate (union) all source dataframes vertically.
# 2. Convert the 'company' column to string.
# 3. For all other columns, convert values to integers with the following processing:
#    - Columns that are originally string but categorical or numeric stored as strings (e.g. 'rate', 'reviews') 
#      need to be converted carefully:
#      * 'reviews' column may contain commas (like '6,388'), so remove commas before conversion.
#      * 'rate' and 'salary' may be float strings; we will convert them to int by rounding.
#      * 'org_salary_period' is a categorical string (e.g. 'year', 'hour', 'day', 'month') - we convert to integers by
#        assigning consistent integer IDs to each category as in the target examples.
#    - Columns 'title', 'location', 'summary', 'salary', 'href', 'rate', 'reviews' are converted to integer.
# 4. Remove any rows with missing values after conversion to ensure clean output matching target examples.
# 5. Save to the target CSV path.

# Concatenate all source dataframes (union)
df = pd.concat(dfs, ignore_index=True)

# Ensure 'company' is string
df['company'] = df['company'].astype(str)

# Helper to convert columns to integer safely
def to_int_series(s):
    # Remove commas if present (like in 'reviews')
    s_clean = s.astype(str).str.replace(',', '', regex=False).str.strip()
    # Convert to float first to handle decimal strings, then to int by rounding
    return pd.to_numeric(s_clean, errors='coerce').round().astype('Int64')

# Convert text columns to integer categorical mappings if needed
# org_salary_period conversion based on distinct categories seen in sources and consistent with target examples:
# Examples categories: 'year', 'hour', 'day', 'month'
# We assign integers as per the examples, inferred:
org_salary_period_map = {
    'year': 1,
    'hour': 2,
    'day': 3,
    'month': 4
}
# Normalize org_salary_period strings: lower-case and strip
df['org_salary_period'] = df['org_salary_period'].astype(str).str.strip().str.lower().map(org_salary_period_map)

# Convert columns except 'company' and 'org_salary_period' to int
for col in ['title', 'location', 'summary', 'salary', 'href', 'rate', 'reviews']:
    df[col] = to_int_series(df[col])

# Drop rows with any missing values after conversions to mimic clean target data (no NaNs in target examples)
df_clean = df.dropna(subset=['company', 'title', 'location', 'summary', 'salary', 'href', 'rate', 'reviews', 'org_salary_period'])

# Convert Integer Nullable dtypes to standard int (target examples show int, not nullable)
for col in ['title', 'location', 'summary', 'salary', 'href', 'rate', 'reviews', 'org_salary_period']:
    df_clean[col] = df_clean[col].astype(int)

# Final dataframe columns ordered exactly as target schema:
# ['company', 'title', 'location', 'summary', 'salary', 'href', 'rate', 'reviews', 'org_salary_period']
df_final = df_clean[['company', 'title', 'location', 'summary', 'salary', 'href', 'rate', 'reviews', 'org_salary_period']]

# Write to target csv (no index)
df_final.to_csv("autopipeline-benchmarks/github-pipelines/length4_43/target_multisource_cot.csv", index=False)
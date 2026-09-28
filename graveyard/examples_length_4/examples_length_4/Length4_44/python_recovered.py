import pandas as pd

# File paths for source tables
source_paths = [
    "autopipeline-benchmarks/github-pipelines/length4_44/test_0.csv",
    "autopipeline-benchmarks/github-pipelines/length4_44/test_1.csv",
    "autopipeline-benchmarks/github-pipelines/length4_44/test_2.csv",
    "autopipeline-benchmarks/github-pipelines/length4_44/test_3.csv"
]

# Target schema columns in correct order
target_columns = ['org_salary_period', 'title', 'company', 'location', 'summary', 'salary', 'href', 'rate', 'reviews']

# Container for processed DataFrames
dfs = []

for path in source_paths:
    # Load source file, ignore the index column (index_col=0)
    df = pd.read_csv(path, index_col=0)
    
    # Reorder columns to match target schema order
    # Source columns: ['title', 'company', 'location', 'summary', 'salary', 'href', 'rate', 'reviews', 'org_salary_period']
    # Target columns: ['org_salary_period', 'title', 'company', 'location', 'summary', 'salary', 'href', 'rate', 'reviews']
    df = df[['org_salary_period', 'title', 'company', 'location', 'summary', 'salary', 'href', 'rate', 'reviews']]
    
    # Clean and convert columns:
    # Convert 'org_salary_period' to string explicitly (object dtype)
    df['org_salary_period'] = df['org_salary_period'].astype(str)
    
    # Columns to convert to numeric (may have strings with commas or floats)
    # 'title', 'company', 'location', 'summary', 'salary', 'rate', 'reviews'
    # From data examples, title, company, location, summary are text in sources but target expects integer
    # Checking target examples: 'title', 'company', 'location', 'summary' columns are integers with values like 23, 378, etc.
    # So conversion required is probably the count of rows per group org_salary_period? But here target examples are summary counts,
    # However, prompt says just produce union, no aggregation is needed.
    # Wait, source columns: title,company,... are text fields but target expects int.
    # This means target is an aggregation of counts per org_salary_period for each field? Because target examples:
    # row 0: day   23 23 23 23 23 23 23 23
    # So the integer seems to be a count of entries per org_salary_period for these fields.
    #
    # Therefore we need to count number of entries per org_salary_period and per each field? 
    # Since all rows have multiple text entries, and target shows counts.
    #
    # That means for the transformation:
    # For each org_salary_period value, count how many non-null entries present in each of title, company, location, summary, salary, href, rate, reviews.
    #
    # So we have to group by org_salary_period, aggregate counts for each column.
    #
    # Adjust plan now:
    # 1. Concatenate all source dfs together first (after fixing reviews and rate columns to numeric)
    # 2. Then group by org_salary_period
    # 3. Count number of non-null values for each column except org_salary_period
    
    # So in the current loop, we just clean columns and convert rate, reviews to numeric, remove commas and convert to number
    
    # Clean 'rate' and 'reviews' columns:
    for col in ['rate', 'reviews']:
        # Remove commas from strings and convert to numeric
        df[col] = df[col].astype(str).str.replace(',', '', regex=False)
        df[col] = pd.to_numeric(df[col], errors='coerce')
    
    # 'salary' should be numeric (float or int)
    df['salary'] = pd.to_numeric(df['salary'], errors='coerce')
    
    # For other columns ('title', 'company', 'location', 'summary', 'href'):
    # they are text columns according to source, and target expects integer counts (aggregated)
    # so keep them as string for now
    
    dfs.append(df)

# Concatenate all source dataframes row-wise
all_data = pd.concat(dfs, ignore_index=True)

# Drop rows where org_salary_period is null or empty because it is group by key
all_data = all_data[all_data['org_salary_period'].notna() & (all_data['org_salary_period'] != '')]

# For grouping and aggregation
# Count non-null entries per group org_salary_period for each of these columns:
# ['title', 'company', 'location', 'summary', 'salary', 'href', 'rate', 'reviews']
# Note: 'href' is string, so count the number of non-null non-empty href values per group

# But counting non-null on 'salary', 'rate', 'reviews' will give count of non-null entries, but salary etc are numeric,
# target examples have the same number for all columns per period. So assume count of non-null entries per column.

# To replicate target example format: counts per org_salary_period per column

agg_dict = {
    'title': lambda x: x.notna().sum(),
    'company': lambda x: x.notna().sum(),
    'location': lambda x: x.notna().sum(),
    'summary': lambda x: x.notna().sum(),
    'salary': lambda x: x.notna().sum(),
    'href': lambda x: x.notna().sum(),
    'rate': lambda x: x.notna().sum(),
    'reviews': lambda x: x.notna().sum()
}

# Perform groupby aggregation
result = all_data.groupby('org_salary_period').agg(agg_dict).reset_index()

# Reorder columns to target schema (should already match)
result = result[target_columns]

# Ensure all columns except 'org_salary_period' are int type
for col in target_columns:
    if col != 'org_salary_period':
        result[col] = result[col].astype(int)

# Write the transformed table to the output CSV file with index=False (no row index)
result.to_csv("autopipeline-benchmarks/github-pipelines/length4_44/target_multisource_cot.csv", index=False)
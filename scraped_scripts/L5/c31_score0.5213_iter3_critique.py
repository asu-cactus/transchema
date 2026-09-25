import pandas as pd
import re

paths = [
    "autopipeline-benchmarks/github-pipelines/length5_31/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length5_31/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length5_31/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length5_31/training_3.csv",
    "autopipeline-benchmarks/github-pipelines/length5_31/training_4.csv"
]

dfs = [pd.read_csv(p, index_col=0) for p in paths]

df_all = pd.concat(dfs, ignore_index=True)

# Convert GEO.id to string (already string)
df_all['GEO.id'] = df_all['GEO.id'].astype(str)

# Convert GEO.id2 to integer
df_all['GEO.id2'] = pd.to_numeric(df_all['GEO.id2'], errors='coerce').astype('Int64')

# Extract integer from GEO.display-label string, e.g. "ZCTA5 91932" -> 5
def extract_display_label_int(s):
    # Try to find the first integer in the string after "ZCTA"
    # The source examples show "ZCTA5 91932", so extract the 5
    match = re.search(r'ZCTA(\d+)', s)
    if match:
        return int(match.group(1))
    else:
        # fallback: try to extract any integer in the string
        nums = re.findall(r'\d+', s)
        if nums:
            return int(nums[0])
        else:
            return pd.NA

df_all['GEO.display-label'] = df_all['GEO.display-label'].astype(str).map(extract_display_label_int).astype('Int64')

# Convert HD01_VD01 and HD02_VD01 to integer, fill NaN with 0
df_all['HD01_VD01'] = pd.to_numeric(df_all['HD01_VD01'], errors='coerce').fillna(0).astype(int)
df_all['HD02_VD01'] = pd.to_numeric(df_all['HD02_VD01'], errors='coerce').fillna(0).astype(int)

# Convert Year to integer
df_all['Year'] = pd.to_numeric(df_all['Year'], errors='coerce').astype('Int64')

# Write output with columns in target schema order
df_all = df_all[['GEO.id', 'GEO.id2', 'GEO.display-label', 'HD01_VD01', 'HD02_VD01', 'Year']]

df_all.to_csv("autopipeline-benchmarks/github-pipelines/length5_31/target_multisource_mcts.csv", index=False)
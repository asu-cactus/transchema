import pandas as pd

paths = [
    "autopipeline-benchmarks/github-pipelines/length5_31/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length5_31/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length5_31/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length5_31/training_3.csv",
    "autopipeline-benchmarks/github-pipelines/length5_31/training_4.csv"
]

dfs = [pd.read_csv(p, index_col=0) for p in paths]
union_df = pd.concat(dfs, ignore_index=True)

# Convert numeric columns safely
union_df['HD01_VD01'] = pd.to_numeric(union_df['HD01_VD01'], errors='coerce').fillna(0).astype(int)
union_df['HD02_VD01'] = pd.to_numeric(union_df['HD02_VD01'], errors='coerce').fillna(0).astype(int)
union_df['Year'] = pd.to_numeric(union_df['Year'], errors='coerce').fillna(0).astype(int)
union_df['GEO.id2'] = pd.to_numeric(union_df['GEO.id2'], errors='coerce').fillna(0).astype(int)

# Convert GEO.display-label from string like "ZCTA5 91932" to integer 5 (digit after "ZCTA")
# Extract the digit after "ZCTA" prefix
def extract_display_label(val):
    if isinstance(val, str) and val.startswith("ZCTA"):
        # Extract digits after "ZCTA" prefix until first space or end
        # The examples show "ZCTA5 91932", so we take the digit after "ZCTA"
        # which is the 5 in "ZCTA5"
        # So extract the character at position 4 (0-based)
        try:
            return int(val[4])
        except:
            return 0
    else:
        return 0

union_df['GEO.display-label'] = union_df['GEO.display-label'].apply(extract_display_label).astype(int)

# Group by the three key columns
agg = union_df.groupby(['GEO.id', 'GEO.id2', 'GEO.display-label'], as_index=False).agg({
    'HD01_VD01': 'sum',
    'HD02_VD01': 'sum',
    'Year': 'max'
})

# Ensure types match target schema
agg['GEO.id'] = agg['GEO.id'].astype(str)
agg['GEO.id2'] = agg['GEO.id2'].astype(int)
agg['GEO.display-label'] = agg['GEO.display-label'].astype(int)
agg['HD01_VD01'] = agg['HD01_VD01'].astype(int)
agg['HD02_VD01'] = agg['HD02_VD01'].astype(int)
agg['Year'] = agg['Year'].astype(int)

agg.to_csv("autopipeline-benchmarks/github-pipelines/length5_31/target_multisource_mcts.csv", index=False)
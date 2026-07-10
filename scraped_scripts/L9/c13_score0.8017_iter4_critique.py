import pandas as pd

# File paths
paths = [
    "autopipeline-benchmarks/github-pipelines/length9_13/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length9_13/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length9_13/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length9_13/training_3.csv",
    "autopipeline-benchmarks/github-pipelines/length9_13/training_4.csv",
    "autopipeline-benchmarks/github-pipelines/length9_13/training_5.csv",
    "autopipeline-benchmarks/github-pipelines/length9_13/training_6.csv",
    "autopipeline-benchmarks/github-pipelines/length9_13/training_7.csv",
    "autopipeline-benchmarks/github-pipelines/length9_13/training_8.csv",
    "autopipeline-benchmarks/github-pipelines/length9_13/training_9.csv",
]

# Read all sources with index_col=0 to ignore the first index column
dfs = [pd.read_csv(p, index_col=0) for p in paths]

# Rename columns of each dataframe to add suffixes matching target schema pattern
# The target schema has suffixes like _x, _y, _x_37, _y_55, etc.
# We will assign suffixes in order: _x, _y, _x_37, _y_55, _x_73, _y_91, _x_109, _y_127, _x_145, _y_163
# The first two sources get _x and _y, then the rest get suffixes with increasing numbers.

suffixes = [
    "_x",
    "_y",
    "_x_37",
    "_y_55",
    "_x_73",
    "_y_91",
    "_x_109",
    "_y_127",
    "_x_145",
    "_y_163",
]

# Columns to keep as join keys (no suffix)
join_keys = ['Date', 'Jour']

# For each df, rename all columns except join keys by adding suffix
renamed_dfs = []
for df, suf in zip(dfs, suffixes):
    rename_dict = {col: col + suf for col in df.columns if col not in join_keys}
    renamed_dfs.append(df.rename(columns=rename_dict))

# Now perform successive merges on ['Date', 'Jour'] with outer join to keep all rows
from functools import reduce

def merge_two(left, right):
    return pd.merge(left, right, on=join_keys, how='outer')

merged_df = reduce(merge_two, renamed_dfs)

# The target schema has 'Date' and multiple 'Jour_x', 'Jour_y', etc.
# We currently have only one 'Jour' column (join key).
# To match target schema exactly, we need to replicate 'Jour' columns for each source as in target.

# The target schema shows 'Jour_x', 'Jour_y', 'Jour_x_37', 'Jour_y_55', etc.
# So for each suffix, create a 'Jour' column with that suffix by copying the join key 'Jour'

for suf in suffixes:
    merged_df['Jour' + suf] = merged_df['Jour']

# Similarly for 'Date', target schema only has one 'Date' column (no suffix), so keep as is.

# The target schema also has 'Chaine_x', 'Chaine_y', etc. which are already present from renaming.

# Drop the original 'Jour' column (without suffix) as target schema does not have it standalone
merged_df = merged_df.drop(columns=['Jour'])

# Reorder columns to match target schema order exactly:
# Target schema leftmost columns: 'Date', 'Jour_x', 'Chaine_x', 'Heure_prgm1_x', ...
# We will build columns list accordingly.

# Get the base columns (excluding join keys)
base_cols = [col for col in dfs[0].columns if col not in join_keys]

# Build final columns list:
final_cols = ['Date']
for suf in suffixes:
    # Add 'Jour' with suffix
    final_cols.append('Jour' + suf)
    # Add all base columns with suffix
    for col in base_cols:
        final_cols.append(col + suf)

# Select columns in this order
merged_df = merged_df[final_cols]

# Fix data types to match target schema:
# From target schema info:
# 'Date': string
# 'Jour_x': string
# 'Chaine_x': string
# 'Heure_prgm1_x': float
# 'Titre_prgm1_x': string
# 'Type_prgm1_x': string
# 'Duree_prgm1_x': integer
# 'Nbre_episodes_prgm1_x': integer
# 'Age_conseille_prgm1_x': string
# 'Heure_prgm2_x': float
# 'Titre_prgm2_x': string
# 'Type_prgm2_x': string
# 'Duree_prgm2_x': float
# 'Nbre_episodes_prgm2_x': integer
# 'Age_conseille_prgm2_x': string
# 'Part_de_marche_x': float or string (some sources have string, target mostly float)
# 'Annee_x': integer
# 'Mois_x': string
# 'Week end_x': integer

# Define expected dtypes for base columns (without suffix)
expected_dtypes = {
    'Date': 'string',
    'Jour': 'string',
    'Chaine': 'string',
    'Heure_prgm1': 'float64',
    'Titre_prgm1': 'string',
    'Type_prgm1': 'string',
    'Duree_prgm1': 'Int64',  # nullable integer
    'Nbre_episodes_prgm1': 'Int64',
    'Age_conseille_prgm1': 'string',
    'Heure_prgm2': 'float64',
    'Titre_prgm2': 'string',
    'Type_prgm2': 'string',
    'Duree_prgm2': 'float64',
    'Nbre_episodes_prgm2': 'Int64',
    'Age_conseille_prgm2': 'string',
    'Part_de_marche': 'float64',  # some sources have string, try to convert
    'Annee': 'Int64',
    'Mois': 'string',
    'Week end': 'Int64',
}

# Convert columns accordingly for each suffix
for suf in suffixes:
    for col, dtype in expected_dtypes.items():
        col_name = col + suf if col != 'Date' else 'Date'  # Date has no suffix
        if col_name in merged_df.columns:
            if dtype == 'string':
                merged_df[col_name] = merged_df[col_name].astype('string')
            elif dtype == 'Int64':
                # Convert to nullable integer
                merged_df[col_name] = pd.to_numeric(merged_df[col_name], errors='coerce').astype('Int64')
            elif dtype == 'float64':
                # Convert to float
                merged_df[col_name] = pd.to_numeric(merged_df[col_name], errors='coerce').astype('float64')

# Save to CSV with exact column names
merged_df.to_csv("autopipeline-benchmarks/github-pipelines/length9_13/target_multisource_mcts.csv", index=False)
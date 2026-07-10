import pandas as pd

paths = [
    "autopipeline-benchmarks/github-pipelines/length5_32/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length5_32/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length5_32/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length5_32/training_3.csv",
    "autopipeline-benchmarks/github-pipelines/length5_32/training_4.csv",
    "autopipeline-benchmarks/github-pipelines/length5_32/training_5.csv",
]

dfs = []
for i, path in enumerate(paths):
    df = pd.read_csv(path, index_col=0)
    # Rename columns to avoid collision and match target schema pattern
    # Each source has columns: CountyID, CountyName, <pop_column>, Year, ID
    # We rename columns to match the target schema columns for each source:
    # Source0: asian_population -> asian_population, columns suffix _x_17, _x_18, etc.
    # Source1: aian_population
    # Source2: black_population
    # Source3: whites_population
    # Source4: mixed_population
    # Source5: other_population

    pop_col_map = {
        0: "asian_population",
        1: "aian_population",
        2: "black_population",
        3: "whites_population",
        4: "mixed_population",
        5: "other_population",
    }
    pop_col = pop_col_map[i]

    # Rename columns to target schema columns with suffixes as per target schema:
    # The target schema has groups of columns for each population type with suffixes:
    # For whites_population (source3): CountyID_x, CountyName_x, whites_population, Year_x, ID
    # For other_population (source5): CountyID_y, CountyName_y, other_population, Year_y
    # For mixed_population (source4): CountyID_x_9, CountyName_x_10, mixed_population, Year_x_12
    # For black_population (source2): CountyID_y_13, CountyName_y_14, black_population, Year_y_16
    # For asian_population (source0): CountyID_x_17, CountyName_x_18, asian_population, Year_x_20
    # For aian_population (source1): CountyID_y_21, CountyName_y_22, aian_population, Year_y_24

    rename_map = {}
    if i == 3:  # whites_population
        rename_map = {
            "CountyID": "CountyID_x",
            "CountyName": "CountyName_x",
            pop_col: pop_col,
            "Year": "Year_x",
            "ID": "ID",
        }
    elif i == 5:  # other_population
        rename_map = {
            "CountyID": "CountyID_y",
            "CountyName": "CountyName_y",
            pop_col: pop_col,
            "Year": "Year_y",
        }
    elif i == 4:  # mixed_population
        rename_map = {
            "CountyID": "CountyID_x_9",
            "CountyName": "CountyName_x_10",
            pop_col: pop_col,
            "Year": "Year_x_12",
        }
    elif i == 2:  # black_population
        rename_map = {
            "CountyID": "CountyID_y_13",
            "CountyName": "CountyName_y_14",
            pop_col: pop_col,
            "Year": "Year_y_16",
        }
    elif i == 0:  # asian_population
        rename_map = {
            "CountyID": "CountyID_x_17",
            "CountyName": "CountyName_x_18",
            pop_col: pop_col,
            "Year": "Year_x_20",
        }
    elif i == 1:  # aian_population
        rename_map = {
            "CountyID": "CountyID_y_21",
            "CountyName": "CountyName_y_22",
            pop_col: pop_col,
            "Year": "Year_y_24",
        }

    df = df.rename(columns=rename_map)

    # Keep only the renamed columns (some sources don't have ID column except source3)
    df = df[list(rename_map.values())]

    dfs.append(df)

# Merge all dataframes on ID or on CountyID and Year columns where possible
# But only source3 has ID column, others don't.
# The target schema has ID only once, so we keep ID from source3 (whites_population).
# We will merge on CountyID and Year columns for each population group.

# First, merge all except source3 on CountyID and Year columns (with their respective suffixes)
# Then merge with source3 on ID

# Prepare keys for merging:
# For source3 (whites_population), key is ID
# For others, keys are CountyID and Year with their suffixes

# We will do a full outer join stepwise to keep all data

# Start with source3 (whites_population)
df_whites = dfs[3]

# Merge with other_population (source5)
df_merge = pd.merge(
    df_whites,
    dfs[5],
    left_on=["CountyID_x", "Year_x"],
    right_on=["CountyID_y", "Year_y"],
    how="outer",
)

# Merge with mixed_population (source4)
df_merge = pd.merge(
    df_merge,
    dfs[4],
    left_on=["CountyID_x", "Year_x"],
    right_on=["CountyID_x_9", "Year_x_12"],
    how="outer",
)

# Merge with black_population (source2)
df_merge = pd.merge(
    df_merge,
    dfs[2],
    left_on=["CountyID_x", "Year_x"],
    right_on=["CountyID_y_13", "Year_y_16"],
    how="outer",
)

# Merge with asian_population (source0)
df_merge = pd.merge(
    df_merge,
    dfs[0],
    left_on=["CountyID_x", "Year_x"],
    right_on=["CountyID_x_17", "Year_x_20"],
    how="outer",
)

# Merge with aian_population (source1)
df_merge = pd.merge(
    df_merge,
    dfs[1],
    left_on=["CountyID_x", "Year_x"],
    right_on=["CountyID_y_21", "Year_y_24"],
    how="outer",
)

# The target schema columns order:
target_columns = [
    "CountyID_x",
    "CountyName_x",
    "whites_population",
    "Year_x",
    "ID",
    "CountyID_y",
    "CountyName_y",
    "other_population",
    "Year_y",
    "CountyID_x_9",
    "CountyName_x_10",
    "mixed_population",
    "Year_x_12",
    "CountyID_y_13",
    "CountyName_y_14",
    "black_population",
    "Year_y_16",
    "CountyID_x_17",
    "CountyName_x_18",
    "asian_population",
    "Year_x_20",
    "CountyID_y_21",
    "CountyName_y_22",
    "aian_population",
    "Year_y_24",
]

# Some columns may be missing due to outer joins, add them if missing
for col in target_columns:
    if col not in df_merge.columns:
        df_merge[col] = pd.NA

df_merge = df_merge[target_columns]

df_merge.to_csv(
    "autopipeline-benchmarks/github-pipelines/length5_32/target_multisource_mcts.csv",
    index=False,
)
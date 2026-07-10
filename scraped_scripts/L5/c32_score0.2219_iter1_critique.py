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
    pop_col_map = {
        0: "asian_population",
        1: "aian_population",
        2: "black_population",
        3: "whites_population",
        4: "mixed_population",
        5: "other_population",
    }
    pop_col = pop_col_map[i]

    # Rename columns to match target schema exactly
    if i == 3:  # whites_population
        rename_map = {
            "CountyID": "CountyID_x",
            "CountyName": "CountyName_x",
            pop_col: "whites_population",
            "Year": "Year_x",
            "ID": "ID",
        }
    elif i == 5:  # other_population
        rename_map = {
            "CountyID": "CountyID_y",
            "CountyName": "CountyName_y",
            pop_col: "other_population",
            "Year": "Year_y",
        }
    elif i == 4:  # mixed_population
        rename_map = {
            "CountyID": "CountyID_x_9",
            "CountyName": "CountyName_x_10",
            pop_col: "mixed_population",
            "Year": "Year_x_12",
        }
    elif i == 2:  # black_population
        rename_map = {
            "CountyID": "CountyID_y_13",
            "CountyName": "CountyName_y_14",
            pop_col: "black_population",
            "Year": "Year_y_16",
        }
    elif i == 0:  # asian_population
        rename_map = {
            "CountyID": "CountyID_x_17",
            "CountyName": "CountyName_x_18",
            pop_col: "asian_population",
            "Year": "Year_x_20",
        }
    elif i == 1:  # aian_population
        rename_map = {
            "CountyID": "CountyID_y_21",
            "CountyName": "CountyName_y_22",
            pop_col: "aian_population",
            "Year": "Year_y_24",
        }

    df = df.rename(columns=rename_map)
    df = df[list(rename_map.values())]
    dfs.append(df)

# Start merging from whites_population (source3)
df_merge = dfs[3]

# Merge with other_population (source5)
df_merge = pd.merge(
    df_merge,
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

# Ensure all target columns exist
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

for col in target_columns:
    if col not in df_merge.columns:
        df_merge[col] = pd.NA

# Group by the leftmost key columns to remove duplicates and aggregate populations by sum
group_by_cols = ["CountyID_x", "CountyName_x", "Year_x", "ID"]

agg_cols = [
    "whites_population",
    "other_population",
    "mixed_population",
    "black_population",
    "asian_population",
    "aian_population",
]

# For columns that are keys or names with suffixes, keep first non-null value
first_cols = [
    "CountyID_y",
    "CountyName_y",
    "Year_y",
    "CountyID_x_9",
    "CountyName_x_10",
    "Year_x_12",
    "CountyID_y_13",
    "CountyName_y_14",
    "Year_y_16",
    "CountyID_x_17",
    "CountyName_x_18",
    "Year_x_20",
    "CountyID_y_21",
    "CountyName_y_22",
    "Year_y_24",
]

agg_dict = {col: "sum" for col in agg_cols}
agg_dict.update({col: "first" for col in first_cols})

df_final = df_merge.groupby(group_by_cols, dropna=False, as_index=False).agg(agg_dict)

# Reorder columns to match target schema exactly
df_final = df_final[target_columns]

df_final.to_csv(
    "autopipeline-benchmarks/github-pipelines/length5_32/target_multisource_mcts.csv",
    index=False,
)
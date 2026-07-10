import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_48/training_0.csv", index_col=0)

df = df0.copy()

# Convert WarNum to WarID (int)
df["WarID"] = df["WarNum"].astype("Int64")

# Initiator as string
df["Initiator"] = df["Initiator"].astype(str)

# PolityID from CcodeA (int)
df["PolityID"] = pd.to_numeric(df["CcodeA"], errors='coerce').astype("Int64")

# PolityName from SideA (convert to int if possible, else NaN)
df["PolityName"] = pd.to_numeric(df["SideA"], errors='coerce').astype("Int64")

# Functions to choose start and end dates from first or second period
def choose_start_month(row):
    if pd.notna(row["StartMonth1"]):
        return row["StartMonth1"]
    elif pd.notna(row["StartMonth2"]):
        return row["StartMonth2"]
    else:
        return pd.NA

def choose_start_day(row):
    if pd.notna(row["StartDay1"]):
        return row["StartDay1"]
    elif pd.notna(row["StartDay2"]):
        return row["StartDay2"]
    else:
        return pd.NA

def choose_start_year(row):
    if pd.notna(row["StartYear1"]):
        return row["StartYear1"]
    elif pd.notna(row["StartYear2"]):
        return row["StartYear2"]
    else:
        return pd.NA

def choose_end_month(row):
    if pd.notna(row["EndMonth1"]):
        return row["EndMonth1"]
    elif pd.notna(row["EndMonth2"]):
        return row["EndMonth2"]
    else:
        return pd.NA

def choose_end_day(row):
    if pd.notna(row["EndDay1"]):
        return row["EndDay1"]
    elif pd.notna(row["EndDay2"]):
        return row["EndDay2"]
    else:
        return pd.NA

def choose_end_year(row):
    if pd.notna(row["EndYear1"]):
        return row["EndYear1"]
    elif pd.notna(row["EndYear2"]):
        return row["EndYear2"]
    else:
        return pd.NA

df["StartMonth"] = df.apply(choose_start_month, axis=1)
df["StartDay"] = df.apply(choose_start_day, axis=1)
df["StartYear"] = df.apply(choose_start_year, axis=1)
df["EndMonth"] = df.apply(choose_end_month, axis=1)
df["EndDay"] = df.apply(choose_end_day, axis=1)
df["EndYear"] = df.apply(choose_end_year, axis=1)

# Outcome as int
df["Outcome"] = pd.to_numeric(df["Outcome"], errors='coerce').astype("Int64")

# Deaths = sum of SideADeaths and SideBDeaths (treat NaN as 0)
side_a_deaths = pd.to_numeric(df["SideADeaths"], errors='coerce').fillna(0)
side_b_deaths = pd.to_numeric(df["SideBDeaths"], errors='coerce').fillna(0)
df["Deaths"] = (side_a_deaths + side_b_deaths).astype("Int64")

# Group by Initiator, WarID, PolityID
group_cols = ["Initiator", "WarID", "PolityID"]

agg_dict = {
    "PolityName": "first",
    "StartMonth": "first",
    "StartDay": "first",
    "StartYear": "first",
    "EndMonth": "first",
    "EndDay": "first",
    "EndYear": "first",
    "Outcome": "first",
    "Deaths": "sum"
}

result = df.groupby(group_cols, dropna=False, as_index=False).agg(agg_dict)

# Ensure columns are in target schema order
result = result[[
    "Initiator",
    "WarID",
    "PolityID",
    "PolityName",
    "StartMonth",
    "StartDay",
    "StartYear",
    "EndMonth",
    "EndDay",
    "EndYear",
    "Outcome",
    "Deaths"
]]

# Cast integer columns to Int64 to keep nullable integer dtype
int_cols = ["WarID", "PolityID", "PolityName", "StartMonth", "StartDay", "StartYear",
            "EndMonth", "EndDay", "EndYear", "Outcome", "Deaths"]
for col in int_cols:
    result[col] = pd.to_numeric(result[col], errors='coerce').astype("Int64")

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_48/target_multisource_mcts.csv", index=False)
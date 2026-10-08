import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_62/training_0.csv", index_col=0)

# Convert 'Value Date' from format 'Mon-YY' to 'Mon_YYYY'
# For example, 'Jul-07' -> 'Jul_2007'
def convert_value_date(val):
    # val example: 'Jul-07'
    mon, yr = val.split('-')
    yr = int(yr)
    # Assume years 00-99 map to 2000-2099
    yr += 2000
    return f"{mon}_{yr}"

df0["Month"] = df0["Value Date"].map(convert_value_date)

grouped = df0.groupby("Month", as_index=False).agg({"Water Use": "sum", "Power Use": "sum"})

# Ensure types match target schema
grouped["Water Use"] = grouped["Water Use"].astype(float)
grouped["Power Use"] = grouped["Power Use"].astype(int)

grouped.to_csv("autopipeline-benchmarks/github-pipelines/length1_62/target_multisource_mcts.csv", index=False)
import pandas as pd

paths = [
    "autopipeline-benchmarks/github-pipelines/length3_67/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length3_67/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length3_67/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length3_67/training_3.csv",
]

dfs = [pd.read_csv(p, index_col=0) for p in paths]

df_all = pd.concat(dfs, ignore_index=True)

agg = df_all.groupby("Wrestler", as_index=False).agg({
    "Wins": "sum",
    "Losses": "sum",
    "Draws": "sum"
})

years = [2013, 2014, 2015, 2016]
result = agg.copy()
for year in years[1:]:
    # For years after 2013, add columns with zeros (no data in sources)
    result[f"{year} Wins"] = 0
    result[f"{year} Losses"] = 0
    result[f"{year} Draws"] = 0

# Rename 2013 columns to match target schema
result = result.rename(columns={
    "Wins": "2013 Wins",
    "Losses": "2013 Losses",
    "Draws": "2013 Draws"
})

# Reorder columns to match target schema
cols = ["Wrestler"]
for year in years:
    cols.extend([f"{year} Wins", f"{year} Losses", f"{year} Draws"])
result = result[cols]

result.to_csv("autopipeline-benchmarks/github-pipelines/length3_67/target_multisource_mcts.csv", index=False)
import pandas as pd

# Read sources
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_62/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_62/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_62/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_62/training_3.csv", index_col=0)

# Add Year column to each source according to the target schema order
df0["Year"] = 2013
df1["Year"] = 2014
df2["Year"] = 2015
df3["Year"] = 2016

# UNION all sources
df_all = pd.concat([df0, df1, df2, df3], ignore_index=True)

# GROUP BY Wrestler and Year, sum Wins, Losses, Draws (in case of duplicates)
df_grouped = df_all.groupby(["Wrestler", "Year"], as_index=False).agg({"Wins":"sum", "Losses":"sum", "Draws":"sum"})

# Pivot the table to get columns for each year and metric
df_pivot_wins = df_grouped.pivot(index="Wrestler", columns="Year", values="Wins")
df_pivot_losses = df_grouped.pivot(index="Wrestler", columns="Year", values="Losses")
df_pivot_draws = df_grouped.pivot(index="Wrestler", columns="Year", values="Draws")

# Rename columns to match target schema
df_pivot_wins.columns = [f"{year} Wins" for year in df_pivot_wins.columns]
df_pivot_losses.columns = [f"{year} Losses" for year in df_pivot_losses.columns]
df_pivot_draws.columns = [f"{year} Draws" for year in df_pivot_draws.columns]

# Combine all pivoted dataframes
df_final = pd.concat([df_pivot_wins, df_pivot_losses, df_pivot_draws], axis=1)

# Reset index to bring Wrestler back as a column
df_final = df_final.reset_index()

# Fill NaN with 0 and convert to int for all columns except Wrestler
int_cols = [col for col in df_final.columns if col != "Wrestler"]
df_final[int_cols] = df_final[int_cols].fillna(0).astype(int)

# Reorder columns to match target schema exactly
target_columns = ['Wrestler',
                  '2013 Wins', '2013 Losses', '2013 Draws',
                  '2014 Wins', '2014 Losses', '2014 Draws',
                  '2015 Wins', '2015 Losses', '2015 Draws',
                  '2016 Wins', '2016 Losses', '2016 Draws']

df_final = df_final[target_columns]

# Write output
df_final.to_csv("autopipeline-benchmarks/github-pipelines/length3_62/target_multisource_mcts.csv", index=False)
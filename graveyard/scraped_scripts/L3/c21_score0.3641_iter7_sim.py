import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_21/training_0.csv", index_col=0)
pivot_result_0 = df0.pivot_table(index='Country', columns='dt', values='AverageTemperature').reset_index()

# The target schema requires 'Country', 'AverageTemperature_x', 'AverageTemperature_y'
# The partial plan suggests two pivots, but only one source is given.
# We must produce two columns AverageTemperature_x and AverageTemperature_y from the single source by pivoting twice on different dt values or similar.
# However, only one source is given, so we interpret the two pivots as pivoting twice on different dt values or splitting the data.

# Since only one source is given, and the target has two AverageTemperature columns, we can pivot twice on two different dt values or two different subsets.

# Let's create two pivot tables for two different dt values (e.g., earliest and latest date) to produce two columns.

# Extract two distinct dt values to pivot on:
dt_values = df0['dt'].dropna().unique()
if len(dt_values) < 2:
    # If less than 2 distinct dt, just duplicate the column
    df_pivot_x = df0[df0['dt'] == dt_values[0]].set_index('Country')['AverageTemperature'].rename('AverageTemperature_x')
    df_pivot_y = df0[df0['dt'] == dt_values[0]].set_index('Country')['AverageTemperature'].rename('AverageTemperature_y')
else:
    dt_x, dt_y = dt_values[0], dt_values[1]
    df_pivot_x = df0[df0['dt'] == dt_x].set_index('Country')['AverageTemperature'].rename('AverageTemperature_x')
    df_pivot_y = df0[df0['dt'] == dt_y].set_index('Country')['AverageTemperature'].rename('AverageTemperature_y')

result = pd.concat([df_pivot_x, df_pivot_y], axis=1).reset_index()

result.to_csv("autopipeline-benchmarks/github-pipelines/length3_21/target_multisource_mcts.csv", index=False)
import pandas as pd

# Step 1: Load Source4_18_0
source1 = pd.read_csv('Source4_18_0.csv', index_col=0)

# Step 2: Load Source4_18_1
source2 = pd.read_csv('Source4_18_1.csv', index_col=0)

# Step 3: Combine the two sources
combined = pd.concat([source1, source2], ignore_index=True)

# Step 4: Group by 'area_of_shot' and aggregate
grouped = combined.groupby('area_of_shot').agg(
    area_shot_sum=('is_goal', 'count'),
    is_goal_count=('is_goal', 'sum')
).reset_index()

# Step 5: Calculate 'is_goal'
grouped['is_goal'] = grouped['is_goal_count'] / grouped['area_shot_sum']

# Step 6: Select and reorder columns
result = grouped[['area_of_shot', 'is_goal', 'area_shot_sum', 'is_goal_count']]

# Step 7: Save the resulting DataFrame to a CSV file
result.to_csv('target_output.csv', index=False)
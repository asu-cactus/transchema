import pandas as pd

src_path = 'autopipeline-benchmarks/github-pipelines/length1_75/test_0.csv'
dst_path = 'autopipeline-benchmarks/github-pipelines/length1_75/target_multisource_mcts_recovery_test_val.csv'

df = pd.read_csv(src_path, index_col=0)
grouped = df.groupby('neighbourhood').size().reset_index(name='count')

result = grouped[['neighbourhood']].copy()
result['count'] = grouped['count'].astype(int)

for col in ['id', 'name', 'host_id', 'host_name', 'neighbourhood_group', 'latitude', 
            'longitude', 'room_type', 'price', 'minimum_nights', 'number_of_reviews',
            'last_review', 'reviews_per_month', 'calculated_host_listings_count', 
            'availability_365']:
    result[col] = result['count'].values

result.drop(columns=['count'], inplace=True)
result.to_csv(dst_path, index=False)
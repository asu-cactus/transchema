import pandas as pd
import os
from imblearn.over_sampling import SMOTE
from itertools import combinations

# Function to calculate distinct-value-ratio
def distinct_value_ratio(col, total_rows):
    return len(col.unique()) / total_rows

# Function to calculate Jaccard similarity
def jaccard_similarity(col1, col2):
    set1, set2 = set(col1), set(col2)
    return len(set1 & set2) / len(set1 | set2)

# Function to calculate Jaccard containment
def jaccard_containment(col1, col2):
    set1, set2 = set(col1), set(col2)
    return len(set1 & set2) / min(len(set1), len(set2))

# Function to calculate value-range-overlap
def value_range_overlap(col1, col2):
    if pd.api.types.is_numeric_dtype(col1) and pd.api.types.is_numeric_dtype(col2):
        range1 = col1.max() - col1.min()
        range2 = col2.max() - col2.min()
        intersection = min(col1.max(), col2.max()) - max(col1.min(), col2.min())
        union = range1 + range2 - intersection
        print(range1,range2,intersection,union)
        return max(0, intersection / union)
    return 0

# Function to get column type
def column_type(col):
    return str(col.dtype)

# Function to calculate left-ness
def leftness(pos, total_columns):
    return 1 - (pos / total_columns)

# Function to check if column is sorted
def is_sorted(col):
    return int((col.values == col.sort_values().values).all())

# Function to check if single column candidate
def is_single_column(candidate):
    return int(len(candidate) == 1)

# Function to calculate table-level statistics
def table_level_statistics(table1, table2):
    rows_table1 = len(table1)
    rows_table2 = len(table2)
    row_count_ratio = rows_table1 / rows_table2 if rows_table2 != 0 else 0
    return rows_table1, rows_table2, row_count_ratio

# Function to calculate prefix overlap
def prefix_overlap(col1, col2):
    if col1.dtype != object:
        col1 = col1.astype(str)
    if col2.dtype != object:
        col2 = col2.astype(str)
    prefix1 = col1.str.extract(r'^(\D+)', expand=False).dropna().unique()
    prefix2 = col2.str.extract(r'^(\D+)', expand=False).dropna().unique()
    set1, set2 = set(prefix1), set(prefix2)
    return len(set1 & set2) / len(set1 | set2) if set1 and set2 else 0

# Generate features for a pair of columns
def generate_features(col1, col2, table1, table2, pos1, pos2, total_columns1, total_columns2, is_single_col):
    features = [
        distinct_value_ratio(col1, len(table1)),
        distinct_value_ratio(col2, len(table2)),
        jaccard_similarity(col1, col2),
        jaccard_containment(col1, col2),
        value_range_overlap(col1, col2),
        column_type(col1) == column_type(col2),
        leftness(pos1, total_columns1),
        leftness(pos2, total_columns2),
        is_sorted(col1),
        is_sorted(col2),
        is_single_col,
        prefix_overlap(col1, col2)
    ]
    rows_table1, rows_table2, row_count_ratio = table_level_statistics(table1, table2)
    features.extend([rows_table1, rows_table2, row_count_ratio])
    return features

# Prepare the dataset
def prepare_dataset(tables, join_labels):
    features = []
    labels = []

    for table_name1, table_name2 in combinations(tables.keys(), 2):
        table1 = tables[table_name1]
        table2 = tables[table_name2]
        columns1 = table1.columns
        columns2 = table2.columns
        total_columns1 = len(columns1)
        total_columns2 = len(columns2)

        for col1, col2 in join_labels.get((table_name1, table_name2), []):
            pos1 = columns1.get_loc(col1)
            pos2 = columns2.get_loc(col2)
            features.append(generate_features(table1[col1], table2[col2], table1, table2, pos1, pos2, total_columns1, total_columns2, is_single_column([(col1, col2)])))
            labels.append(1)  # Known join columns are labeled as 1

            # Add negative examples by pairing col1 with other columns in table2 and vice versa
            for other_col in columns2:
                if other_col != col2:
                    pos_other = columns2.get_loc(other_col)
                    features.append(generate_features(table1[col1], table2[other_col], table1, table2, pos1, pos_other, total_columns1, total_columns2, is_single_column([(col1, other_col)])))
                    labels.append(0)  # Non-join columns are labeled as 0
            for other_col in columns1:
                if other_col != col1:
                    pos_other = columns1.get_loc(other_col)
                    features.append(generate_features(table1[other_col], table2[col2], table1, table2, pos_other, pos2, total_columns1, total_columns2, is_single_column([(other_col, col2)])))
                    labels.append(0)  # Non-join columns are labeled as 0

    return pd.DataFrame(features), pd.Series(labels)

# Resample the dataset
def resample_dataset(X, y):
    # Count the number of samples in the minority class
    minority_class_count = y.value_counts().min()
    smote = SMOTE(k_neighbors=min(5, minority_class_count-1))
    X_resampled, y_resampled = smote.fit_resample(X, y)
    return X_resampled, y_resampled

# Read known join labels from a CSV file
def read_join_labels(filename='join_labels.csv'):
    join_labels = {}
    df = pd.read_csv(filename)
    for _, row in df.iterrows():
        table1, col1, table2, col2 = row['Table1'], row['Column1'], row['Table2'], row['Column2']
        if (table1, table2) not in join_labels:
            join_labels[(table1, table2)] = []
        join_labels[(table1, table2)].append((col1, col2))
    return join_labels

# Load multiple tables from a directory
def load_tables(directory):
    tables = {}
    for filename in sorted(os.listdir(directory)):
        if filename.endswith('.csv'):
            table_name = filename.split('.')[0]  # Use the base name without extension
            tables[table_name] = pd.read_csv(os.path.join(directory, filename))
    return tables

# Example usage
if __name__ == '__main__':
    # Load tables
    tables = load_tables('D:/transchema\model\join\data')

    # Read join labels from CSV
    join_labels = read_join_labels('join_labels.csv')

    # Prepare dataset
    X, y = prepare_dataset(tables, join_labels)

    # Resample dataset to handle imbalance
    X_resampled, y_resampled = resample_dataset(X, y)

    X_resampled.to_csv('features_resampled.csv', index=False)
    pd.DataFrame(y_resampled, columns=['label']).to_csv('labels_resampled.csv', index=False)



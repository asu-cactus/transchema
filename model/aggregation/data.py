import pandas as pd
import os
from sklearn.preprocessing import LabelEncoder
from imblearn.over_sampling import SMOTE

# Function to calculate distinct-value-count
def distinct_value_count(col):
    return len(col.unique())

# Function to get column data type
def column_data_type(col):
    return str(col.dtype)

# Function to calculate left-ness
def leftness(pos, total_columns):
    return pos,(pos / total_columns)

# Function to calculate emptiness
def emptiness(col):
    return col.isnull().sum() / len(col)

# Function to calculate value range
def value_range(col):
    if pd.api.types.is_numeric_dtype(col):
        return col.max() - col.min()
    return 0

# Function to calculate ratio of distinct value count to range
def distinct_to_range_ratio(col):
    range_val = value_range(col)
    if range_val != 0:
        return len(col.unique()) / range_val
    return 0

# Function to calculate peak frequency
def peak_frequency(col):
    # return col.value_counts().max() / len(col)
    return col.value_counts().max(), col.value_counts().max() / len(col)

# Generate features for each column in a table
def generate_features_for_column(col, col_name, pos, total_columns, label_encoder):
    features = [
        distinct_value_count(col),
        distinct_value_count(col) / len(col),  # Ratio-based feature
        label_encoder.transform([column_data_type(col)])[0],  # Encode data type
        *leftness(pos, total_columns),
        emptiness(col),
        value_range(col),
        distinct_to_range_ratio(col),
        *peak_frequency(col)
    ]
    return features

# Prepare the dataset for Key prediction
def prepare_key_dataset(tables, key_labels):
    key_features = []
    key_labels_list = []

    # Fit LabelEncoder on all possible data types
    all_data_types = ['int64', 'float64', 'object']  # Add more types if needed
    label_encoder = LabelEncoder()
    label_encoder.fit(all_data_types)

    for table_name, table in tables.items():
        columns = table.columns
        total_columns = len(columns)

        for pos, col_name in enumerate(columns):
            col = table[col_name]

            # Generate features
            features = generate_features_for_column(col, col_name, pos, total_columns, label_encoder)

            # Add features and labels for Key prediction
            key_features.append(features)
            key_labels_list.append(int((table_name, col_name) in key_labels.set_index(['Table', 'Column']).index))

    return pd.DataFrame(key_features), pd.Series(key_labels_list)

# Resample the dataset
def resample_dataset(X, y):
    # Count the number of samples in the minority class
    minority_class_count = y.value_counts().min()
    smote = SMOTE(k_neighbors=min(5, minority_class_count-1))
    X_resampled, y_resampled = smote.fit_resample(X, y)
    return X_resampled, y_resampled

# Read known key labels from a CSV file
def read_labels(filename):
    return pd.read_csv(filename)

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
    tables = load_tables('model/aggregation/data')

    # Read key labels from CSV
    key_labels = read_labels('key_labels.csv')

    # Prepare dataset
    X_key, y_key = prepare_key_dataset(tables, key_labels)

    # Resample dataset to handle imbalance
    X_key_resampled, y_key_resampled = resample_dataset(X_key, y_key)

    X_key_resampled.to_csv('key_features_resampled.csv', index=False)
    pd.DataFrame(y_key_resampled, columns=['label']).to_csv('key_labels_resampled.csv', index=False)

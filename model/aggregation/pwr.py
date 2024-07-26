import pandas as pd
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import accuracy_score
import xgboost as xgb
from sklearn.preprocessing import LabelEncoder

from model.aggregation.data import generate_features_for_column, load_tables, resample_dataset

# Load the dataset
def load_dataset(features_file, labels_file):
    X = pd.read_csv(features_file)
    y = pd.read_csv(labels_file)['label']
    return X, y

def train_model(X, y):
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    model = xgb.XGBClassifier(objective='binary:logistic', eval_metric='logloss')
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    print(f'Accuracy: {accuracy}')
    model.save_model('key_model.json')
    return model

# Load the model
def load_trained_model(filename='key_model.json'):
    model = xgb.XGBClassifier()
    model.load_model(filename)
    return model

# Predict Key columns
def predict_columns(tables, model, label_encoder):
    predictions = []

    for table_name, table in tables.items():
        columns = table.columns
        total_columns = len(columns)

        for pos, col_name in enumerate(columns):
            col = table[col_name]
            features = generate_features_for_column(col, col_name, pos, total_columns, label_encoder)
            features_df = pd.DataFrame([features])
            score = model.predict_proba(features_df)[0][1]
            predictions.append((table_name, col_name, score))

    predictions.sort(key=lambda x: x[2], reverse=True)
    return predictions


# Example usage
if __name__ == '__main__':
    # Load Key dataset
    X_key, y_key = load_dataset('key_features_resampled.csv', 'key_labels_resampled.csv')

    # Train Key model
    key_model = train_model(X_key, y_key)

    # Load tables
    tables = load_tables('D:/transchema\model/aggregation\data_test')

    # Fit LabelEncoder on all possible data types
    all_data_types = ['int64', 'float64', 'object']  # Add more types if needed
    label_encoder = LabelEncoder()
    label_encoder.fit(all_data_types)

    # Predict and rank Key columns
    key_predictions = predict_columns(tables, key_model, label_encoder)
    for table_name, col_name, score in key_predictions:
        print(f'Key Column: {table_name}.{col_name}, Score: {score}')

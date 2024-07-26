import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import xgboost as xgb
from itertools import combinations
from model.join.data import generate_features, load_tables

def load_dataset(features_file='features_resampled.csv', labels_file='labels_resampled.csv'):
    X = pd.read_csv(features_file)
    y = pd.read_csv(labels_file)['label']
    return X, y

# Train the model
def train_model(X, y):
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    model = xgb.XGBClassifier(objective='binary:logistic', eval_metric='logloss')
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    print(f'Accuracy: {accuracy}')
    model.save_model('join_model.json')
    return model

# Load the model
def load_trained_model(filename='join_model.json'):
    model = xgb.XGBClassifier()
    model.load_model(filename)
    return model

# Predict join columns
def predict_join_columns(tables, model):
    candidates = []

    for table_name1, table_name2 in combinations(tables.keys(), 2):
        table1 = tables[table_name1]
        table2 = tables[table_name2]
        columns1 = table1.columns
        columns2 = table2.columns
        total_columns1 = len(columns1)
        total_columns2 = len(columns2)

        for col1 in columns1:
            for col2 in columns2:
                pos1 = columns1.get_loc(col1)
                pos2 = columns2.get_loc(col2)
                features = generate_features(table1[col1], table2[col2], table1, table2, pos1, pos2, total_columns1, total_columns2, 1)  # Here we assume single column candidate
                features_df = pd.DataFrame([features])
                score = model.predict_proba(features_df)[0][1]
                candidates.append(((table_name1, col1), (table_name2, col2), score))

    candidates.sort(key=lambda x: x[2], reverse=True)
    return candidates

# Example usage
if __name__ == '__main__':
    # Load dataset
    X, y = load_dataset()

    # Train model
    model = train_model(X, y)

    # Load tables
    tables = load_tables('D:/transchema\model\join\data_test')

    # Predict and rank join column pairs
    candidates = predict_join_columns(tables, model)
    for (table1, col1), (table2, col2), score in candidates:
        print(f'Columns: {table1}.{col1} and {table2}.{col2}, Score: {score}')

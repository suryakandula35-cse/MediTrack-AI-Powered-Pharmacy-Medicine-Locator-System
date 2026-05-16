import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import joblib
import os

# Define paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATASET_PATH = os.path.join(BASE_DIR, 'Dataset', 'Training.csv')
MODEL_DIR = os.path.join(BASE_DIR, 'ml_model')
MODEL_PATH = os.path.join(MODEL_DIR, 'disease_predictor.pkl')
VECTORIZER_PATH = os.path.join(MODEL_DIR, 'tfidf_vectorizer.pkl')

def train_model():
    """
    Trains a disease prediction model and saves it.
    """
    print("Loading data...")
    try:
        df = pd.read_csv(DATASET_PATH)
    except FileNotFoundError:
        print(f"Error: The dataset was not found at {DATASET_PATH}")
        return

    print("Processing data...")
    # Drop the last unnamed column if it exists
    if 'Unnamed: 133' in df.columns:
        df = df.drop('Unnamed: 133', axis=1)

    # Get symptom column names
    symptom_cols = df.columns.drop('prognosis')

    # For each row, combine the names of symptoms that are present (value of 1)
    symptoms_list = []
    for index, row in df.iterrows():
        symptoms = [col.replace('_', ' ') for col in symptom_cols if row[col] == 1]
        symptoms_list.append(' '.join(symptoms))

    df['symptoms_text'] = symptoms_list

    X = df['symptoms_text']
    y = df['prognosis']

    # Split data for validation
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    print("Training model...")
    # Create and train the TF-IDF vectorizer
    vectorizer = TfidfVectorizer()
    X_train_tfidf = vectorizer.fit_transform(X_train)
    X_test_tfidf = vectorizer.transform(X_test)

    # Train the Logistic Regression model
    model = LogisticRegression(max_iter=1000)
    model.fit(X_train_tfidf, y_train)

    # Evaluate the model
    y_pred = model.predict(X_test_tfidf)
    accuracy = accuracy_score(y_test, y_pred)
    print(f"Model Accuracy: {accuracy * 100:.2f}%")

    print("Saving model and vectorizer...")
    # Save the trained model and vectorizer
    joblib.dump(model, MODEL_PATH)
    joblib.dump(vectorizer, VECTORIZER_PATH)

    print(f"Model saved to {MODEL_PATH}")
    print(f"Vectorizer saved to {VECTORIZER_PATH}")

if __name__ == '__main__':
    train_model()

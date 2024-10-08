import os
from matplotlib import pyplot as plt
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier
from sklearn.pipeline import Pipeline
from sklearn.metrics import accuracy_score, confusion_matrix, precision_score, recall_score, f1_score, classification_report
import pandas as pd
import seaborn as sns
import numpy as np
from sklearn.model_selection import GridSearchCV, train_test_split
from gensim.models import Word2Vec
from nltk.tokenize import sent_tokenize, word_tokenize
import nltk
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.utils.validation import check_is_fitted
from imblearn.pipeline import Pipeline as ImbPipeline
from imblearn.over_sampling import SMOTE


print("Hypertunning with W2V and Greadsearch")

nltk.download('punkt')

# Specify the file path of your CSV file
file_path = "/home/users/elicina/Master-Thesis/Dataset/Cleaned_Dataset.csv"

# Read the CSV file into a DataFrame
df_clean = pd.read_csv(file_path)

# Extract the relevant columns
ticket_data = df_clean['complaint_what_happened_basic_clean_DL']

label_data = df_clean['category_encoded']

# Split the data into training and testing sets
train_texts, test_texts, train_labels, test_labels = train_test_split(ticket_data, label_data, test_size=0.3, random_state=42, shuffle=True)


# Define the Word2Vec transformer
class Word2VecTransformer(BaseEstimator, TransformerMixin):
    def __init__(self, vector_size=100, window=5, min_count=2, workers=4, sg=1):
        self.vector_size = vector_size
        self.window = window
        self.min_count = min_count
        self.workers = workers
        self.sg = sg

    def fit(self, X, y=None):
        data = []
        for text in X:
            for sentence in sent_tokenize(text):
                words = [word.lower() for word in word_tokenize(sentence)]
                data.append(words)
        self.model = Word2Vec(sentences=data, vector_size=self.vector_size, window=self.window, min_count=self.min_count, workers=self.workers, sg = self.sg)
        return self

    def transform(self, X, y=None):
        check_is_fitted(self, 'model')
        embeddings = []
        for text in X:
            tokens = text.split()
            vectors = [self.model.wv[token] for token in tokens if token in self.model.wv]
            if vectors:
                vector = np.mean(vectors, axis=0)
            else:
                vector = np.zeros(self.vector_size)
            embeddings.append(vector)
        return np.array(embeddings)

# Define a custom transformer to print the shape
class ShapePrinter(BaseEstimator, TransformerMixin):
    def fit(self, X, y=None):
        return self

    def transform(self, X, y=None):
        print(f"Shape of dataset after SMOTE: {X.shape}")
        return X

# Define the classifiers to test
classifiers = {
    'RandomForest': RandomForestClassifier(),
    'LogisticRegression': LogisticRegression(max_iter=6000),
    'SVC': SVC()
}

# Define the base pipeline
def create_base_pipeline(classifier):
    return ImbPipeline([
        ('w2v', Word2VecTransformer()),
        ('smote', SMOTE(random_state=42)),
        # ('shape_printer', ShapePrinter()),
        ('clf', classifier)
    ])

# Define grid search parameters for different classifiers
parameters = {
    'RandomForest': {
        'w2v__vector_size': [150, 200, 350],
        'w2v__window': [5, 7, 10],
        'w2v__min_count': [1, 2],
        'w2v__sg': [0, 1],
        'clf__n_estimators': [100,300,700],
        'clf__min_samples_leaf': [5,10,30],
        'clf__max_depth': [None, 20, 30, 40]
    },
    'SVC': {
        'w2v__vector_size': [150, 200, 350],
        'w2v__window': [5, 7, 10],
        'w2v__min_count': [1, 2],
        'w2v__sg': [0, 1],
        'clf__C': [0.01, 1, 10, 100],
        'clf__kernel': ['linear', 'rbf'],
        'clf__gamma': [1, 0.1, 0.001, 0.0001]
    }
}

# Iterate over classifiers
results = []
for clf_name, clf in classifiers.items():
    print(f"Training with {clf_name}...")
    
    # Create the base pipeline for the classifier
    base_pipeline = create_base_pipeline(clf)
    
    # Perform grid search
    gs_clf = GridSearchCV(base_pipeline, parameters[clf_name], n_jobs=-1, cv=5)
    gs_clf.fit(train_texts, train_labels)
    
    # Output the best score and parameters
    best_score = gs_clf.best_score_
    best_params = gs_clf.best_params_
    
    print(f'Best score: {best_score}')
    print(f'Best parameters: {best_params}')

    # Retrieve the best model from RandomizedSearchCV
    best_model = gs_clf.best_estimator_

    # Create the test pipeline without SMOTE
    test_pipeline = Pipeline([
        ('w2v', best_model.named_steps['w2v']), # type: ignore
        ('clf', best_model.named_steps['clf']) # type: ignore
    ])

    # Transform the test data and make predictions
    test_predictions = test_pipeline.predict(test_texts)
    
    # Function to plot confusion matrix
    def plot_confusion_matrix(y_true, y_pred, classes, filename):
        cm = confusion_matrix(y_true, y_pred)
        plt.figure(figsize=(10, 7))
        sns.heatmap(cm, annot=True, fmt="d", cmap="Blues", xticklabels=classes, yticklabels=classes)
        plt.xlabel('Predicted')
        plt.ylabel('Actual')
        plt.title('Confusion Matrix')
        plt.savefig(filename)  # Save the plot to a file
        plt.close()  # Close the plot to prevent it from displaying

    # Evaluate the model performance
    accuracy = accuracy_score(test_labels, test_predictions)
    precision = precision_score(test_labels, test_predictions, average='weighted')
    recall = recall_score(test_labels, test_predictions, average='weighted')
    f1 = f1_score(test_labels, test_predictions, average='weighted')
    report = classification_report(test_labels, test_predictions)

    # Store the results
    results.append({
        'Classifier': clf_name,
        'Best Score': best_score,
        'Best Parameters': best_params,
        'Accuracy': accuracy,
        'Precision': precision,
        'Recall': recall,
        'F1 Score': f1,
    })

    # Print the evaluation metrics
    print(f"Results for {clf_name}:")
    print(f'Accuracy: {accuracy}')
    print(f'Precision: {precision}')
    print(f'Recall: {recall}')
    print(f'F1 Score: {f1}')
    print(f'Classification Report:\n{report}\n')

    # Plot the confusion matrix
    # unique_classes = test_labels.unique()  # type: ignore # Get unique class labels from the test set
    # confusion_matrix_filename = os.path.join("/home/users/elicina/Master-Thesis/Diagrams/ML-Results/W2V",f"{clf_name}.png")
    # plot_confusion_matrix(test_labels, test_predictions, unique_classes, confusion_matrix_filename)


    
# Create a DataFrame for the results
# results_df = pd.DataFrame(results)

# Save the results to a CSV file
# results_df.to_csv("/home/users/elicina/Master-Thesis/Diagrams/ML-Results/W2V/W2VResults1.csv", index=False)

# Display the results
# print(results_df)














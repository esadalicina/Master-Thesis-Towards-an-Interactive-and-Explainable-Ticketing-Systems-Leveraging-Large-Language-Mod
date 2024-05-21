from imblearn.over_sampling import SMOTE
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.io as pio
from matplotlib import pyplot as plt
from sklearn.svm import SVC
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.naive_bayes import MultinomialNB
import seaborn as sns
from xgboost import XGBClassifier
from sklearn.model_selection import StratifiedKFold, GridSearchCV, train_test_split
from sklearn.metrics import roc_auc_score, accuracy_score, precision_score, recall_score, f1_score, \
    classification_report
from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay

# Specify the file path of your CSV file
file_path = "../../Dataset/Cleaned_Dataset.csv"
# Read the CSV file into a DataFrame
df_clean = pd.read_csv(file_path)

# Keep the columns "complaint_what_happened" & "category_encoded" only in the new dataframe --> training_data
training_data = df_clean[['complaint_what_happened', 'category_encoded']]

# Display the first few rows of the DataFrame
print(training_data.head())

unique_categories = df_clean['category'].unique()

count_vect = CountVectorizer()

# Write your code to get the Vector count
X_train_counts = count_vect.fit_transform(training_data['complaint_what_happened'])

# Write your code here to transform the word vector to tf-idf
tfidf_transformer = TfidfTransformer()
X_train_tf = tfidf_transformer.fit_transform(X_train_counts)

# Checking for class imbalance
# px.bar(x=training_data['category_encoded'].value_counts().index, y=training_data['category_encoded'].value_counts().values/max(training_data['category_encoded'].value_counts().values), title='Class Imbalance')

print(X_train_tf)

# Assuming 'training_data' is your DataFrame and 'category_encoded' is your target column
category_counts = training_data['category_encoded'].value_counts()
normalized_counts = category_counts.values / max(category_counts.values)

fig = px.bar(
    x=category_counts.index,
    y=normalized_counts,
    title='Class Imbalance',
    labels={'x': 'Category', 'y': 'Normalized Count'}
)

# Show the plot
fig.show()

# Handle class imbalance using SMOTE
smote = SMOTE(random_state=42)
X_res, y_res = smote.fit_resample(X_train_tf, training_data['category_encoded'])

# Prepare the training and test data
train_X, test_X, train_y, test_y = train_test_split(X_res, y_res, test_size=0.2, random_state=40)


# Function to evaluate the model and display the results
def eval_model(y_test, y_pred, y_pred_proba, type='Training'):
    print(type, 'results')
    print('Accuracy: ', accuracy_score(y_test, y_pred).round(2))
    print('Precision: ', precision_score(y_test, y_pred, average='weighted').round(2))
    print('Recall: ', recall_score(y_test, y_pred, average='weighted').round(2))
    print('F1 Score: ', f1_score(y_test, y_pred, average='weighted').round(2))
    print('ROC AUC Score: ', roc_auc_score(y_test, y_pred_proba, average='weighted', multi_class='ovr').round(2))
    print('Classification Report: ', classification_report(y_test, y_pred))
    cm = confusion_matrix(y_test, y_pred)
    disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=training_data['category_encoded'].unique())
    disp.plot()


# Function to grid search the best parameters for the model
def run_model(model, param_grid):
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=40)
    grid = GridSearchCV(model, param_grid={}, cv=cv, scoring='f1_weighted', verbose=1, n_jobs=-1)
    grid.fit(train_X, train_y)
    return grid.best_estimator_


# print("------------------------------------------# 1. Logistic Regression #-------------------------------------------")
# params = {
#     'C': [0.001, 0.01, 0.1, 1, 10, 100],
#     'penalty': ['l1', 'l2', 'elasticnet', 'None'],
#     'solver': ['newton-cg', 'lbfgs', 'liblinear', 'sag', 'saga'],
#     'max_iter': [100, 200, 300, 500, 1000],
#     'class_weight': [None, 'balanced']
# }
#
# model1 = run_model(LogisticRegression(), params)
# eval_model(train_y, model1.predict(train_X), model1.predict_proba(train_X), type='Training')
# eval_model(test_y, model1.predict(test_X), model1.predict_proba(test_X), type='Test')



# print("-----------------------------------------------# 2. Decision Tree #--------------------------------------------")
# params = {
#     'criterion': ['gini', 'entropy'],
#     'splitter': ['best', 'random'],
#     'max_depth': [None, 2, 4, 6, 8, 10],
#     'min_samples_split': [2, 4, 6, 8, 10],
#     'min_samples_leaf': [1, 2, 4, 6, 8, 10],
#     'max_features': [None, 'auto', 'sqrt', 'log2']
# }
# model2 = run_model(DecisionTreeClassifier(), params)
# eval_model(train_y, model2.predict(train_X), model2.predict_proba(train_X), type='Training')
# eval_model(test_y, model2.predict(test_X), model2.predict_proba(test_X), type='Test')
#
#
# print("---------------------------------------------# 3. Random Forest #--------------------------------------------")
# params = {
#     'n_estimators': [10, 50, 100, 200, 500],
#     'criterion': ['gini', 'entropy'],
#     'max_depth': [None, 2, 4, 6, 8, 10],
#     'min_samples_split': [2, 4, 6, 8, 10],
#     'min_samples_leaf': [1, 2, 4, 6, 8, 10],
#     'max_features': [None, 'auto', 'sqrt', 'log2'],
#     'bootstrap': [True, False]
# }
# model3 = run_model(RandomForestClassifier(), params)
# eval_model(train_y, model3.predict(train_X), model3.predict_proba(train_X), type='Training')
# eval_model(test_y, model3.predict(test_X), model3.predict_proba(test_X), type='Test')
#
#
# print("-----------------------------------------------# 4. Naive Bayes #----------------------------------------------")
# params = {
#     'alpha': [0.1, 0.5, 1, 2, 5],
#     'fit_prior': [True, False]
# }
# model4 = run_model(MultinomialNB(), params)
# eval_model(train_y, model4.predict(train_X), np.exp(model4.predict_log_proba(train_X)), type='Training')
# eval_model(test_y, model4.predict(test_X), np.exp(model4.predict_log_proba(test_X)), type='Test')
#
#
# print("-------------------------------------------------# 5. XGBoost #------------------------------------------------")
# params = {
#     'n_estimators': [100, 200, 500],
#     'max_depth': [3, 5, 7],
#     'learning_rate': [0.01, 0.05, 0.1],
#     'gamma': [0, 0.5, 1],
#     'min_child_weight': [1, 3, 5],
#     'subsample': [0.5, 0.8, 1],
#     'colsample_bytree': [0.5, 0.8, 1]
# }
# model5 = run_model(XGBClassifier(use_label_encoder=False), params)
# eval_model(train_y, model5.predict(train_X), model5.predict_proba(train_X), type='Training')
# eval_model(test_y, model5.predict(test_X), model5.predict_proba(test_X), type='Test')
#
#
# print("----------------------------------------------------# 6. SVM #-------------------------------------------------")
# params = {
#     'C': [0.1, 1, 10, 100],
#     'kernel': ['linear', 'poly', 'rbf', 'sigmoid'],
#     'degree': [2, 3, 4],
#     'gamma': ['scale', 'auto'],
#     'class_weight': [None, 'balanced']
# }
# model6 = run_model(SVC(probability=True), params)
# eval_model(train_y, model6.predict(train_X), model6.predict_proba(train_X), type='Training')
# eval_model(test_y, model6.predict(test_X), model6.predict_proba(test_X), type='Test')
#
#
# print("-------------------------------------------------# Conclusion #------------------------------------------------")
#
# # Applying the best model on the Custom Text
# # We will use the XGBoost model as it has the best performance
# df_complaints = pd.DataFrame({'complaints': [
#     "I can not get from chase who services my mortgage, who owns it and who has original loan docs",
#     "The bill amount of my credit card was debited twice. Please look into the matter and resolve at the earliest.",
#     "I want to open a salary account at your downtown branch. Please provide me the procedure.",
#     "Yesterday, I received a fraudulent email regarding renewal of my services.",
#     "What is the procedure to know my CIBIL score?",
#     "I need to know the number of bank branches and their locations in the city of Dubai"
# ]})
#
#
# def predict_lr(text):
#     Topic_names = {0: 'Credit Reporting and Debt Collection', 1: 'Credit Cards and Prepaid Cards',
#                    2: 'Bank Account or Service', 3: 'Loans', 4: 'Money Transfers and Financial Services'}
#     X_new_counts = count_vect.transform(text)
#     X_new_tfidf = tfidf_transformer.transform(X_new_counts)
#     predicted = model5.predict(X_new_tfidf)
#     return Topic_names[predicted[0]]
#
#
# df_complaints['tag'] = df_complaints['complaints'].apply(lambda x: predict_lr([x]))
# print(df_complaints)


# ---------------------------------------------------- Save Model ------------------------------------------------------

# # Save the model
# joblib.dump(model, '/Users/esada/Documents/UNI.lu/MICS/Master-Thesis/Model/xgb_model.pkl')
#
# # Saving the objects
# joblib.dump(count_vect, '/Users/esada/Documents/UNI.lu/MICS/Master-Thesis/Model/count_vect.pkl')
# joblib.dump(tfidf_transformer, '/Users/esada/Documents/UNI.lu/MICS/Master-Thesis/Model/tfidf_transformer.pkl')

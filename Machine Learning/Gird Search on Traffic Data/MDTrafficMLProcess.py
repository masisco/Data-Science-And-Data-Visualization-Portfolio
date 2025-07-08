# Author: Mari Sisco
# PA2
# Purpose: Generate a machine learning process for the severity (3 classes) of accidents that affect traffic in
#          Maryland.


# Imports needed for ML process
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.decomposition import PCA
from sklearn.model_selection import GridSearchCV
from sklearn.linear_model import LogisticRegression, Perceptron
from sklearn.svm import SVC
from sklearn.metrics import classification_report, confusion_matrix, ConfusionMatrixDisplay

# Reading in pre-processed data
train_df = pd.read_csv("mdtraffic_train.csv", skipinitialspace=True)
test_df = pd.read_csv("mdtraffic_test.csv", skipinitialspace=True)

# Separate features and target
X_train = train_df.drop("Severity", axis=1)
y_train = train_df["Severity"]

X_test = test_df.drop("Severity", axis=1)
y_test = test_df["Severity"]

# Confirm shapes
print("X_train shape:", X_train.shape)
print("y_train shape:", y_train.shape)
print("X_test shape:", X_test.shape)
print("y_test shape:", y_test.shape)

# --- Pipeline 1: Logistic Regression ---
pipe_lr = Pipeline(steps=[
    ('scaler', StandardScaler()),
    ('pca', PCA()),
    ('lr', LogisticRegression(max_iter=1000))
])

param_range = [0.1, 1, 10, 50, 100]

# Parameter grid for Logistic Regression pipeline
param_grid_lr = {
    'pca__n_components': [0.9,0.95],
    'lr__C': param_range
}


# --- Grid Search Setup ---
# Grid search for Logistic Regression
grid_lr = GridSearchCV(
    estimator=pipe_lr,
    param_grid=param_grid_lr,
    scoring='f1_macro',  # Using F1-macro as the scoring metric
    cv=10,               # 10-fold cross validation
    verbose=2,
    n_jobs=-1
)

# Fitting on training data
grid_lr.fit(X_train, y_train)


# Printing score and best parameters
print("Logistic Regression best score (training):", grid_lr.best_score_)
print("Logistic Regression best parameters:", grid_lr.best_params_)


# --- Pipeline 2: SVC with RBF Kernel ---
pipe_svc = Pipeline(steps=[
    ('scaler', StandardScaler()),
    ('pca', PCA()),
    ('svc', SVC())
])

c_range = [0.001, 0.1, 1, 10, 100]
gamma_range = [10**-4, 10**-5, 10**-6]
degree_range = [2, 3, 4]


# Parameter grid for SVC with RBF
param_grid_svc = {
    'pca__n_components': [0.9,0.95],
    'svc__C': c_range,
    'svc__gamma': gamma_range,
    'svc__kernel': ["poly", "rbf"]
}

# Grid search for SVC kernel
grid_svc = GridSearchCV(
    estimator=pipe_svc,
    param_grid=param_grid_svc,
    scoring='f1_macro',  # Using macro f1 to evaluate performance
    cv=10,
    verbose=2,
    n_jobs=6
)

# Fitting on training data
grid_svc.fit(X_train, y_train)

print("SVC best score (training):", grid_svc.best_score_)
print("SVC best parameters:", grid_svc.best_params_)


# --- Selecting the Best Model ---
if grid_lr.best_score_ >= grid_svc.best_score_:
    best_model = grid_lr.best_estimator_
    best_model_name = "Logistic Regression"
else:
    best_model = grid_svc.best_estimator_
    best_model_name = "SVM"

print("\nSelected Best Model:", best_model_name)

# --- Evaluating on Test Data ---
predictions = best_model.predict(X_test)
cm = confusion_matrix(y_test, predictions)
print("\nConfusion Matrix:\n", cm)
ConfusionMatrixDisplay(cm).plot()
print("\nClassification Report:\n", classification_report(y_test, predictions))


# Displaying final results and analysis from the information above.

# Underlining in printing of statement
underline = "\033[4m"
reset = "\033[0m"

print(f"{underline}Analyzing the Results Obtained:{reset}"
      f"\n The {underline}first{reset} model was Logistic Regression \n\t The best parameters were a C value of 1 and a "
      f"PCA component retention of 0.95."
      f"\n The {underline}second{reset} model was SVM, tested with both polynomial and RBF kernels. \n\t The best "
      f"parameters were: 'pca__n_components': 0.95, 'svc__C': 100, 'svc__gamma': 0.0001, and 'svc__kernel': 'rbf'."
      f"\n  + After conducting grid search on both models, the best-performing model was the SVM. While Logistic Regression "
      f"achieved a training F1-score of around 0.43, the SVM demonstrated better generalization and performance on the "
      f"test set, particularly with Class 1 and Class 2."
      f"\n  + From the classification report, the SVM achieved a strong F1-score of 0.74 for Class 1, which represents the "
      f"least severe accidents. It also had a moderate F1-score of 0.56 for Class 2, showing it could reasonably detect more "
      f"impactful accidents."
      f"\n  + However, the model entirely failed to predict any instances of Class 3 (most severe accidents), resulting "
      f"in an F1-score of 0.00 for that class. This issue is also reflected in the confusion matrix, where Class 3 rows"
      f" show zero correct predictions and heavy misclassification as Class 1 and 2."
      f"\n  + Overall, while SVM outperformed Logistic Regression in both accuracy (0.65) and weighted F1-score (0.61), "
      f"it still struggles with the minority class. This suggests the need for further class balancing strategies or "
      f"sampling techniques to improve detection of the most severe accidents."
)

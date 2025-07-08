# Mari Sisco
# PA 3
# May 5th 2025

# Purpose: Prepare data and perform GridSearchCV for Random Forest using two scoring metrics.

import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.metrics import classification_report

# Load data
df = pd.read_csv("diabetes_binary.csv")

# Check if all columns are numeric (no encoding needed)
print("Checking if columns are already numeric: ")
print(df.dtypes)

# Examine class distribution to confirm imbalance
imbalance_counts = df["Diabetes_binary"].value_counts()
print("Checking imbalance of data:")
print(imbalance_counts)

# Print class distribution as percentages
print(f"Percentage of class 0: {imbalance_counts[0] / (imbalance_counts[0] + imbalance_counts[1]) * 100:.2f}%")
print(f"Percentage of class 1: {imbalance_counts[1] / (imbalance_counts[0] + imbalance_counts[1]) * 100 :.2f}%")

# Drop ID column - it does not contribute to prediction
df.drop(columns=["ID"], inplace=True)

# Separate features from target label
data = df.drop(columns=["Diabetes_binary"])
target = df["Diabetes_binary"]

# Split the data into training and test sets with stratified sampling
X_train, X_test, y_train, y_test = train_test_split(
    data, target, stratify=target, test_size=0.25, random_state=42
)

# Define the grid of hyperparameters to search over
# Includes key parameters for random forest and class_weight handling
parameter_grid = {
    "n_estimators": (50, 100, 150, 200),
    "max_features": ("sqrt", "log2"),
    "oob_score": [False, True],
    "class_weight": (None, "balanced", "balanced_subsample"),
    "max_depth": (5, 10, 15, 20, 25),
}

# Function to run grid search for the specified scoring metric (e.g., accuracy or f1)
def grid_search(scoring_metric):

    # Initialize base random forest model
    random_forest = RandomForestClassifier(bootstrap=True, random_state=42)

    # Set up grid search with cross-validation
    grid_RF = GridSearchCV(
        estimator=random_forest,
        param_grid=parameter_grid,
        scoring=scoring_metric,
        cv=5,
        n_jobs=-1,
        return_train_score=True,
        verbose=2
    )

    # Fit the grid search model to the training data
    grid_RF.fit(X_train, y_train)

    # Convert results to DataFrame for export and analysis
    results_df = pd.DataFrame(grid_RF.cv_results_)

    # Convert class_weight column to string to avoid issues when analyzing results
    results_df["param_class_weight"] = results_df["param_class_weight"].astype(str)

    # Evaluate model on training data
    print("\nTraining classification report:")
    y_train_pred = grid_RF.predict(X_train)
    print(classification_report(y_train, y_train_pred))

    # Evaluate model on test data
    print("\nTesting classification report:")
    y_test_pred = grid_RF.predict(X_test)
    print(classification_report(y_test, y_test_pred))

    return results_df

# Run GridSearchCV using accuracy as the scoring metric
print("\nRunning Grid Search for accuracy metric: ")
accuracy_rf_results = grid_search("accuracy")
accuracy_rf_results.to_csv("accuracy_results1.csv", index=False)

# Run GridSearchCV using F1 score as the scoring metric
print("\nRunning Grid Search for f1 metric: ")
f1_rf_results = grid_search("f1")
f1_rf_results.to_csv("f1_results1.csv", index=False)

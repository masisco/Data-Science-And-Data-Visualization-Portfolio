# Random Forest Hyperparameter Exploration – Diabetes Prediction

**Author:** Maria Andreina Sisco  
**Course:** CS484 – Machine Learning at Loyola University Maryland  
**Date Completed:** April 14, 2025

---

## Project Overview

This project implements a full machine learning workflow using a **Random Forest Classifier** to predict whether individuals have diabetes based on health-related survey data. The primary focus of the project is to explore how different **hyperparameters** affect model performance using two separate `GridSearchCV` experiments — one evaluated by **accuracy**, and the other by **F1-score** — on a highly imbalanced dataset.

---

## Key Features

- **Data Preparation**: Checked feature types, dropped irrelevant features, and split data using stratified sampling.
- **Dual Grid Search**: Ran extensive hyperparameter tuning twice using:
    - Accuracy as the scoring metric
    - F1-score as the scoring metric
- **Evaluated Parameters**:
    - `n_estimators`
    - `max_features`
    - `oob_score`
    - `max_depth`
    - `class_weight`
- **Result Exporting**: Saved both grid search results as CSV files for later analysis.
- **Comprehensive Evaluation**: Printed classification reports for both training and test sets for each run.

---

## File Structure

- `randomforest.py` — Main Python script for data prep, training, and exporting grid search results
- `RFAnalysisPA3MariSisco.ipynb` — Jupyter notebook for exploring the results and interpreting the impact of hyperparameters
- `accuracy_results1.csv` — Grid search results using accuracy
- `f1_results1.csv` — Grid search results using F1 score
- `interpretation.md` — Final reflections and answers on model behavior and hyperparameter influence

---

## How to Run

1. Ensure **Python 3.x** is installed.
2. Clone this repository locally.
3. Run the main pipeline script:

```bash
python randomforest.py
```

4. Open the Jupyter notebook to view and interpret the results:

```bash
jupyter notebook RFAnalysisPA3MariSisco.ipynb
```

---

## Technologies Used

- Pandas
- NumPy
- scikit-learn
- Jupyter Notebook
- matplotlib & seaborn (for analysis and visualization)

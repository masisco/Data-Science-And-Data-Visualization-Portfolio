# Maryland Traffic Accident Severity Classifier

**Author:** Maria Andreina Sisco  
**Course:** CS484 – Machine Learning at Loyola University Maryland  
**Date Completed:** March 14, 2025

---

## Project Overview

This project develops a machine learning pipeline to classify the **severity of traffic accidents** in Maryland into three categories using real-world accident data. The work involves comprehensive **data preprocessing** in a Jupyter notebook and the design of multiple **classification pipelines** using `GridSearchCV`, culminating in the selection of the best-performing model based on validation performance.

---

## Key Features

- **Data Cleaning & Preprocessing**: Exploratory analysis and preprocessing performed in a Jupyter notebook, including handling missing values, irrelevant features, and class imbalances.
- **Train-Test Pipeline**: Data split into training and test sets using `train_test_split`.
- **Grid Search & Model Evaluation**: Two separate pipelines were built:
   - Logistic Regression with PCA
   - Support Vector Machine with RBF/Polynomial kernel and PCA
- **Automated Model Selection**: The better model is automatically selected based on cross-validated F1-macro scores.
- **Evaluation Metrics**:
   - Confusion matrix
   - Classification report (precision, recall, F1-score)
- **Insightful Output**: Final test performance and detailed observations printed to console.

---

## File Structure

- `PA2DataPreProcessing.ipynb` — Jupyter notebook for cleaning and preparing the Maryland accident dataset
- `MDTrafficMLProcess.py` — Python script for training, model selection, and evaluation
- `mdtraffic_train.csv` — Preprocessed training data (generated from notebook)
- `mdtraffic_test.csv` — Preprocessed testing data (generated from notebook)
- `interpretation.md` — Final answers and insights based on model performance
- `datainfo.md` — Information about the original dataset (mdtraffic.csv)

---

## How to Run

1. Ensure **Python 3.x** is installed.
2. Clone this repository locally.
3. Run the preprocessing notebook first (if data is not yet split):

```bash
jupyter notebook PA2DataPreProcessing.ipynb
```

4. Then run the main pipeline script:

```bash
python MDTrafficMLProcess.py
```

The script will:
- Load the preprocessed data
- Run `GridSearchCV` on both models with cross-validation
- Evaluate both models and select the best one
- Output classification results and analysis

---

## Technologies Used

- Python (3.x)
- Pandas
- NumPy
- scikit-learn
- matplotlib
- Jupyter Notebook
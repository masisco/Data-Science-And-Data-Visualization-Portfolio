# Multiclass Perceptron Classifier – Wine Dataset

**Author:** Maria Andreina Sisco  
**Course:** CS484 – Machine Learning at Loyola University Maryland 
**Date Completed:** February 3, 2025

---

## Project Overview

This project implements a **multiclass Perceptron classifier** using the **One-vs-Rest (OvR)** strategy on a wine dataset that includes chemical analysis data of wines derived from three different cultivars. The primary objective was to extend a standard binary Perceptron model into a multiclass classification system while following best practices in software development, experimentation, and reproducibility.

---

## Key Features

- **One-vs-Rest Strategy**: Trained three separate Perceptron models, each distinguishing one class from the rest.
- **Performance Visualization**: Tracked and graphed training error per epoch for each binary classifier.
-  **Evaluation**: Automatically selected the best-performing model based on validation accuracy, and reported:
    - Final **confusion matrix**
    - **Classification report** (precision, recall, F1-score)
-  **Data Preprocessing**: Removed features with extreme scale variance to ensure model stability.
-  **Modular Code Design**: Structured with reusable functions, clear documentation, and a dedicated `Perceptron.py` class file.
-  **Interpretation**: Reflections and answers provided in `interpretation.md`.

---

##  File Structure

- main.py ---- Main script for data processing, training, and evaluation

- perceptron.py --- Binary Perceptron class adapted from course textbook

- interpretation.md  --- Written answers interpreting results and learnings

- wine.data --- Provided dataset (13 features, 3 classes)

---

##  How to Run

1. Ensure **Python 3.x** is installed.
2. Clone this repo locally.
3. Open terminal or command prompt and run:

```bash
python main.py
```

---

## Technologies Used
- Python (3.x)
- Pandas
- NumPy
- scikit-learn
- matplotlib

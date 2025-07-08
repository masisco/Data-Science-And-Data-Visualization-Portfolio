# Mari Sisco
# PA 1
# Purpose of Main - Classifying a wine dataset using a multiclass perceptron model with the One vs rest approach

# Importing all packages and functions that will be used throughout the program
from Perceptron import Perceptron
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import confusion_matrix,ConfusionMatrixDisplay, classification_report


# Reading in the wine dataset as a pandas dataframe
dfWine = pd.read_csv('wine.data', encoding='utf-8')
# Function allowing for the display of the dataframe to be full
pd.set_option('display.max_columns', None)

# Optional functions to obtain summary of dataframe
#print(dfWine.head())
#print(dfWine.tail())
#print(dfWine.describe())
#print(dfWine.info())

# source: https://www.statology.org/pandas-create-dataframe-from-existing-dataframe/
# Creating X(features) and y(target)
# Two features, other than class are dropped: Magnesium and Proline (vastly different scale than the other ones)
X = dfWine.drop(['Class','Magnesium','Proline'], axis=1)
y = dfWine['Class']

# From this, it is observed that the class levels for wine are 1, 2 and 3.
print('Class labels:', np.unique(y))

# Splitting data: 80% train set and 20% test set
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=1, stratify=y)

# Standardizing Results
sc = StandardScaler()
sc.fit(X_train)
X_train_std = sc.transform(X_train)
X_test_std = sc.transform(X_test)

# One-vs-Rest Encoding (Creating three binary label sets)
# Creating new columns of the binary labels that will be passed to each Perceptron
y_train_binary_labels = pd.DataFrame()
y_test_binary_labels = pd.DataFrame()

# For each class (1, 2 or 3) in the dataset,
for cls in np.unique(y_train):
    # if the label = class, then the binary label is 1
    y_train_binary_labels[cls] = (y_train == cls).astype(int)

# Testing results of the binary levels
y_train_binary_labels['Og Label'] = y_train.values
print(y_train_binary_labels)


# Multiclass perceptron, One vs Rest
# ----------------------------------------------------------
# Training three Perceptron models, one for each class label

# Initializing an array of perceptrons
perceptrons = []

# obtaining the unique labels
unique_labels = np.unique(y)

# for each label
for label in unique_labels:
    # Obtain the series of labels of that class
    labels = y_train_binary_labels[label]
    ppn = Perceptron(eta = 0.1, n_iter = 50 )
    # Train the perceptron
    ppn.fit(X_train_std, labels)

    # Code obtained from HW4
    # Plotting number of updates per epoch
    plt.plot(range(1, len(ppn.errors_) + 1), ppn.errors_, marker='o')
    plt.title(f"One vs Rest: Class{label}")
    plt.xlabel('Epochs')
    plt.ylabel('Number of updates')

    # plt.savefig('images/02_07.png', dpi=300)
    plt.show()

    # output the final learned bias and weights of each model in the multi-class Perceptron

    print(f'Class{label} learned bias: {ppn.b_}')
    print(f'Class{label} learned weights: {ppn.w_}')

    # Appending Perceptron object to array
    perceptrons.append(ppn)


# PREDICT MULTICLASS FUNCTION
# Purpose: predict the class based on raw outputs
# Parameters: perceptron array, X data frame
# Return: predicted classes
def predict_multiclass(perceptrons, X):
    # getting raw outputs from each perceptron
    perceptron_outputs = []
    for ppn in perceptrons:
        # appending raw output of each perceptron
        perceptron_outputs.append(ppn.raw_output(X))
    # combining outputs into a np array
    # it must be transposed in order to have columns be classes and rows be each row sample
    raw_outputs = np.array(perceptron_outputs).T

    # Find the index of the perceptron with the highest output for each sample
    # Add 1 to match class labels (1, 2, 3)
    predicted_classes = np.argmax(raw_outputs, axis=1) + 1

    return predicted_classes

# Predict the classes for the test data
y_pred = predict_multiclass(perceptrons, X_test_std)

# Confusion matrix generated for test data
cm = confusion_matrix(y_test, y_pred)
print('Confusion Matrix:')
print(cm)

# Confusion matrix displayed
disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=np.unique(y))
disp.plot()
plt.title('Confusion Matrix Multiclass perceptron')
plt.show()

# Classification report generated for test data
class_report = classification_report(y_test, y_pred)
print('Classification Report Multiclass Perceptron:')
print(class_report)

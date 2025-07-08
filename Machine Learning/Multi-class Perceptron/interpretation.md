# Interpretations

## Setup

What hyperparameters were used on the perceptron?

I used (eta) = 0.1 as the learning rate and n_iter = 50 for the number of epochs. A moderate learning rate was used as it ensures steady learning, while 50 epochs allow sufficient updates without overfitting.

What features were used in training?

I used all features except Magnesium and Proline. These two were dropped because they had vastly different scales compared to other features, which could have negatively impacted training even after standardization.

## Errors

How many errors occured on each epoch for each learned model? Did the models differ? 

- Class 1 and Class 3 learned quickly, with the number of updates stopping around 15 epochs.

- Class 2 was more difficult to classify, as its number of updates never reached zero. Instead, the updates fluctuated up and down toward the end, indicating that the decision boundary was harder to establish.


## Test data results

### What were the test data results? 

The multi-class perceptron performed well, achieving 97% accuracy on the test set. Some classes were easier to predict than others as such:

- Class 1 had near-perfect precision and recall.

- Class 2 had slightly lower recall (0.93), meaning it misclassified one instance.

- Class 3 was perfectly classified.

I experimented with different hyperparameters, such as higher eta and lower n_iter, but the current values provided the best balance that could be used for other datasets! 


# Interpretations 

## About the Process

### Why did I choose these machine learning algorithms?
I chose Logistic Regression and SVC with an RBF kernel because they represent different approaches to classification. Logistic Regression works well for linearly separable data, and even though our data was not all necessarily linearly seperable, it does not prevent one from using it. Meanwhile SVC is capable of capturing more complex, non-linear relationships. Given that real-world traffic accident data may have both linear and non-linear patterns, testing both models allowed me to compare their effectiveness and choose the best one.

### Why were the hyperparameters chosen?

For Logistic Regression, I tuned the C parameter, which controls regularization, to prevent overfitting while maintaining model flexibility. I used [0.1, 1, 10, 50, 100], a good range of values to choose the best regularization. The PCA component (0.90 and 0.95 variance) was chosen to reduce dimensionality while preserving most of the variance in the data.

For SVC, I selected a grid of values for C (regularization parameter of [0.001, 0.1, 1, 10, 100]) and gamma (which controls the influence of each training example: [10**-4, 10**-5, 10**-6]) to explore different levels of complexity, using both polynomial and RBF kernels. The RBF kernel was prioritized due to its flexibility with non-linear patterns. PCA was again applied with the same variance thresholds.


## About Results

### How well did each grid search perform?

The Logistic Regression model achieved a best cross-validated training score of approximately 0.4341 with C=1 and pca__n_components=0.95. The SVC model, using the RBF kernel, outperformed it with a higher test set F1-score and better classification performance overall. Its best parameters were: C=100, gamma=0.0001, pca__n_components=0.95, and svc__kernel=rbf'.

On the test set, SVC reached a weighted average F1-score of 0.61 and an accuracy of 65%, compared to lower performance from Logistic Regression. This suggests that the non-linear capacity of the SVM model was better suited to capture relationships in the data, at least for the majority classes.

I was surprised by how poorly the SVC model performed for detecting class 3. Given that SVC with an RBF kernel is known for handling non-linear relationships, I expected it to at get some value above 0.3. But, both models completely failed to identify Class 3, the most severe accidents. In the confusion matrix, Class 3 predictions are entirely misclassified as Class 1 or 2, with an F1-score of 0.00. This failure likely stems from the class imbalance in the dataset, where Class 3 had far fewer examples.
## Interpretations after Training

### How well did each grid search appear to work based on the *training* data's classification report?

Accuracy-based model:

Achieved 90% overall accuracy on the training set. However, this masks a serious issue: class 0 (majority) had 99% recall and 0.94 F1, while class 1 (minority) only reached 30% recall and 0.45 F1. This means the model mostly memorized class 0 but struggled to identify individuals with diabetes (class 1).

F1-based model:
Achieved 83% accuracy, but more importantly, class 1 recall jumped to 85%, with a better F1 score of 0.58. Class 0 performance dropped a bit (F1: 0.89), but the model overall treated both classes more fairly.

Conclusion: The F1 grid search worked better for the imbalanced goal: identifying people with diabetes, even if it meant slightly lower accuracy.

### How does the interpretation change after seeing the test data's classification report? 

When I looked at the test classification reports, my interpretation definitely shifted. At first, I thought the accuracy-based model was performing really well, it had 86% accuracy, which seemed promising. But then I saw that its recall for class 1 (the diabetic cases) was only 13%, with an F1 score of just 0.21. It made me realize that even though the model looked good on paper, it was almost completely ignoring the minority class.

On the other hand, the F1-based model had a lower accuracy of 78%, which initially felt like a step backward. But then I saw the recall for class 1 jumped to 65%, and its F1 score was 0.45. That’s a huge difference, and it told me this model was actually doing what I needed: identifying people with diabetes.

This result honestly confirmed what I expectedin the test data. The dataset is heavily imbalanced, with far more non-diabetic cases (class 0), and accuracy favors that majority class. But optimizing for F1 forced the model to focus more on the harder-to-detect class. That shift in metric, and the use of class weighting—clearly helped the model generalize better without overfitting to the dominant class. It really showed me how important metric selection is, especially in real-world applications like this where the minority class actually matters more.

## Interpretation after Analysis

### Did the effect of hyperparameter values match between metrics, or differ? 

The impact of hyperparameter values clearly differed depending on the evaluation metric. When optimizing for accuracy, the class_weight=None setting consistently produced the highest scores. However, when shifting to F1 optimization—more appropriate for our imbalanced diabetes dataset—the use of class_weight='balanced' or 'balanced_subsample' significantly improved performance, particularly for the minority class (class 1). Other parameters like max_depth, n_estimators, and max_features influenced both metrics in a similar direction, typically improving performance to a point before plateauing. Still, the class_weight hyperparameter had the most metric-specific effect, emphasizing the importance of aligning the tuning strategy with the evaluation goal.


Some of the trends observed in the analysis graphs were expected, while others were more revealing. As anticipated, enabling class_weight='balanced' or 'balanced_subsample' improved F1 scores significantly, and increasing the number of estimators generally improved performance until it leveled off around 150–200 trees. What was more surprising was that even at the deepest tree depth tested (max_depth=25), the model with class_weight=None failed to close the F1 performance gap. This demonstrated that increasing model complexity alone does not compensate for poor handling of class imbalance.


### Did either or both searches result in models with overfitting?

The accuracy model showed clear signs of overfitting. While its F1 score for class 1 was 0.45 on the training set, it dropped dramatically to just 0.21 on the test set—evidence that it had learned patterns that did not generalize beyond the training data. In contrast, the F1-optimized model demonstrated much less overfitting. Its class 1 F1 score declined more modestly, from 0.58 in training to 0.45 in testing, indicating better generalization. This comparison illustrates how optimizing for the right metric, one that aligns with the dataset's imbalance—can also lead to more robust model behavior.


### Did the best model perform as well on the test data?

Yes, the best model performed in line with expectations. The F1 model achieved a class 1 recall of 0.65 and an F1 score of 0.45 on the test set, strong outcomes given the class imbalance. These metrics indicate that the model was not only identifying a much higher proportion of true diabetic cases, but doing so with precision. In contrast, the accuracy model, which initially appeared strong due to its high overall accuracy, failed dramatically in detecting positive cases when evaluated on test data. This contrast reinforced the importance of evaluating models on metrics aligned with the real-world objective.

### This data was imbalanced.

The dataset was highly imbalanced, with far more non-diabetic cases than diabetic ones. To address this, we included class_weight as a tunable hyperparameter, testing 'None', 'balanced', and 'balanced_subsample' to reweight the training data in favor of the minority class. Additionally, we conducted a separate grid search using F1 score as the evaluation metric to focus on improving performance for class 1. This approach was effective: the final model—using class_weight='balanced_subsample' and max_depth=15—achieved a substantial boost in both recall and F1 score for class 1, making it better suited for identifying positive diabetes cases in a real-world setting.


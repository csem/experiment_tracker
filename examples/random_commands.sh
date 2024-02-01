python3 examples/training_experiment.py -m seed=1,2,3,43 dataset=digits,iris normalize=True,False
python3 examples/training_experiment.py -m estimator=svm dataset=digits
python3 examples/training_experiment.py -m estimator=svm dataset=digits normalize=False
python3 examples/training_experiment.py -m estimator=svm,knn dataset=iris normalize=True,False
python3 examples/training_experiment.py trigger_error=True dataset=digits